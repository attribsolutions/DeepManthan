

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from rest_framework.parsers import JSONParser
from django.http import JsonResponse
from ..models import *
import io
from ftplib import FTP
from urllib.parse import urlparse


class InvoiceSendToFTPForSAP(APIView):
    permission_classes = (IsAuthenticated,)
    @transaction.atomic
    def post(self, request):
        InvoiceData = JSONParser().parse(request)        
        try:
            InvoiceID = InvoiceData['InvoiceID'] 
            self.Upload_InvoiceToSAP(InvoiceID)
            return JsonResponse({'message': 'Uploaded successfully'}, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500) 

    def Upload_InvoiceToSAP(self, InvoiceID):
            try:
                    # Fetch FTP credentials from M_Settings
                    settings_map = self.get_ftp_settings()
                    user_name = settings_map.get(50)  # Username
                    password = settings_map.get(51)  # Password
                    FTPFilePath = settings_map.get(52)  # FTPFilePath           
                    ItemSAPCode=f'''SELECT M_Items.Name 
                        FROM T_Invoices 
                        JOIN TC_InvoiceItems ON TC_InvoiceItems.Invoice_ID = T_Invoices.ID 
                        JOIN M_Items ON M_Items.ID = TC_InvoiceItems.Item_ID
                        WHERE T_Invoices.ID = {InvoiceID} AND IFNULL(SapItemCode, '') = '' 
                        LIMIT 1'''
                    # if not ItemSAPCode: 
                        # Raw SQL Query
                    upload_invoices_query = f'''Select  1 id, ChallanDate ,Quantity,Rate from T_Challan 
                    Join TC_ChallanItems ON TC_ChallanItems.Challan_id=T_Challan.id Where Challan_id=%s'''
                    # Execute query           
                    raw_queryset = T_Invoices.objects.raw(upload_invoices_query, [InvoiceID])            
                    # Generate file name
                    file_name = f"{datetime.now().strftime('%Y%m%d')}_InvoiceFile1.csv"
                    # print(file_name)
                    ftp_file_path = f"{FTPFilePath}/inbound/GRN_MIR7/source/{file_name}"
                    # print(ftp_file_path)
                    # Prepare CSV content
                    headers = [
                        "ChallanDate", "Quantity", "Rate"
                    ]
                    rows = [
                        [
                            item.ChallanDate, item.Quantity, item.Rate
                            
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
    
    def generate_csv(self, headers, rows):
        """Generate CSV content as bytes."""
        output = io.StringIO()
        output.write(",".join(headers) + "\n")
        for row in rows:
            output.write(",".join(map(str, row)) + "\n")
        return output.getvalue().encode("utf-8")