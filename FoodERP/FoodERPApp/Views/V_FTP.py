import os
from ftplib import FTP
import requests
from datetime import datetime
from django.conf import settings
# from myapp.models import SAPLedger  # Import your SAPLedger model
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response
from django.http import JsonResponse
from django.views import View
from django.core.exceptions import PermissionDenied
from ..models import *
from django.views.generic import View
from django.db import IntegrityError, transaction
from rest_framework.parsers import JSONParser
from django.db.models import Q
from django.db import connection
from ..Views.V_CommFunction import *
from rest_framework.authentication import BasicAuthentication, TokenAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication


class ReadFTPFileView(View):
    
    permission_classes = (IsAuthenticated,)
    authentication_classes = [BasicAuthentication, TokenAuthentication, JWTAuthentication]
    # authentication_class = JSONWebTokenAuthentication
    
    def get(self, request):
        try:
            # FTP server config
            server = '10.101.20.177'
            username = 'ftp1'
            password = 'Newroot@123!'
            source_folder = '/outbound/FERP_CSCM/custledger/source'
            success_folder = '/outbound/FERP_CSCM/custledger/success'

            # Connect to FTP server
            ftp = FTP(server)
            ftp.login(username, password)

            # Get list of CSV files in source folder
            files = ftp.nlst(source_folder)

            if not files:
                ftp.quit()
                log_entry = create_transaction_logNew(request,{'UserID': 1},0,'No files to process',460,0)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'No files to process.', 'Data': []})

            for file in files:
                # Process only CSV files
                if not file.lower().endswith('.csv'):
                    continue

                lines = []
                ftp.retrlines('RETR ' + file, lines.append)

                if len(lines) <= 1:
                    continue  # Skip empty files or those with only a header

                lines = lines[1:]  # skip header

                SAPItems = []
                for line in lines:
                    values = line.split(',')

                    if len(values) < 11:
                        continue  # Skip invalid/malformed lines

                    try:
                        # Parse posting date
                        PostingDate = values[4]
                        PostDate = datetime.strptime(PostingDate, "%Y%m%d")
                        PostingDateFormat = PostDate.strftime("%Y-%m-%d")

                        # Extract file date from filename
                        FileDate = os.path.basename(file).split('_')[0]
                        FileDateFormat = f"{FileDate[:4]}-{FileDate[4:6]}-{FileDate[6:8]}"

                        SAPItems.append(M_SAPCustomerLedger(
                            CompanyCode=values[0],
                            DocumentNo=values[1],
                            FiscalYear=values[2],
                            DocumentType=values[3],
                            PostingDate=PostingDateFormat,
                            DocumentDesc=values[5],
                            CustomerCode=values[6],
                            CustomerName=values[7],
                            DebitCredit=values[8],
                            Amount=float(values[9].replace("-", "")) if values[8] == "H" else float(values[9]),
                            ItemText=values[10],
                            CreatedBy=1,
                            UpdatedBy=1,
                            FileDate=FileDateFormat
                        ))
                    except Exception as line_error:
                        continue  # optionally log malformed lines

                # Bulk insert records
                if SAPItems:
                    M_SAPCustomerLedger.objects.bulk_create(SAPItems)

                # Move processed file to success folder
                filename = os.path.basename(file)
                ftp.rename(f"{source_folder}/{filename}", f"{success_folder}/{filename}")

            ftp.quit()
            create_transaction_logNew(request, {'UserID': 1}, 0, 'FTP Data processed successfully', 460, 0)
            return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Data processed successfully.', 'Data': []})

        except Exception as e:
            log_entry = create_transaction_logNew(request,{'UserID': 1}, 0,'FTPData:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': False, 'Message': str(e), 'Data': []})