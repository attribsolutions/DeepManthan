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
    authentication_classes = [BasicAuthentication]
    def post(self, request, id=0):
        POSCashierdata = JSONParser().parse(request)
        try:
            with transaction.atomic():
                user=BasicAuthenticationfunction(request)
                FromDate = POSCashierdata['FromDate']
                ToDate = POSCashierdata['ToDate']
                Party = POSCashierdata['Party']
            if user is not None:  
                WhereClause=""
                if Party:
                    WhereClause= f'AND T_SPOSInvoices.Party={Party}'
                
                CashierSummaryQuery=T_SPOSInvoices.objects.raw(f'''SELECT 1 as id ,T_SPOSInvoices.InvoiceDate,
                M_SweetPOSUser.LoginName ClientName,fooderp20240624.M_Parties.Name CashierName ,
                SUM(T_SPOSInvoices.GrandTotal)Amount from T_SPOSInvoices               
                JOIN M_SweetPOSUser ON M_SweetPOSUser.DivisionID=T_SPOSInvoices.Party
                JOIN fooderp20240624.M_Parties ON fooderp20240624.M_Parties.ID=T_SPOSInvoices.Party
                WHERE T_SPOSInvoices.InvoiceDate BETWEEN {FromDate} AND {ToDate} {WhereClause} 
                GROUP BY M_SweetPOSUser.ID''')
                
                if CashierSummaryQuery:
                    CashierDetails=list()
                    for row in CashierSummaryQuery:
                        print(row)
                        CashierDetails.append({
                            "Id":row.Id,
                            "InvoiceDate":row.InvoiceDate,
                            "ClientName":row.ClientName,
                            "CashierName":row.CashierName,
                            "Amount":row.Amount                           
                            
                        })
                    
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': CashierDetails})
                        
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Record Not Found', 'Data': []})

        except Exception as e:
            # log_entry = create_transaction_logNew( request, Orderdata, 0, 'StockProcessing:'+str(e), 33, 0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})