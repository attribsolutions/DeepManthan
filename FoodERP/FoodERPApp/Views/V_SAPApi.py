from django.contrib.auth import authenticate
from base64 import b64decode
from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import BasicAuthentication
from django.db import transaction
from ..models import *

class SAPInvoiceView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    # authentication_classes = [BasicAuthentication]

    @transaction.atomic()
    def get(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                user='admin'
                passw='1234'
                # Get the Authorization header from the request
                auth_header = request.META.get('HTTP_AUTHORIZATION', '')
                # Check if the header is a basic authentication header
                if auth_header.startswith('Basic '):
                    # Decode the base64-encoded string in the header and extract the username and password
                    credentials = b64decode(auth_header[6:]).decode('utf-8').split(':')
                    
                    username = credentials[0]
                    password = credentials[1]
                    print(username,password)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'File Uploaded Successfully', 'Data': []})
                    # if(user = credentials[0]):
                    #     return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Authorized user', 'Data': []})
                    # else:
                    #     return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'UnAuthorized user', 'Data': []})

        except Exception as e:
            raise JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})






