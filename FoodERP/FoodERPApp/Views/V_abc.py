from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
# from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import transaction
from rest_framework.parsers import MultiPartParser, FormParser

from ..Views.V_CommFunction import GetO_BatchWiseLiveStock

from ..Serializer.S_Orders import TC_OrderTermsAndConditionsSerializer

from ..Serializer.S_abc import *
from ..models import *


class AbcView(CreateAPIView):

    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication
    parser_classes = (MultiPartParser, FormParser)

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
                print('aaaaa')
                Modulesdata = TC_OrderTermsAndConditions.objects.filter(Order=201)
                print('bbbbb')
                if Modulesdata.exists():
                    print('ccccc')
                    Modules_Serializer = TC_OrderTermsAndConditionsSerializer(
                    Modulesdata, many=True)
                    Stock=GetO_BatchWiseLiveStock(44,4)
                    print(Stock)
                    return JsonResponse({'StatusCode': 200, 'Status': True,'Message': float(Stock),'Data': Modules_Serializer.data })
                return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'Modules Not available', 'Data': []})    
        except Exception as e :
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':   'Execution Error', 'Data':[e]})
        
        
        
        
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
         