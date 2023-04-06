from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, transaction
from rest_framework.parsers import JSONParser
from ..Views.V_TransactionNumberfun import GetMaxNumber, GetPrifix
from ..Serializer.S_Receipts import *
from django.db.models import Sum
from ..models import *


class ReceiptInvoicesView(CreateAPIView):

    permission_classes = (IsAuthenticated,)
    authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                Receiptdata = JSONParser().parse(request)
                Party = Receiptdata['Party']
                Customer = Receiptdata['Customer']
                Receiptinvoicequery = TC_ReceiptInvoices.objects.raw('''SELECT '0' id, '2' aa,'0' flag,tc_receiptinvoices.Receipt_id,t_invoices.id as Invoice_ID ,t_invoices.InvoiceDate,t_invoices.FullInvoiceNumber, t_invoices.GrandTotal,SUM(IFNULL(tc_receiptinvoices.PaidAmount,0)) PaidAmount,(t_invoices.GrandTotal - SUM(IFNULL(tc_receiptinvoices.PaidAmount,0)))  BalAmt FROM t_invoices LEFT JOIN tc_receiptinvoices ON t_invoices.id=tc_receiptinvoices.Invoice_id and tc_receiptinvoices.flag=0 WHERE t_invoices.id NOT IN (SELECT Invoice_ID FROM (SELECT Invoice_id,tc_receiptinvoices.GrandTotal,SUM(PaidAmount) PaidAmount FROM tc_receiptinvoices JOIN t_invoices  ON t_invoices.id= tc_receiptinvoices.Invoice_id and tc_receiptinvoices.flag=0 WHERE t_invoices.Party_id=%s AND t_invoices.Customer_id=%s GROUP BY t_invoices.id ) Invoicess WHERE (GrandTotal-PaidAmount)=0) AND t_invoices.Party_id=%s AND t_invoices.Customer_id=%s GROUP BY t_invoices.id	''', ([Party], [Customer], [Party], [Customer]))
           
                OrderItemSerializer = ReceiptInvoiceserializer(Receiptinvoicequery, many=True).data
                ReceiptInvoiceList = list()
                for a in OrderItemSerializer:
                    ReceiptInvoiceList.append({
                        "Receipt":a['Receipt_id'],
                        "Invoice":a['Invoice_ID'],
                        "InvoiceDate":a['InvoiceDate'],
                        "FullInvoiceNumber":a['FullInvoiceNumber'],
                        "GrandTotal":a['GrandTotal'],
                        "PaidAmount":a['PaidAmount'],
                        "BalanceAmount":a['BalAmt']
                    })
                return JsonResponse({'StatusCode': 200, 'Status': True,  'Message': '', 'Data': ReceiptInvoiceList})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})

class ReceiptListView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request, id=0):
        try:
            with transaction.atomic():
                Receiptdata = JSONParser().parse(request)
                FromDate = Receiptdata['FromDate']
                ToDate = Receiptdata['ToDate']
                Customer = Receiptdata['Customer']
                Party = Receiptdata['Party']
               
                if(Customer == ''):
                    query = T_Receipts.objects.filter(ReceiptDate__range=[FromDate, ToDate], Party=Party)
                else:
                    query = T_Receipts.objects.filter(ReceiptDate__range=[FromDate, ToDate], Customer=Customer, Party=Party)
                   
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
                            "ReceiptMode": a['ReceiptMode']['Name'],
                            "ReceiptType": a['ReceiptType']['Name'],
                            "AmountPaid": a['AmountPaid'],
                            "DocumentNo": a['DocumentNo'],
                            "BalanceAmount": a['BalanceAmount'],
                            "OpeningBalanceAdjusted": a['OpeningBalanceAdjusted'],
                            "ChequeDate": a['ChequeDate'],
                            "Bank": a['Bank']['Name'],
                            "DepositorBank": a['DepositorBank']['Name'],
                            "CreatedOn": a['CreatedOn']

                        })
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': ReceiptListData})
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Record Not Found', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})   
        
        
class ReceiptView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                Receiptdata = JSONParser().parse(request)
                Party = Receiptdata['Party']
                '''Get Max Receipt Number'''
                a = GetMaxNumber.GetOrderNumber(Party)
                # return JsonResponse({'StatusCode': 200, 'Status': True,   'Data':[] })
                Receiptdata['ReceiptNo'] = a
                '''Get Receipt Prifix '''
                b = GetPrifix.GetReceiptPrifix(Party)
                Receiptdata['FullReceiptNumber'] = b+""+str(a)
                # return JsonResponse({ 'Data': Orderdata })
                Receipt_serializer = ReceiptSerializer(data=Receiptdata)
                if Receipt_serializer.is_valid():
                    Receipt_serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True,  'Message': 'Receipt Save Successfully', 'Data': []})
                return JsonResponse({'StatusCode': 406, 'Status': True,  'Message': Receipt_serializer.errors, 'Data': []})
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
        
