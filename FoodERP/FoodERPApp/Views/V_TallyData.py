from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from rest_framework.parsers import JSONParser
from SweetPOS.models import *
from ..Views.V_CommFunction import *
from ..models import *
from SweetPOS.Views.V_SweetPosRoleAccess import BasicAuthenticationfunction
from rest_framework.authentication import BasicAuthentication, TokenAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from datetime import datetime



class TallyDataListView(CreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [BasicAuthentication]
    
    @transaction.atomic()
    def post(self, request):
        TallyData = JSONParser().parse(request)
        try:
            with transaction.atomic():
                 
                Mode = TallyData['Mode']  
                
                TallyDetails = []
                
                if Mode == "Purchase":
                    query=(f''' select * from  
(SELECT GRN.id ,GRN.InvoiceNumber,GRN.InvoiceDate,P.id AS PartyCode,P.Name AS PartyName,CASE AccountingGRNStatus
                        WHEN 0 THEN 'Created'
                        WHEN 1 THEN 'Canceled'
                        ELSE 'Edited'END AS Statuss,U2.LoginName AS User, 
                        GRN.RoundOffAmount RoundOff,GRN.TotalExpenses ,
                        GRN.GrandTotal
                        FROM T_GRNs GRN
						JOIN M_Users U2 ON GRN.CreatedBy = U2.id
                        JOIN M_Parties P ON GRN.Party_id = P.id
                        WHERE P.Company_id = 4 AND GRN.IsTallySave = 0 
                        AND ((IsSave=0 and AccountingGRNStatus=0) OR (IsSave=1 and AccountingGRNStatus=1) OR (IsSave=0 and AccountingGRNStatus=2))limit 200)a
left join 
(select GI.GRN_id,I.id AS ItemCode,I.Name AS ItemName,H.HSNCode,
                    GI.Rate ,GI.Quantity,U.Name AS UnitName,GI.DiscountType,GI.Discount AS DiscountPercentage,
                    GI.DiscountAmount,GI.BasicAmount AS TaxableValue,GI.CGSTPercentage,GI.CGST,GI.SGSTPercentage,GI.SGST,
                    GI.IGSTPercentage,GI.IGST,GI.GSTPercentage,GI.GSTAmount,GI.Amount AS TotalValue,0 AS TCSTaxAmount
                    
                    FROM TC_GRNItems GI  
					JOIN M_Items I ON GI.Item_id = I.id 
                    JOIN M_GSTHSNCode H ON GI.GST_id = H.id
                    JOIN MC_ItemUnits IU ON GI.Unit_id = IU.id 
                    JOIN M_Units U ON IU.UnitID_id = U.id
                    
union all
select E.GRN_id,NULL AS ItemCode,L.Name AS ItemName,
                    L.HSN AS HSNCode,NULL AS Rate,NULL AS Quantity,NULL AS UnitName,
                    NULL AS DiscountType,NULL AS DiscountPercentage, NULL AS DiscountAmount,
                    E.BasicAmount AS TaxableValue,"" CGSTPercentage,E.CGST AS CGST,
                    "" SGSTPercentage,E.SGST AS SGST,""IGSTPercentage,E.IGST AS IGST,E.GSTPercentage AS GSTPercentage,
                    0 as GSTAmount,E.Amount AS TotalValue,0 AS TCSTaxAmount
                    FROM TC_GRNExpenses E 
                    JOIN M_Ledger L ON E.Ledger_id = L.id
                    LEFT JOIN M_AccountGroupType AGT ON L.AccountGroupType_id = AGT.id  )b
                    on a.id=b.GRN_id ''')
                    tallyquery = TC_GRNItems.objects.raw(query)
                    ID = "PurchaseID"
                
                elif Mode == "Sale":
                    tallyquery = T_Invoices.objects.raw(f'''select * from                                                    
                                                             
                                                             (SELECT T_Invoices.id, T_Invoices.FullInvoiceNumber InvoiceNumber, T_Invoices.InvoiceDate, M_Parties.id AS PartyCode, M_Parties.Name AS PartyName,
                                                                M_Items.id AS ItemCode, M_Items.Name AS ItemName, M_GSTHSNCode.HSNCode, TI.Rate,
                                                                TI.Quantity,  M_Units.Name as UnitName, TI.DiscountType, TI.Discount AS DiscountPercentage,
                                                                TI.DiscountAmount, TI.BasicAmount AS TaxableValue, TI.CGSTPercentage, TI.CGST, TI.SGSTPercentage,
                                                                TI.SGST, TI.IGSTPercentage, TI.IGST, TI.GSTPercentage, TI.GSTAmount, TI.Amount AS TotalValue,
                                                                0 AS TCSTaxAmount, T_Invoices.GrandTotal, 'Created' AS Statuss, M_Users.LoginName AS User,T_Invoices.RoundOffAmount RoundOff,0 as TotalExpenses
                                                                FROM T_Invoices 
                                                                JOIN TC_InvoiceItems TI ON T_Invoices.id = TI.Invoice_id
                                                                JOIN MC_ItemUnits ON TI.Unit_id = MC_ItemUnits.id
                                                                JOIN M_Units on MC_ItemUnits.UnitID_id = M_Units.id
                                                                JOIN M_Parties ON M_Parties.id = T_Invoices.Customer_id
                                                                JOIN M_Items ON M_Items.id = TI.Item_id
                                                                JOIN M_GSTHSNCode ON M_GSTHSNCode.id = TI.GST_id
                                                                JOIN M_Users ON M_Users.id = T_Invoices.CreatedBy
                                                                WHERE M_Parties.Company_id = 4 AND T_Invoices.IsTallySave=0 
                                                             
                                                             UNION ALL 
                                                             
                                                             SELECT T_DeletedInvoices.Invoice id , T_DeletedInvoices.FullInvoiceNumber InvoiceNumber, T_DeletedInvoices.InvoiceDate, M_Parties.id AS PartyCode,
                                                                M_Parties.Name AS PartyName,
                                                                M_Items.id AS ItemCode, M_Items.Name AS ItemName, M_GSTHSNCode.HSNCode, TI.Rate,
                                                                TI.Quantity,  M_Units.Name as UnitName, TI.DiscountType, TI.Discount AS DiscountPercentage,
                                                                TI.DiscountAmount, TI.BasicAmount AS TaxableValue, TI.CGSTPercentage, TI.CGST, TI.SGSTPercentage,
                                                                TI.SGST, TI.IGSTPercentage, TI.IGST, TI.GSTPercentage, TI.GSTAmount, TI.Amount AS TotalValue,
                                                                0 AS TCSTaxAmount, T_DeletedInvoices.GrandTotal, 'Canceled' AS Statuss, M_Users.LoginName AS User,T_DeletedInvoices.RoundOffAmount RoundOff,0 as TotalExpenses
                                                                FROM T_DeletedInvoices 
                                                                JOIN TC_DeletedInvoiceItems TI ON T_DeletedInvoices.Invoice = TI.Invoice
                                                                JOIN MC_ItemUnits ON TI.Unit = MC_ItemUnits.id
                                                                JOIN M_Units on MC_ItemUnits.UnitID_id = M_Units.id
                                                                JOIN M_Parties ON M_Parties.id = T_DeletedInvoices.Customer
                                                                JOIN M_Items ON M_Items.id = TI.Item
                                                                JOIN M_GSTHSNCode ON M_GSTHSNCode.id = TI.GST
                                                                JOIN M_Users ON M_Users.id = T_DeletedInvoices.CreatedBy
                                                                WHERE M_Parties.Company_id = 4 AND T_DeletedInvoices.IsTallySave=0 )s order by id ''')
                    ID = "SaleID"
                else:
                    return JsonResponse({'StatusCode': 400, 'Status': False, 'Message': 'Invalid Mode', 'Data': []})
                
                if tallyquery:
                    for row in tallyquery:
                        InvoiceDate = row.InvoiceDate.strftime('%d-%m-%Y') if row.InvoiceDate else None
                        TallyDetails.append({
                            ID: row.id,
                            "InvoiceNumber": row.InvoiceNumber,
                            "InvoiceDate": InvoiceDate,
                            "PartyCode": row.PartyCode,
                            "PartyName": row.PartyName,
                            "ItemCode": row.ItemCode,
                            "ItemName": row.ItemName,
                            "HSNCode": row.HSNCode,
                            "MRP": row.Rate,
                            "Quantity": row.Quantity,
                            "UnitName": row.UnitName,
                            "DiscountType": row.DiscountType,
                            "DiscountPercentage": row.DiscountPercentage,
                            "DiscountAmount": row.DiscountAmount,
                            "TaxableValue": row.TaxableValue,
                            "CGSTPercentage": row.CGSTPercentage,
                            "CGST": row.CGST,
                            "SGSTPercentage": row.SGSTPercentage,
                            "SGST": row.SGST,
                            "IGSTPercentage": row.IGSTPercentage,
                            "IGST": row.IGST,
                            "GSTPercentage": row.GSTPercentage,
                            "GSTAmount": row.GSTAmount,
                            "TotalValue": row.TotalValue,
                            "TCSTaxAmount": row.TCSTaxAmount,
                            "GrandTotal": round((row.GrandTotal+row.TotalExpenses),2),
                            "RoundOff" : row.RoundOff,
                            "Status": row.Statuss,
                            "User": row.User
                        })
                    
                    log_entry = create_transaction_logNew(request, 0, 0, 'TallyDetails', 451, 0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': TallyDetails})  
            
            log_entry = create_transaction_logNew(request, 0, 0, "Data Not Available", 451, 0, 0, 0, 0)
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Data Not Available', 'Data': []}) 
        
        except Exception as e:
            log_entry = create_transaction_logNew(request, 0, 0, 'TallyData:' + str(e), 33, 0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': str(e), 'Data': []})



class UpdateIsTallySaveView(CreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [BasicAuthentication]

    @transaction.atomic
    def post(self, request, id=0):
        Data = JSONParser().parse(request)
        try:
            mode = Data.get('mode', '') 
            ids = Data.get('ids', '') 
            
            if not ids:
                    return JsonResponse({'StatusCode': 400, 'Status': False, 'Message': 'IDs not provided', 'Data': []})
            
            if mode == "Purchase":

                GRNID_list = [int(id.strip()) for id in ids.split(',') if id.strip().isdigit()]
                
                updated_count = T_GRNs.objects.filter(id__in=GRNID_list, IsTallySave=0).update(IsTallySave=1)
                
                if updated_count == 0:
                    log_entry = create_transaction_logNew(request, Data, 0, 'No TallyData updated', 452, 0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'No Data Updated', 'Data': []})
                
                log_entry = create_transaction_logNew(request, Data, 0, f'PurchaseTallyData Updated successfully IDs are: {",".join(map(str, GRNID_list))}', 452, 0)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Data Updated Successfully', 'Data': updated_count})

            elif mode == "Sale":
                
                InvoiceID_list = [int(id.strip()) for id in ids.split(',') if id.strip().isdigit()]
                
                for Billid in ids.split(','):
                    
                    aa=T_Invoices.objects.filter(id=Billid).count()
                    
                    if aa > 0:
                        
                        updated_count = T_Invoices.objects.filter(id = Billid).update(IsTallySave=1)
                    else:
                        
                        updated_count =T_DeletedInvoices.objects.filter(Invoice=Billid).update(IsTallySave=1)
                if updated_count == 0:
                    log_entry = create_transaction_logNew(request, Data, 0, 'No TallyData updated', 452, 0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'No Data Updated', 'Data': []})
                
                log_entry = create_transaction_logNew(request, Data, 0, f'SaleTallyData Updated successfully IDs are: {",".join(map(str, InvoiceID_list))}', 452, 0)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Data Updated Successfully', 'Data': updated_count})

            else:
                return JsonResponse({'StatusCode': 400, 'Status': False, 'Message': 'Invalid mode', 'Data': []})

        except Exception as e:
            log_entry = create_transaction_logNew(request, Data, 0, f'UpdateIsTallySaveView: {str(e)}', 33, 0)
            return JsonResponse({'StatusCode': 500, 'Status': False, 'Message': str(e), 'Data': []})
