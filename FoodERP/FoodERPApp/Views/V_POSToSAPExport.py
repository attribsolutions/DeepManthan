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
from django.utils import timezone
from ..Serializer.S_Invoices import *




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
            self.File2(Party,InvoiceDate)            
            ss= self.File3(Party,InvoiceDate) 
            return JsonResponse(ss)
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
                SELECT  1 id,	M_Items.SAPItemCode AS Material, 
                M_Parties.SapPartyCode AS Store, 
                 TR.TotalRevenue,
                SUM(II.Quantity) AS Quantity, 
                M_Units.SAPUnit UOM, 
                MRPValue Rate,  
                SUM(II.CGST) AS CGST, 
                SUM(II.SGST) AS SGST, 
                DATE_FORMAT(I.InvoiceDate, '%%Y%%m%%d') SaleDate, 
                SUM(II.BasicAmount) AS BasicValue, 
                SUM(II.DiscountAmount) AS DiscountValue
                FROM SweetPOS.TC_SPOSInvoiceItems II
                join SweetPOS.T_SPOSInvoices  I on I.id= II.Invoice_id
                JOIN FoodERP.M_Items ON M_Items.id = II.Item 
                JOIN FoodERP.M_Parties ON M_Parties.id = II.Party 
                JOIN FoodERP.MC_ItemUnits ON MC_ItemUnits.id = II.Unit 
                JOIN FoodERP.M_Units ON M_Units.id = MC_ItemUnits.UnitID_id
                
                JOIN (SELECT SUM(GrandTotal) AS TotalRevenue,I.Party as PartyID
                FROM   SweetPOS.T_SPOSInvoices I               
                WHERE I.InvoiceDate =%s
                AND I.Party IN ({Party}) and I.IsDeleted=0  GROUP BY I.Party  )TR ON TR.PartyID = I.Party
                
                WHERE I.InvoiceDate = %s  
                AND I.Party IN ({Party})  and  I.IsDeleted=0
			    GROUP BY 
                M_Items.SAPItemCode,
                M_Parties.SapPartyCode, 
                TotalRevenue,MC_ItemUnits.UnitID_id,MRPValue,I.InvoiceDate Order by I.Party    '''

            
            
            # Execute query           
            # raw_queryset = T_SPOSInvoices.objects.raw(upload_invoices_query, [InvoiceDate,Party,InvoiceDate,Party])   
            # print(raw_queryset.query)         
            # Generate file name
            # file_name = f"{datetime.now().strftime('%Y%m%d')}_{raw_queryset[0].Name.strip()}_File1.csv"
            raw_queryset = list(T_SPOSInvoices.objects.raw(upload_invoices_query, [InvoiceDate,  InvoiceDate]))  
            if not raw_queryset:  
                raise Exception(f"No records found for Party {Party} on {InvoiceDate}")
            
            manual_date_obj = datetime.strptime(InvoiceDate, '%Y-%m-%d')
            file_name = f"{manual_date_obj.strftime('%Y%m%d')}_{raw_queryset[0].Store.strip()}_File1.csv"
            
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
            self.upload_to_ftp(ftp_file_path, user_name, password, csv_content,Party,InvoiceDate)            
            pass
            # Return success response
            # return JsonResponse({'message': 'File uploaded successfully', 'file_name': file_name})
            
        except Exception as exc:
            # Log and return the error
            self.insert_pos_log(1, "Failed1", str(exc),Party,InvoiceDate)
            return ({'StatusCode': 400, 'Status': True, 'Message':  str(exc), 'Data':[]})
            
    def File3(self, Party,InvoiceDate):
        try:
            
            # Fetch FTP credentials from M_Settings
            settings_map = self.get_ftp_settings()
            user_name = settings_map.get(50)  # Username
            password = settings_map.get(51)  # Password
            FTPFilePath = settings_map.get(52)  # FTPFilePath           
           
            
            upload_invoices_query =f'''SELECT 1 id, DATE_FORMAT(InvoiceDate, '%%Y%%m%%d')SaleDate, FoodERP.M_Parties.SAPPartyCode Store,
                A.ClientID, InvoiceNumber BillNumber 
                FROM SweetPOS.T_SPOSInvoices A
                JOIN FoodERP.M_Parties ON A.Party = FoodERP.M_Parties.id
                WHERE InvoiceDate = %s AND A.Party in ({Party}) and A.IsDeleted=0 order by A.Party '''
                

                # SELECT 1 id, DATE_FORMAT(InvoiceDate, '%%Y%%m%%d') SaleDate, FoodERP.M_Parties.SAPPartyCode Store,
                # A.ClientID, InvoiceNumber BillNumber,M_Parties.Name 
                # FROM T_SPOSInvoices A
                # JOIN FoodERP.M_Parties ON A.Party = FoodERP.M_Parties.id
                # WHERE InvoiceDate = %s AND A.Party =%s

            # Execute query with parameters        
            # raw_queryset = T_SPOSInvoices.objects.raw(upload_invoices_query, [InvoiceDate,Party])
            
            # Generate file name
            # file_name = f"{datetime.now().strftime('%Y%m%d')}_{raw_queryset[0].Name.strip()}_File3.csv"
            raw_queryset = list(T_SPOSInvoices.objects.raw(upload_invoices_query, [InvoiceDate]))  
            if not raw_queryset:  
                raise Exception(f"No records found for Party {Party} on {InvoiceDate}")
            manual_date_obj = datetime.strptime(InvoiceDate, '%Y-%m-%d')
            file_name = f"{manual_date_obj.strftime('%Y%m%d')}_{raw_queryset[0].Store.strip()}_File3.csv"
            
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
            self.upload_to_ftp(ftp_file_path, user_name, password, csv_content,Party,InvoiceDate)           
            return ({'StatusCode': 200, 'Status': True,'Message': file_name +' File uploaded successfully ', 'Data': []})
        except Exception as exc:
            # Log and raise error
            self.insert_pos_log(3, "Failed3", str(exc),Party,InvoiceDate)
            return ({'StatusCode': 400, 'Status': True, 'Message':  str(exc), 'Data':[]})
         
        
    def File2(self, Party,InvoiceDate):
        try:
           
            # Fetch FTP credentials from M_Settings
            settings_map = self.get_ftp_settings()
            user_name = settings_map.get(50)  # Username
            password = settings_map.get(51)  # Password
            FTPFilePath = settings_map.get(52)  # FTPFilePath 
            DoNOtUseItemID= settings_map.get(53)  
            
            upload_invoices_query =f'''SELECT 1 id,DATE_FORMAT(I.InvoiceDate, '%%Y%%m%%d') AS SaleDate,SapItemCode AS Material,
            SUM(Quantity) AS Quantity,M_Units.SAPUnit UOM, M_Parties.SapPartyCode AS Store 
            FROM SweetPOS.TC_SPOSInvoiceItems II 
            join SweetPOS.T_SPOSInvoices  I on I.id= II.Invoice_id
            JOIN FoodERP.M_Items ON M_Items.id = II.Item
            JOIN FoodERP.M_Parties ON M_Parties.id = II.Party
            JOIN FoodERP.MC_ItemUnits ON MC_ItemUnits.id = Unit
            JOIN FoodERP.M_Units ON M_Units.id = MC_ItemUnits.UnitID_id
            WHERE I.InvoiceDate = %s  AND  I.Party in ({Party})   and I.IsDeleted=0 AND II.Item NOT IN  (%s)
            GROUP BY SapItemCode,M_Units.Name,M_Parties.SapPartyCode,I.InvoiceDate,M_Units.id order by I.Party
            
            
            '''

            # Execute query with parameters            
            # raw_queryset = T_SPOSInvoices.objects.raw(upload_invoices_query, [InvoiceDate,Party,DoNOtUseItemID])
            
            # Generate file name
            # file_name = f"{datetime.now().strftime('%Y%m%d')}_{raw_queryset[0].Name.strip()}_File2.csv"
            
            
            raw_queryset = list(T_SPOSInvoices.objects.raw(upload_invoices_query, [InvoiceDate, DoNOtUseItemID]))  
            if not raw_queryset:  
                raise Exception(f"No records found for Party {Party} on {InvoiceDate}")
            manual_date_obj = datetime.strptime(InvoiceDate, '%Y-%m-%d')
            file_name = f"{manual_date_obj.strftime('%Y%m%d')}_{raw_queryset[0].Store.strip()}_File2.csv"
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
            self.upload_to_ftp(ftp_file_path, user_name, password, csv_content,Party,InvoiceDate)    
            pass
        except Exception as exc:
            # Log and raise error
            self.insert_pos_log(2, "Failed2", str(exc),Party,InvoiceDate)
            return ({'StatusCode': 400, 'Status': True, 'Message':  str(exc), 'Data':[]})
        
    def generate_csv(self, headers, rows):
        """Generate CSV content as bytes."""
        output = io.StringIO()
        output.write(",".join(headers) + "\n")
        for row in rows:
            output.write(",".join(map(str, row)) + "\n")
        return output.getvalue().encode("utf-8")
   
    def upload_to_ftp(self, ftp_url, username, password, file_content,Party,InvoiceDate):
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
            self.insert_pos_log(ftp_url, "Success", "File uploaded successfully" + str(Party), Party, InvoiceDate)
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

  
        
    def get_ftp_settings(self):
        """Fetches FTP credentials."""
        Q11 = M_Settings.objects.filter(id__in=[50, 51, 52,53]).values("id", "DefaultValue")
        return {item['id']: item['DefaultValue'] for item in Q11}
    
    def insert_pos_log(self, file_type, status, message, party, sale_date):
        """Log operation details into m_sapposuploadlog."""
        try:
            print(f"Logging: file_type={file_type}, status={status}, message={message}, party={party}, sale_date={sale_date}")
            # party_ids = [int(p.strip()) for p in party.split(',') if p.strip().isdigit()]
            # for pid in party_ids:
            M_SAPPOSUploadLog.objects.create(
                UploadDate=datetime.now(),
                UploadBy=int(party.split(',')[0]),  
                Party=int(party.split(',')[0]),
                SaleDate=sale_date,
                UploadStatus=status,
                Message=message,
                File=file_type
            )
            
        except Exception as e:
            print(f"Failed to insert log: {e}")
    
    
class UploadFileList(APIView):
    permission_classes = (IsAuthenticated,)    
    def get(self, request):
        # SAPPOSUploaddata = JSONParser().parse(request)
        try:
            with transaction.atomic():
                               
                # Party = SAPPOSUploaddata['Party'] 
                # InvoiceDate=SAPPOSUploaddata['InvoiceDate']             
                SAPPOSQuery=M_Users.objects.raw(f'''SELECT FoodERP.M_SAPPOSUploadLog.id, UploadDate,SaleDate,FoodERP.M_Parties.Name, UploadStatus,Message,File  FROM FoodERP.M_SAPPOSUploadLog
                JOIN FoodERP.M_Parties  ON M_Parties.id=Party''')              
                if SAPPOSQuery:
                    POSSAPDetails=list()
                    for row in SAPPOSQuery:
                        POSSAPDetails.append({                            
                            "UploadDate":row.UploadDate,
                            "SaleDate":row.SaleDate,
                            "Name":row.Name,
                            "Message":row.Message,
                            "File":row.File,
                            "UploadStatus":row.UploadStatus,
                        })
                    log_entry = create_transaction_logNew( request, 0, 0, '', 466, 0,0,0,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True,'Message': 'Data Upload Successfully', 'Data': POSSAPDetails})
                log_entry = create_transaction_logNew( request, POSSAPDetails, 0, 'Data Not Found', 466, 0,0,0,0)           
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Record Not Found', 'Data': []})

        except Exception as e:
            log_entry = create_transaction_logNew( request, 0, 0, 'Cashier:'+str(e), 33,0,0,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})