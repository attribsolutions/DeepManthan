import base64
from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import BasicAuthentication
# from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import transaction
from rest_framework.parsers import MultiPartParser, FormParser
from ..Views.V_CommFunction import GetO_BatchWiseLiveStock
from ..Serializer.S_Orders import TC_OrderTermsAndConditionsSerializer
from ..Serializer.S_abc import *
from ..models import *

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate


class AbcView(CreateAPIView):

    permission_classes = (IsAuthenticated,)
    authentication_classes = [BasicAuthentication]
    # parser_classes = (MultiPartParser, FormParser)

    @transaction.atomic()
    def post(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                file_serializer =  TC_OrderTermsAndConditionsSerializer(data=request.data)
                if file_serializer.is_valid():
                    file_serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'File Uploaded Successfully', 'Data': []})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': file_serializer.errors, 'Data': []})
        except Exception as e:
            raise JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})

    @transaction.atomic()
    def get(self, request ):
        try:
            with transaction.atomic():
                auth_header = request.META.get('HTTP_AUTHORIZATION')
                if auth_header:
                # Parsing the authorization header
                    auth_type, auth_string = auth_header.split(' ', 1)
                if auth_type.lower() == 'basic':
                    # Decoding the base64-encoded username and password
                    try:
                        username, password = base64.b64decode(auth_string).decode().split(':', 1)
                    except (TypeError, ValueError, UnicodeDecodeError):
                        return Response('Invalid authorization header', status=status.HTTP_401_UNAUTHORIZED)
                    # Authenticating the user
                    user = authenticate(request, username=username, password=password)
                    if user is not None:
                        # Username and password are valid
                        return Response('Authenticated', status=status.HTTP_200_OK)
                # Invalid authorization header or authentication failed
                return Response('Unauthorized', status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            raise JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})



        
        
# class MultipleReceiptView(CreateAPIView):
    
    # permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    # @transaction.atomic()
    # def post(self, request):
    #     try:
    #         with transaction.atomic():
    #             Receiptdata = JSONParser().parse(request)
    #             for aa in  Receiptdata['data']:   
    #                 Party = aa['Party']
    #                 Date = aa['ReceiptDate']
    #                 '''Get Max Receipt Number'''
    #                 a = GetMaxNumber.GetReceiptNumber(Party,Date)
    #                 aa['ReceiptNo'] = a
    #                 '''Get Receipt Prifix '''
    #                 b = GetPrifix.GetReceiptPrifix(Party)
    #                 aa['FullReceiptNumber'] = b+""+str(a)
    #                 Receipt_serializer = ReceiptSerializer(data=aa)
    #                 if Receipt_serializer.is_valid():
    #                     Receipt_serializer.save()
    #             return JsonResponse({'StatusCode': 200, 'Status': True,  'Message': 'Receipt Save Successfully', 'Data': []})    
    #     except Exception as e:
    #         return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []}) 
                
        # JSON BODY Above Code    
        # {
        #         "data": [
        #         {
        #             "ReceiptDate": "2023-04-13",
        #             "Description": "",
        #             "AmountPaid": "32.00",
        #             "BalanceAmount": "",
        #             "OpeningBalanceAdjusted": "",
        #             "DocumentNo": "",
        #             "AdvancedAmountAjusted": "",
        #             "Customer": 1,
        #             "ChequeDate": "",
        #             "Party": 4,
        #             "ReceiptMode": 31,
        #             "ReceiptType": 29,
        #             "CreatedBy": 5,
        #             "UpdatedBy": 5,
        #             "ReceiptInvoices": [
        #                 {
        #                     "Invoice": 21,
        #                     "GrandTotal": "32.00",
        #                     "PaidAmount": "32",
        #                     "flag": 0
        #                 }
        #             ]
        #         },
        #         {
        #             "ReceiptDate": "2023-04-13",
        #             "Description": "",
        #             "AmountPaid": "76.00",
        #             "BalanceAmount": "",
        #             "OpeningBalanceAdjusted": "",
        #             "DocumentNo": "",
        #             "AdvancedAmountAjusted": "",
        #             "Customer": 1,
        #             "ChequeDate": "",
        #             "Party": 4,
        #             "ReceiptMode": 31,
        #             "ReceiptType": 29,
        #             "CreatedBy": 5,
        #             "UpdatedBy": 5,
        #             "ReceiptInvoices": [
        #                 {
        #                     "Invoice": 22,
        #                     "GrandTotal": "276.00",
        #                     "PaidAmount": "76",
        #                     "flag": 0
        #                 }
        #             ]
        #         }
        #     ]
        # }
        
    # @transaction.atomic()
    # def post(self, request):
    #         try:
    #             with transaction.atomic():
    #                 Receiptdata = JSONParser().parse(request)
    #                 studentsList=[]
    #                 for jsonObj in Receiptdata:
    #                     studentDict = json.loads(jsonObj)
    #                     studentsList.append(studentDict)
                    
    #                 for cc in studentsList: 
    #                     Party = cc['Party']
    #                     Date = cc['ReceiptDate']
    #                     '''Get Max Receipt Number'''
    #                     a = GetMaxNumber.GetReceiptNumber(Party,Date)
                       
    #                     cc['ReceiptNo'] = a
    #                     '''Get Receipt Prifix '''
    #                     b = GetPrifix.GetReceiptPrifix(Party)
                    
    #                     cc['FullReceiptNumber'] = b+""+str(a)
                       
    #                     Receipt_serializer = ReceiptSerializer(data=cc)
    #                     if Receipt_serializer.is_valid():
    #                         Receipt_serializer.save()
    #                 return JsonResponse({'StatusCode': 200, 'Status': True,  'Message': 'Receipt Save Successfully', 'Data': []})
    #                 return JsonResponse({'StatusCode': 406, 'Status': True,  'Message': Receipt_serializer.errors, 'Data': []})
    #         except Exception as e:
    #             return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})              
         