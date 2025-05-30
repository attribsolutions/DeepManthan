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
                Cashier = POSCashierdata['Cashier']
                
                WhereClause=""
                if int(Party) != 0  :
                    WhereClause= f'''AND SPOSIn.Party={Party}'''

                if Cashier != "" :    
                    ss=Cashier.split(',')
                    # print(ss)
                    WhereClause= f'''AND SPOSIn.CreatedBy in ({','.join(ss)} )'''
                
                CashierSummaryQuery=T_SPOSInvoices.objects.raw(f'''SELECT 1 as id , SPOSIn.InvoiceDate,
                Users.LoginName CashierName ,
                SUM(SPOSIn.GrandTotal)Amount,count(SPOSIn.id)InvoiceCount,
                sum(case when MobileNo !=''  then 1 else 0 end)Mobile_Count,SUM(CASE WHEN SPOSIn.VoucherCode IS NOT NULL AND SPOSIn.VoucherCode <> '' THEN 1 ELSE 0 END) AS VoucherCode
                from SweetPOS.T_SPOSInvoices SPOSIn
                -- JOIN SweetPOS.M_SweetPOSUser SPOSUser ON SPOSUser.id=SPOSIn.CreatedBy -- Comment For changing M_SweetPOSUser to M_Users
                JOIN FoodERP.M_Users Users ON Users.id=SPOSIn.CreatedBy
                WHERE SPOSIn.InvoiceDate BETWEEN %s AND %s and SPOSIn.IsDeleted=0 {WhereClause} 
                GROUP BY SPOSIn.InvoiceDate,Users.LoginName, Users.id
                ''',(FromDate,ToDate))                
                # print(CashierSummaryQuery)
                if CashierSummaryQuery:
                    
                    CashierDetails=list()
                    for row in CashierSummaryQuery:
                        
                        CashierDetails.append({
                            
                            "InvoiceDate":row.InvoiceDate,
                            "CashierName":row.CashierName,
                            "Amount":row.Amount, 
                            "InvoiceCount" : row.InvoiceCount,
                            "MobilenoCount" :   row.Mobile_Count,
                            "VoucherCodeCount" :row.VoucherCode                    
                            
                        })

                    log_entry = create_transaction_logNew( request, POSCashierdata, Party, '', 386, 0,FromDate,ToDate,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': CashierDetails})
                log_entry = create_transaction_logNew( request, POSCashierdata, Party, 'Data Not Found', 386, 0,FromDate,ToDate,0)           
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Record Not Found', 'Data': []})

        except Exception as e:
            log_entry = create_transaction_logNew( request, POSCashierdata, 0, 'SPOSCashierSummary:'+str(e), 33, 0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})