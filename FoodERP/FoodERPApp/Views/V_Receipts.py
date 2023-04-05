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

class ReceiptInvociesViewList(CreateAPIView):

    permission_classes = (IsAuthenticated,)
    authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                Receiptdata = JSONParser().parse(request)
                Party = Receiptdata['Party']
                Customer = Receiptdata['Customer']
                Receiptinvoicequery = TC_OrderItems.objects.raw('''SELECT '2' aa,'0' flag,tc_receiptinvoices.Receipt_id,t_invoices.id as Invoice_ID ,t_invoices.InvoiceDate, t_invoices.GrandTotal,SUM(IFNULL(tc_receiptinvoices.PaidAmount,0)) PaidAmount,(t_invoices.GrandTotal - SUM(IFNULL(tc_receiptinvoices.PaidAmount,0)))  BalAmt FROM t_invoices LEFT JOIN tc_receiptinvoices ON t_invoices.id=tc_receiptinvoices.Invoice_id and tc_receiptinvoices.flag=0 WHERE t_invoices.id NOT IN (SELECT Invoice_ID FROM (SELECT Invoice_id,tc_receiptinvoices.GrandTotal,SUM(PaidAmount) PaidAmount FROM tc_receiptinvoices JOIN t_invoices  ON t_invoices.id= tc_receiptinvoices.Invoice_id and tc_receiptinvoices.flag=0 WHERE t_invoices.Party_id=%s AND t_invoices.Customer_id=%s GROUP BY t_invoices.id ) Invoicess WHERE (GrandTotal-PaidAmount)=0) AND t_invoices.Party_id=%s AND t_invoices.Customer_id=%s GROUP BY t_invoices.id	''', ([Party], [Customer]))
                print(str(Receiptinvoicequery.query))
                return JsonResponse({'StatusCode': 200, 'Status': True,  'Message': 'Order Save Successfully', 'Data': []})
              
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})
