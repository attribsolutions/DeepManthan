from rest_framework.views import APIView
from rest_framework import status
from datetime import datetime
from django.db import transaction
from ftplib import FTP
from datetime import datetime
from django.http import JsonResponse
from SweetPOS.models import *
from ..models import *
import io
from rest_framework.permissions import IsAuthenticated
from urllib.parse import urlparse
from rest_framework.parsers import JSONParser


class SAPExportViewDetails(APIView):
    permission_classes = (IsAuthenticated,)
    @transaction.atomic
    def post(self, request):
        SalesData = JSONParser().parse(request)        
        try:
            Party = SalesData['Party'] 
            InvoiceDate = SalesData['InvoiceDate'] 
            # Call the orchestrator method
            self.File1(Party,InvoiceDate)
            self.File3(Party,InvoiceDate)            
            self.File2(Party,InvoiceDate) 
            return JsonResponse({'message': 'Files are uploaded successfully'}, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)   
    
    def File1(self, Party,InvoiceDate):
        try:
            # Fetch FTP credentials from M_Settings
            settings_map = self.get_ftp_settings()
            user_name = settings_map.get(50)  # Username
            password = settings_map.get(51)  # Password
            FTPFilePath = settings_map.get(52)  # FTPFilePath           

            # Raw SQL Query
            upload_invoices_query = f'''
                SELECT 1 id,
                M_Items.SAPItemCode AS Material, 
                M_Parties.SapPartyCode AS Store, 
                C.TotalRevenue, 
                SUM(SweetPOS.TC_SPOSInvoiceItems.Quantity) AS Quantity, 
                CASE WHEN MC_ItemUnits.UnitID_id = 2 THEN M_Units.Name ELSE 'EA' END AS UOM, 
                SweetPOS.TC_SPOSInvoiceItems.Rate,  
                SUM(SweetPOS.TC_SPOSInvoiceItems.CGST) AS CGST, 
                SUM(SweetPOS.TC_SPOSInvoiceItems.SGST) AS SGST, 
                DATE_FORMAT(SweetPOS.TC_SPOSInvoiceItems.InvoiceDate,'%%Y%%m%%d') AS SaleDate, 
                0 AS BasicValue, 
                0 AS DiscountValue ,M_Parties.Name
                FROM SweetPOS.TC_SPOSInvoiceItems 
                JOIN FoodERP.M_Items ON M_Items.id = SweetPOS.TC_SPOSInvoiceItems.Item 
                JOIN FoodERP.M_Parties ON M_Parties.id = SweetPOS.TC_SPOSInvoiceItems.Party 
                JOIN FoodERP.MC_ItemUnits ON MC_ItemUnits.id = SweetPOS.TC_SPOSInvoiceItems.Unit 
                JOIN FoodERP.M_Units ON M_Units.id = MC_ItemUnits.UnitID_id
                JOIN (
                SELECT SUM(BasicAmount) AS TotalRevenue, Party AS DivisionID, InvoiceDate 
                FROM SweetPOS.TC_SPOSInvoiceItems 
                WHERE InvoiceDate = %s
                AND Party IN (%s)  
                GROUP BY Party, InvoiceDate
                ) C ON SweetPOS.TC_SPOSInvoiceItems.Party = C.DivisionID 
                AND SweetPOS.TC_SPOSInvoiceItems.InvoiceDate = C.InvoiceDate
                WHERE SweetPOS.TC_SPOSInvoiceItems.InvoiceDate = %s  
                AND SweetPOS.TC_SPOSInvoiceItems.Party IN (%s)  
                AND M_Items.SAPItemCode != '' 
                GROUP BY 
                M_Items.SAPItemCode '''

            # Execute query           
            raw_queryset = T_SPOSInvoices.objects.raw(upload_invoices_query, [InvoiceDate,Party,InvoiceDate,Party])   
            # print(raw_queryset.query)         
            # Generate file name
            file_name = f"{datetime.now().strftime('%Y%m%d')}_{raw_queryset[0].Name.strip()}_File1.csv"
            ftp_file_path = f"{FTPFilePath}/inbound/POS/POS_day_sales/source/{file_name}"
            
            # Prepare CSV content
            headers = [
                "Material", "Store", "TotalRevenue", "Quantity", "UOM",
                "Rate", "CGST", "SGST", "SaleDate", "BasicValue", "DiscountValue"
            ]
            rows = [
                [
                    item.Material, item.Store, item.TotalRevenue,
                    item.Quantity, item.UOM, item.Rate, item.CGST,
                    item.SGST, item.SaleDate, item.BasicValue, item.DiscountValue
                ]
                for item in raw_queryset
            ]
            
            csv_content = self.generate_csv(headers, rows)
            

            # Upload to FTP
            self.upload_to_ftp(ftp_file_path, user_name, password, csv_content)            
            pass
            # Return success response
            # return JsonResponse({'message': 'File uploaded successfully', 'file_name': file_name})
            
        except Exception as exc:
            # Log and return the error
            self.insert_pos_log(1, "Failed", str(exc))
            return JsonResponse({'error': str(exc)}, status=500)
            raise
            
    def File3(self, Party,InvoiceDate):
        try:
            
            # Fetch FTP credentials from M_Settings
            settings_map = self.get_ftp_settings()
            user_name = settings_map.get(50)  # Username
            password = settings_map.get(51)  # Password
            FTPFilePath = settings_map.get(52)  # FTPFilePath           
           
            
            upload_invoices_query =f'''
                SELECT 1 id, DATE_FORMAT(InvoiceDate, '%%Y%%m%%d') SaleDate, FoodERP.M_Parties.SAPPartyCode Store,
                A.ClientID, InvoiceNumber BillNumber,M_Parties.Name 
                FROM T_SPOSInvoices A
                JOIN FoodERP.M_Parties ON A.Party = FoodERP.M_Parties.id
                WHERE InvoiceDate = %s AND A.Party =%s'''

            # Execute query with parameters        
            raw_queryset = T_SPOSInvoices.objects.raw(upload_invoices_query, [InvoiceDate,Party])
            
            # Generate file name
            file_name = f"{datetime.now().strftime('%Y%m%d')}_{raw_queryset[0].Name.strip()}_File3.csv"
            ftp_file_path = f"{FTPFilePath}/inbound/POS/POS_day_sales/source/{file_name}"            
            # Prepare CSV content
            headers = [
                "SaleDate", "Store", "ClientID","BillNumber"
            ]
            rows = [
                [
                    item.SaleDate,  item.Store,
                    item.ClientID, item.BillNumber
                ]
                for item in raw_queryset
            ]            
            csv_content = self.generate_csv(headers, rows)

            # Upload to FTP
            self.upload_to_ftp(ftp_file_path, user_name, password, csv_content)           
            pass
        except Exception as exc:
            # Log and raise error
            self.insert_pos_log(3, "Failed", str(exc))
            raise
        
    def File2(self, Party,InvoiceDate):
        try:
           
            # Fetch FTP credentials from M_Settings
            settings_map = self.get_ftp_settings()
            user_name = settings_map.get(50)  # Username
            password = settings_map.get(51)  # Password
            FTPFilePath = settings_map.get(52)  # FTPFilePath 
            DoNOtUseItemID= settings_map.get(53)  
            
            upload_invoices_query =f'''SELECT 1 id,DATE_FORMAT(InvoiceDate, '%%Y%%m%%d') AS SaleDate,SapItemCode AS Material,
            SUM(Quantity) AS Quantity,CASE WHEN M_Units.id = 2 THEN M_Units.Name ELSE 'EA' END AS UOM,M_Parties.SapPartyCode AS Store,
            M_Parties.Name
            FROM SweetPOS.TC_SPOSInvoiceItems JOIN FoodERP.M_Items ON M_Items.id = SweetPOS.TC_SPOSInvoiceItems.Item
            JOIN
            FoodERP.M_Parties ON M_Parties.id = SweetPOS.TC_SPOSInvoiceItems.Party
            JOIN
            FoodERP.MC_ItemUnits ON MC_ItemUnits.id = Unit
            JOIN
            FoodERP.M_Units ON M_Units.id = MC_ItemUnits.UnitID_id
            WHERE
            InvoiceDate = %s  AND  Party = %s  AND M_Items.SAPItemCode != '' AND SweetPOS.TC_SPOSInvoiceItems.Item NOT IN  (%s)
            GROUP BY
            SapItemCode,M_Units.Name,M_Parties.SapPartyCode,InvoiceDate,M_Parties.Name,M_Items.SAPItemCode,M_Units.id'''

            # Execute query with parameters            
            raw_queryset = T_SPOSInvoices.objects.raw(upload_invoices_query, [InvoiceDate,Party,DoNOtUseItemID])
            
            # Generate file name
            file_name = f"{datetime.now().strftime('%Y%m%d')}_{raw_queryset[0].Name.strip()}_File2.csv"
            ftp_file_path = f"{FTPFilePath}/inbound/POS/POS_day_sales/source/{file_name}"            
            # Prepare CSV content
            headers = [
                "SaleDate", "Material", "Quantity","UOM","Store"
            ]
            rows = [
                [
                    item.SaleDate,  item.Material,
                    item.Quantity, item.UOM,item.Store
                ]
                for item in raw_queryset
            ]
            
            csv_content = self.generate_csv(headers, rows)

            # Upload to FTP
            self.upload_to_ftp(ftp_file_path, user_name, password, csv_content)    
            pass
        except Exception as exc:
            # Log and raise error
            self.insert_pos_log(2, "Failed", str(exc))
            raise
        
    def generate_csv(self, headers, rows):
        """Generate CSV content as bytes."""
        output = io.StringIO()
        output.write(",".join(headers) + "\n")
        for row in rows:
            output.write(",".join(map(str, row)) + "\n")
        return output.getvalue().encode("utf-8")
   
    def upload_to_ftp(self, ftp_url, username, password, file_content):
        """Upload file content to an FTP server."""        
        try:
            parsed_url = urlparse(ftp_url)
            ftp_base_url = parsed_url.hostname  
            ftp_file_path = parsed_url.path.lstrip('/')  
            directories, file_name = ftp_file_path.rsplit('/', 1)  # Extract directory and file name
            
            # Connect to the FTP server
            ftp = FTP(ftp_base_url)  # Create an FTP object and connect
            ftp.login(username, password)  # Login with credentials

            # Navigate to the directory or create it
            try:
                ftp.cwd(directories)  # Try changing to the directory
            except Exception:
                for subdir in directories.split('/'):
                    try:
                        ftp.cwd(subdir)  # Change to subdirectory if it exists
                    except Exception:
                        ftp.mkd(subdir)  # Create subdirectory if it doesn't exist
                        ftp.cwd(subdir)  # Change to the newly created subdirectory

            # Upload the file
            with io.BytesIO(file_content) as file_stream:                        
                ftp.storbinary(f"STOR {file_name}", file_stream)  # Upload the file

            # Verify the upload
            uploaded_files = []
            ftp.retrlines('NLST', uploaded_files.append)
            if file_name not in uploaded_files:
                raise Exception(f"File {file_name} not found after upload.")
            # Close FTP connection
            ftp.quit()

        except Exception as e:
            print(f"FTP upload failed: {e}")
            raise

    def insert_pos_log(self, file_type, status, message):
        """Log operation details."""
        print(f"Log - FileType: {file_type}, Status: {status}, Message: {message}")  
        
    def get_ftp_settings(self):
        """Fetches FTP credentials."""
        Q11 = M_Settings.objects.filter(id__in=[50, 51, 52,53]).values("id", "DefaultValue")
        return {item['id']: item['DefaultValue'] for item in Q11}