from decimal import Decimal
from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from rest_framework.parsers import JSONParser
from ..Views.V_TransactionNumberfun import GetMaxNumber, GetPrifix
from ..Serializer.S_GST_Reports import *
from ..models import  *
import io
from django.http import HttpResponse


class AllGSTReportsDownloadView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    
    def post(self, request):
        try:
            with transaction.atomic():
                Orderdata = JSONParser().parse(request)
                FromDate = Orderdata['FromDate']
                ToDate = Orderdata['ToDate']
                Party = Orderdata['Party']
                
                
                GSTWisequery = T_Invoices.objects.raw('''SELECT 1 as id, TC_InvoiceItems.GSTPercentage,SUM(BasicAmount)TaxableValue,SUM(CGST)CGST, SUM(SGST)SGST, SUM(IGST)IGST,SUM(CGST)+SUM(SGST)+ SUM(IGST)GSTAmount,SUM(Amount)TotalValue FROM TC_InvoiceItems JOIN T_Invoices ON TC_InvoiceItems.Invoice_id=T_Invoices.id WHERE T_Invoices.Party_id=%s  AND  T_Invoices.InvoiceDate BETWEEN %s AND %s  GROUP BY TC_InvoiceItems.GSTPercentage UNION SELECT 1 as id,0 as GSTPercentage,0 TaxableValue,0 CGST, 0 SGST, 0 IGST,0 GSTAmount,SUM(T_Invoices.TCSAmount)TotalValue FROM T_Invoices WHERE T_Invoices.Party_id=%s  AND  T_Invoices.InvoiceDate BETWEEN %s AND %s ''',([Party],[FromDate],[ToDate],[Party],[FromDate],[ToDate]))
               
                GSTWisedata = GSTWiseSerializer(GSTWisequery, many=True).data
                
                if not GSTWisedata:
                    GSTWisedata = [{
                                    'GST Percentage': None,
                                    'Taxable Value': None,
                                    'CGST': None,
                                    'SGST': None,
                                    'IGST': None,
                                    'GST Amount': None,
                                    'Total Value': None
                                }]
                    
                B2Bquery2 = T_Invoices.objects.raw('''SELECT 'Total' as id, SUM(TaxableValue)TotalTaxableValue,SUM(CGST)TotalCGST,SUM(SGST)TotalSGST,SUM(IGST)TotalIGST,SUM(GSTAmount)TotalGSTAmount,SUM(TotalValue)GrandTotal FROM  (SELECT TC_InvoiceItems.GSTPercentage,SUM(BasicAmount)TaxableValue,SUM(CGST)CGST, SUM(SGST)SGST, SUM(IGST)IGST,SUM(CGST)+SUM(SGST)+ SUM(IGST)GSTAmount,SUM(Amount)TotalValue FROM TC_InvoiceItems JOIN T_Invoices ON TC_InvoiceItems.Invoice_id=T_Invoices.id WHERE T_Invoices.Party_id=%s  AND  T_Invoices.InvoiceDate BETWEEN %s AND %s  GROUP BY TC_InvoiceItems.GSTPercentage UNION SELECT  0 GSTPercentage,0 TaxableValue,0 CGST, 0 SGST, 0 IGST,0 GSTAmount,SUM(T_Invoices.TCSAmount)TotalValue FROM T_Invoices WHERE T_Invoices.Party_id=%s  AND  T_Invoices.InvoiceDate BETWEEN %s AND %s )a  ''',([Party],[FromDate],[ToDate],[Party],[FromDate],[ToDate]))
                GSTWisedata2 = GSTWiseSerializer2(B2Bquery2, many=True).data
                
                if not GSTWisedata2:
                    GSTWisedata2 = [{
                                    'Total Taxable Value': None,
                                    'Total CGST': None,
                                    'Total SGST': None,
                                    'Total IGST': None,
                                    'Total GST Amount': None,
                                    'Grand Total': None
                                }]
                
                response_data = {
                    "GSTWisedata1": GSTWisedata,
                    "GSTWisedata2": GSTWisedata2
                }
                
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': response_data})
        
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': False, 'Message': str(e), 'Data': []})

