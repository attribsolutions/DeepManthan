from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
# from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, transaction
from rest_framework.parsers import JSONParser
from ..Views.V_TransactionNumberfun import GetMaxNumber, GetPrifix
from ..Serializer.S_Receipts import *
from django.db.models import Q, Sum
from datetime import date
from ..models import *


class ReceiptInvoicesView(CreateAPIView):

    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                Receiptdata = JSONParser().parse(request)
                Party = Receiptdata['PartyID']
                Customer = Receiptdata['CustomerID']
                InvoiceIDs = Receiptdata['InvoiceID']
                Invoice_list = InvoiceIDs.split(",")
                if(InvoiceIDs == ""):
                    Receiptinvoicequery = TC_ReceiptInvoices.objects.raw('''SELECT '0' id,TC_ReceiptInvoices.Receipt_id,T_Invoices.id as Invoice_ID ,T_Invoices.InvoiceDate,T_Invoices.FullInvoiceNumber,T_Invoices.Customer_id,M_Parties.Name AS CustomerName, T_Invoices.GrandTotal,SUM(IFNULL(TC_ReceiptInvoices.PaidAmount,0)) PaidAmount,(T_Invoices.GrandTotal - SUM(IFNULL(TC_ReceiptInvoices.PaidAmount,0)))  BalAmt FROM T_Invoices LEFT JOIN TC_ReceiptInvoices ON T_Invoices.id=TC_ReceiptInvoices.Invoice_id JOIN M_Parties ON M_Parties.id= T_Invoices.Customer_id  WHERE T_Invoices.id NOT IN (SELECT Invoice_id FROM TC_ReceiptInvoices) AND T_Invoices.Party_id=%s AND T_Invoices.Customer_id=%s GROUP BY T_Invoices.id	''', ([Party], [Customer]))
                else:
                    Receiptinvoicequery = TC_ReceiptInvoices.objects.raw('''SELECT '0' id,TC_ReceiptInvoices.Receipt_id,T_Invoices.id as Invoice_ID ,T_Invoices.InvoiceDate,T_Invoices.FullInvoiceNumber,T_Invoices.Customer_id,M_Parties.Name AS CustomerName, T_Invoices.GrandTotal,SUM(IFNULL(TC_ReceiptInvoices.PaidAmount,0)) PaidAmount,(T_Invoices.GrandTotal - SUM(IFNULL(TC_ReceiptInvoices.PaidAmount,0)))  BalAmt FROM T_Invoices LEFT JOIN TC_ReceiptInvoices ON T_Invoices.id=TC_ReceiptInvoices.Invoice_id JOIN M_Parties ON M_Parties.id= T_Invoices.Customer_id  WHERE T_Invoices.Party_id=%s AND T_Invoices.id IN %s  GROUP BY T_Invoices.id	''', ([Party],Invoice_list))
                    # print(str(Receiptinvoicequery.query))  
                ReceiptInvoiceSerializer = ReceiptInvoiceserializer(Receiptinvoicequery, many=True).data
                ReceiptInvoiceList = list()
                for a in ReceiptInvoiceSerializer:
                    ReceiptInvoiceList.append({
                        "Receipt":a['Receipt_id'],
                        "Customer":a['Customer_id'],
                        "CustomerName":a['CustomerName'],
                        "Invoice":a['Invoice_ID'],
                        "InvoiceDate":a['InvoiceDate'],
                        "FullInvoiceNumber":a['FullInvoiceNumber'],
                        "GrandTotal":a['GrandTotal'],
                        "PaidAmount":a['PaidAmount'],
                        "BalanceAmount":a['BalAmt'],    
                    })
                return JsonResponse({'StatusCode': 200, 'Status': True,  'Message': '', 'Data': ReceiptInvoiceList})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})

class ReceiptListView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request, id=0):
        try:
            with transaction.atomic():
                Receiptdata = JSONParser().parse(request)
                FromDate = Receiptdata['FromDate']
                ToDate = Receiptdata['ToDate']
                Customer = Receiptdata['CustomerID']
                Party = Receiptdata['PartyID']
                ReceiptType = Receiptdata['ReceiptType']
               
                if(Customer == ''):
                    query = T_Receipts.objects.filter(ReceiptDate__range=[FromDate, ToDate], Party=Party, ReceiptType=ReceiptType)
                else:
                    query = T_Receipts.objects.filter(ReceiptDate__range=[FromDate, ToDate], Customer=Customer, Party=Party, ReceiptType=ReceiptType)
                   
                # return JsonResponse({'query': str(Orderdata.query)})
                if query:
                    Receipt_serializer = ReceiptSerializerSecond(query, many=True).data
                    # return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':'','Data': Order_serializer})
                    ReceiptListData = list()
                    for a in Receipt_serializer:
                        ReceiptListData.append({
                            "id": a['id'],
                            "ReceiptDate": a['ReceiptDate'],
                            "FullReceiptNumber": a['FullReceiptNumber'],
                            "CustomerID": a['Customer']['id'],
                            "Customer": a['Customer']['Name'],
                            "PartyID": a['Party']['id'],
                            "Party": a['Party']['Name'],
                            "Description": a['Description'],
                            "ReceiptMode": a['ReceiptMode']['id'],
                            "ReceiptModeName": a['ReceiptMode']['Name'],
                            "ReceiptType": a['ReceiptType']['id'],
                            "ReceiptTypeName": a['ReceiptType']['Name'],
                            "AmountPaid": a['AmountPaid'],
                            "DocumentNo": a['DocumentNo'],
                            "BalanceAmount": a['BalanceAmount'],
                            "OpeningBalanceAdjusted": a['OpeningBalanceAdjusted'],
                            "ChequeDate": a['ChequeDate'],
                            "Bank": a['Bank']['id'],
                            "BankName": a['Bank']['Name'],
                            "DepositorBank": a['DepositorBank']['id'],
                            "DepositorBankName": a['DepositorBank']['Name'],
                            "CreatedOn": a['CreatedOn']

                        })
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': ReceiptListData})
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Record Not Found', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})   
        
        
class ReceiptView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication
    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                Receiptdata = JSONParser().parse(request)
                for aa in  Receiptdata['BulkData']:   
                    Party = aa['Party']
                    Date = aa['ReceiptDate']
                    '''Get Max Receipt Number'''
                    a = GetMaxNumber.GetReceiptNumber(Party,Date)
                    aa['ReceiptNo'] = a
                    '''Get Receipt Prifix '''
                    b = GetPrifix.GetReceiptPrifix(Party)
                    aa['FullReceiptNumber'] = b+""+str(a)
                    Receipt_serializer = ReceiptSerializer(data=aa)
                    if Receipt_serializer.is_valid():
                        Receipt_serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True,  'Message': Receipt_serializer.errors, 'Data': []})   
                return JsonResponse({'StatusCode': 200, 'Status': True,  'Message': 'Receipt Save Successfully', 'Data': []})    
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})

    # @transaction.atomic()
    # def post(self, request):
    #     try:
    #         with transaction.atomic():
    #             Receiptdata = JSONParser().parse(request)
    #             Party = Receiptdata['Party']
    #             Date = Receiptdata['ReceiptDate']
    #             '''Get Max Receipt Number'''
    #             a = GetMaxNumber.GetReceiptNumber(Party,Date)
    #             # return JsonResponse({'StatusCode': 200, 'Status': True,   'Data':[] })
    #             Receiptdata['ReceiptNo'] = a
    #             '''Get Receipt Prifix '''
    #             b = GetPrifix.GetReceiptPrifix(Party)
             
    #             Receiptdata['FullReceiptNumber'] = b+""+str(a)
    #             # return JsonResponse({ 'Data': Orderdata })
    #             Receipt_serializer = ReceiptSerializer(data=Receiptdata)
    #             if Receipt_serializer.is_valid():
    #                 Receipt_serializer.save()
    #                 return JsonResponse({'StatusCode': 200, 'Status': True,  'Message': 'Receipt Save Successfully', 'Data': []})
    #             return JsonResponse({'StatusCode': 406, 'Status': True,  'Message': Receipt_serializer.errors, 'Data': []})
    #     except Exception as e:
    #         return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})
        
        
    @transaction.atomic()
    def get(self, request, id=0):
        try:
            with transaction.atomic():
                query = T_Receipts.objects.filter(id=id)
                if query.exists():
                    Receipt_serializer = ReceiptSerializerSecond(query, many=True).data
                    ReceiptListData = list()
                    for a in Receipt_serializer:
                        ReceiptListData.append({
                            "id": a['id'],
                            "ReceiptDate": a['ReceiptDate'],
                            "FullReceiptNumber": a['FullReceiptNumber'],
                            "CustomerID": a['Customer']['id'],
                            "Customer": a['Customer']['Name'],
                            "PartyID": a['Party']['id'],
                            "Party": a['Party']['Name'],
                            "Description": a['Description'],
                            "ReceiptMode": a['ReceiptMode']['id'],
                            "ReceiptModeName": a['ReceiptMode']['Name'],
                            "ReceiptType": a['ReceiptType']['id'],
                            "ReceiptTypeName": a['ReceiptType']['Name'],
                            "AmountPaid": a['AmountPaid'],
                            "DocumentNo": a['DocumentNo'],
                            "BalanceAmount": a['BalanceAmount'],
                            "OpeningBalanceAdjusted": a['OpeningBalanceAdjusted'],
                            "ChequeDate": a['ChequeDate'],
                            "Bank": a['Bank']['id'],
                            "BankName": a['Bank']['Name'],
                            "DepositorBank": a['DepositorBank']['id'],
                            "DepositorBankName": a['DepositorBank']['Name'],
                            "CreatedOn": a['CreatedOn']

                        })
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': ReceiptListData[0]})
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Record Not Found', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})    
        
        
    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                Receiptdata = T_Receipts.objects.get(id=id)
                Receiptdata.delete()
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Receipt Deleted Successfully', 'Data':[]})
        except IntegrityError:   
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Receipt used in another table', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})  
        
         
        
class MakeReceiptOfPaymentListView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request, id=0):
        try:
            with transaction.atomic():
                Receiptdata = JSONParser().parse(request)
                FromDate = Receiptdata['FromDate']
                ToDate = Receiptdata['ToDate']
                Party = Receiptdata['PartyID']
                Customer = Receiptdata['CustomerID']
                ReceiptType = Receiptdata['ReceiptType']
                if(Customer == ''):
                    query = T_Receipts.objects.filter(ReceiptDate__range=[FromDate, ToDate], Customer=Party, ReceiptType=ReceiptType)
                else:    
                    query = T_Receipts.objects.filter(ReceiptDate__range=[FromDate, ToDate], Customer=Party, Party=Customer, ReceiptType=ReceiptType)
               
                   
                if query:
                    Receipt_serializer = ReceiptSerializerSecond(query, many=True).data
                    # return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':'','Data': Order_serializer})
                    ReceiptListData = list()
                    for a in Receipt_serializer:
                        ReceiptListData.append({
                            "id": a['id'],
                            "ReceiptDate": a['ReceiptDate'],
                            "FullReceiptNumber": a['FullReceiptNumber'],
                            "CustomerID": a['Party']['id'],
                            "Customer": a['Party']['Name'],
                            "Description": a['Description'],
                            "ReceiptMode": a['ReceiptMode']['id'],
                            "ReceiptModeName": a['ReceiptMode']['Name'],
                            "ReceiptType": a['ReceiptType']['id'],
                            "ReceiptTypeName": a['ReceiptType']['Name'],
                            "AmountPaid": a['AmountPaid'],
                            "DocumentNo": a['DocumentNo'],
                            "BalanceAmount": a['BalanceAmount'],
                            "OpeningBalanceAdjusted": a['OpeningBalanceAdjusted'],
                            "ChequeDate": a['ChequeDate'],
                            "Bank": a['Bank']['id'],
                            "BankName": a['Bank']['Name'],
                            "DepositorBank": a['DepositorBank']['id'],
                            "DepositorBankName": a['DepositorBank']['Name'],
                            "CreatedOn": a['CreatedOn']

                        })
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': ReceiptListData})
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Record Not Found', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})    
          
