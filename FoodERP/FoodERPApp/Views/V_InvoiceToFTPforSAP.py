from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from rest_framework.parsers import JSONParser
from django.http import JsonResponse
from ..models import *
import io
from ftplib import FTP
from urllib.parse import urlparse
from ..Views.V_CommFunction import *


class InvoiceSendToFTPForSAP(APIView):
    permission_classes = (IsAuthenticated,)
    @transaction.atomic
    def post(self, request):
        InvoiceData = JSONParser().parse(request) 
        # print('sssssssssss')       
        try:
            InvoiceID = InvoiceData['InvoiceID'] 
            
            settings_map = self.get_ftp_settings()
            user_name = settings_map.get(50)  # Username
            password = settings_map.get(51)  # Password
            FTPFilePath = settings_map.get(52)  # FTPFilePath       
                
            ItemSAPCode=f'''SELECT 1 id ,  
            'IN60' AS Vendor,
            M_Parties.SAPPartyCode AS Plant,
            T_Invoices.Party_id PartyID,
            T_Invoices.InvoiceDate ,
            DATE_FORMAT(T_Invoices.InvoiceDate, '%%d.%%m.%%Y') DocumentDate,
            0 AS DeliveryNote,
            '' AS BillofLading,
            '' AS HeaderText,
            T_Invoices.FullInvoiceNumber AS VenderInvoiceNumber,
            T_Invoices.GrandTotal AS InvoiceheaderAmountwithGST,
            M_Items.SAPItemCode AS Material,
            TC_InvoiceItems.Quantity,
            O_LiveBatches.BatchCode,
            
            DATE_FORMAT(O_LiveBatches.BatchDate, '%%d.%%m.%%Y') ProdnDate,
            DATE_FORMAT(O_LiveBatches.ItemExpiryDate, '%%d.%%m.%%Y') sled
            FROM T_Invoices 
            JOIN TC_InvoiceItems ON TC_InvoiceItems.Invoice_ID = T_Invoices.ID 
            JOIN M_Items ON M_Items.ID = TC_InvoiceItems.Item_ID
            JOIN M_Parties ON M_Parties.ID = T_Invoices.Customer_id
            JOIN O_LiveBatches ON O_LiveBatches.id = TC_InvoiceItems.LiveBatch_id
            JOIN O_BatchWiseLiveStock ON O_BatchWiseLiveStock.LiveBatche_id = O_LiveBatches.id
            WHERE T_Invoices.ID = %s '''                   
             
            raw_queryset = T_Invoices.objects.raw(ItemSAPCode, [InvoiceID])   
            shedshortname =M_Settings.objects.filter(id=64).values('DefaultValue')
            dd=shedshortname[0]['DefaultValue']
            
            for i in raw_queryset:
                shortname=dd.split(',')
                for j in shortname:
                    ss=j.split('-')
                    if int(i.PartyID) == int(ss[0]):
                        N=ss[1]
                
                InvoiceDate = i.InvoiceDate
                Plant = i.Plant
                InvNo =i.VenderInvoiceNumber 
                PartyID=i.PartyID      
             
            file_name = f"{InvoiceDate.strftime('%Y%m%d')}_{Plant}_IN60_{N}_{InvNo}.csv"
            # print(file_name)
            ftp_file_path = f"{FTPFilePath}/inbound/GRN_MIR7/source/{file_name}"
            # print(ftp_file_path)
            headers = [
                "Vendor", "Plant", "DocumentDate","DeliveryNote","BillofLading",
                "HeaderText","VenderInvoiceNumber","InvoiceheaderAmountwithGST","Material","Quantity",
                "BatchCode","ProdnDate","sled"
            ]
            rows = [
                [
                    item.Vendor, item.Plant, item.DocumentDate,item.DeliveryNote,item.BillofLading,item.HeaderText,
                    item.VenderInvoiceNumber,item.InvoiceheaderAmountwithGST,item.Material,item.Quantity,
                    item.BatchCode,item.ProdnDate,item.sled                            
                    
                ]
                for item in raw_queryset
            ]
            
            csv_content = self.generate_csv(headers, rows)
            

            # Upload to FTP
            self.upload_to_ftp(ftp_file_path, user_name, password, csv_content) 
                       
            sapupdatequery = T_Invoices.objects.filter(id=InvoiceID).update(IsSendToFTPSAP=1)
            log_entry = create_transaction_logNew(request,InvoiceID, PartyID,f'File uploaded successfully: {file_name}',456,0)
            return JsonResponse ({'StatusCode': 200, 'Status': True,'Message': file_name +' File uploaded successfully ', 'Data': []})
            
                    
        except Exception as exc:
            
            log_entry = create_transaction_logNew(request,InvoiceID, 0,'FileUploadedError:'+str(exc),33,0)
            return JsonResponse ({'StatusCode': 400, 'Status': True, 'Message':  str(exc), 'Data':[]})
                
                
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
            
            # print(ftp.login(username, password))
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
    
    def generate_csv(self, headers, rows):
        """Generate CSV content as bytes."""
        output = io.StringIO()
        output.write(",".join(headers) + "\n")
        for row in rows:
            output.write(",".join(map(str, row)) + "\n")
        return output.getvalue().encode("utf-8")