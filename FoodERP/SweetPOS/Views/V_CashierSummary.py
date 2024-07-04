from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from rest_framework.parsers import JSONParser
from rest_framework.authentication import BasicAuthentication
from SweetPOS.Views.V_SweetPosRoleAccess import BasicAuthenticationfunction

from ..models import  *



class SPOSCashierSummaryList(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    
    def post(self, request, id=0):
        POSCashierdata = JSONParser().parse(request)
        try:
            with transaction.atomic():
                FromDate = POSCashierdata['FromDate']
                ToDate = POSCashierdata['ToDate']
                Party = POSCashierdata['Party']
             
                WhereClause=""
                if Party:
                    WhereClause= f'AND SPOSIn.Party={Party}'
                
                CashierSummaryQuery=T_SPOSInvoices.objects.raw(f'''SELECT 1 as id , SPOSIn.InvoiceDate,
                SPOSUser.LoginName CashierName ,
                SUM(SPOSIn.GrandTotal)Amount
                from SweetPOS.T_SPOSInvoices SPOSIn
                JOIN SweetPOS.M_SweetPOSUser SPOSUser ON SPOSUser.id=SPOSIn.CreatedBy
                WHERE SPOSIn.InvoiceDate BETWEEN {FromDate} AND {ToDate} {WhereClause} 
                GROUP BY SPOSIn.InvoiceDate,SPOSUser.LoginName, SPOSUser.id
                ''')
                print(CashierSummaryQuery)
                if CashierSummaryQuery:
                    print('sssssssssssssss')
                    CashierDetails=list()
                    for row in CashierSummaryQuery:
                        print(row)
                        CashierDetails.append({
                            
                            "InvoiceDate":row.InvoiceDate,
                            "CashierName":row.CashierName,
                            "Amount":row.Amount                           
                            
                        })
                    
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': CashierDetails})
                            
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Record Not Found', 'Data': []})

        except Exception as e:
            # log_entry = create_transaction_logNew( request, Orderdata, 0, 'StockProcessing:'+str(e), 33, 0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})