from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from rest_framework.parsers import JSONParser
from FoodERPApp.Views.V_CommFunction import create_transaction_logNew

from ..models import  *



class SPOSCashierSummaryList(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    
    def post(self, request):
        POSCashierdata = JSONParser().parse(request)
        try:
            with transaction.atomic():
                FromDate = POSCashierdata['FromDate']
                ToDate = POSCashierdata['ToDate']
                Party = POSCashierdata['Party']

                WhereClause=""
                if Party:
                    WhereClause= f'''AND SPOSIn.Party={Party}'''
                    # for log
                    if WhereClause :
                        x = Party
                    else:
                        x = 0
                
                CashierSummaryQuery=T_SPOSInvoices.objects.raw(f'''SELECT 1 as id , SPOSIn.InvoiceDate,
                SPOSUser.LoginName CashierName ,
                SUM(SPOSIn.GrandTotal)Amount
                from SweetPOS.T_SPOSInvoices SPOSIn
                JOIN SweetPOS.M_SweetPOSUser SPOSUser ON SPOSUser.id=SPOSIn.CreatedBy
                WHERE SPOSIn.InvoiceDate BETWEEN %s AND %s {WhereClause} 
                GROUP BY SPOSIn.InvoiceDate,SPOSUser.LoginName, SPOSUser.id
                ''',(FromDate,ToDate))
                
                if CashierSummaryQuery:
                    
                    CashierDetails=list()
                    for row in CashierSummaryQuery:
                        
                        CashierDetails.append({
                            
                            "InvoiceDate":row.InvoiceDate,
                            "CashierName":row.CashierName,
                            "Amount":row.Amount                           
                            
                        })

                    log_entry = create_transaction_logNew( request, POSCashierdata, x, '', 386, 0,FromDate,ToDate,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': CashierDetails})
                log_entry = create_transaction_logNew( request, POSCashierdata, x, 'Data Not Found', 386, 0,FromDate,ToDate,0)           
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Record Not Found', 'Data': []})

        except Exception as e:
            log_entry = create_transaction_logNew( request, POSCashierdata, 0, 'SPOSCashierSummary:'+str(e), 33, 0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})