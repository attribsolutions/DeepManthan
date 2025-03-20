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


class TallyDataListView(CreateAPIView):
    permission_classes = ()
    authentication_classes = [BasicAuthentication]
    
    @transaction.atomic()
    def post(self, request):
        # TallyData = JSONParser().parse(request)
        try:
            with transaction.atomic():
                # FromDate = TallyData['FromDate']
                # ToDate = TallyData['ToDate']   
                
                TallyDetails = []
                
                tallyquery = TC_GRNItems.objects.raw(f'''SELECT T_GRNs.id, T_GRNs.InvoiceNumber, T_GRNs.InvoiceDate, M_Parties.id AS PartyCode, M_Parties.Name AS PartyName,
                                                        M_Items.id AS ItemCode, M_Items.Name AS ItemName, M_GSTHSNCode.HSNCode, GI.Rate,
                                                        GI.Quantity,  M_Units.Name as UnitName, GI.DiscountType, GI.Discount AS DiscountPercentage,
                                                        GI.DiscountAmount, GI.BasicAmount AS TaxableValue, GI.CGSTPercentage, GI.CGST, GI.SGSTPercentage,
                                                        GI.SGST, GI.IGSTPercentage, GI.IGST, GI.GSTPercentage, GI.GSTAmount, GI.Amount AS TotalValue,
                                                        0 AS TCSTaxAmount, T_GRNs.GrandTotal, 'create' AS Statuss, M_Users.LoginName AS User
                                                        FROM T_GRNs 
                                                        JOIN TC_GRNItems GI ON T_GRNs.id = GI.GRN_id
                                                        JOIN MC_ItemUnits ON GI.Unit_id = MC_ItemUnits.id
                                                        JOIN M_Units on MC_ItemUnits.UnitID_id = M_Units.id
                                                        JOIN M_Parties ON M_Parties.id = T_GRNs.Customer_id
                                                        JOIN M_Items ON M_Items.id = GI.Item_id
                                                        JOIN M_GSTHSNCode ON M_GSTHSNCode.id = GI.GST_id
                                                        JOIN M_Users ON M_Users.id = T_GRNs.CreatedBy
                                                        WHERE T_GRNs.GRNDate BETWEEN '2025-02-01' and '2025-03-18' 
                                                        AND IsSave = 0 AND M_Parties.Company_id = 4''')
                if tallyquery:
                    for row in tallyquery:
                        TallyDetails.append({
                            "PurchaseID": row.id,
                            "InvoiceNumber": row.InvoiceNumber,
                            "InvoiceDate": row.InvoiceDate,
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
                            "GrandTotal": row.GrandTotal,
                            "Status": row.Statuss,
                            "User": row.User
                        })

                    log_entry = create_transaction_logNew(request, 0, 0, ','.join(str(row.id) for row in tallyquery),451, 0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': TallyDetails})  
            
            log_entry = create_transaction_logNew(request, 0, 0, "Data Not Available", 451, 0, 0, 0, 0)
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Data Not Available', 'Data': []}) 
        
        except Exception as e:
            log_entry = create_transaction_logNew(request, 0, 0, 'TallyData:' + str(e), 33, 0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': str(e), 'Data': []})



class UpdateIsTallySaveView(CreateAPIView):
    permission_classes = ()
    authentication_classes = [BasicAuthentication]

    @transaction.atomic
    def post(self, request, id=0):
        GRNData = JSONParser().parse(request)
        try:
            mode = GRNData.get('mode', '') 
            ids = GRNData.get('ids', '') 
            
            if not ids:
                    return JsonResponse({'StatusCode': 400, 'Status': False, 'Message': 'IDs not provided', 'Data': []})
            
            if mode == "Purchase":

                GRNID_list = [int(id.strip()) for id in ids.split(',') if id.strip().isdigit()]
                
                updated_count = T_GRNs.objects.filter(id__in=GRNID_list, IsTallySave=0).update(IsTallySave=1)
                
                if updated_count == 0:
                    create_transaction_logNew(request, GRNData, 0, 'No TallyData updated', 452, 0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'No Data Updated', 'Data': []})
                
                create_transaction_logNew(request, GRNData, 0, f'TallyData Updated successfully IDs are: {",".join(map(str, GRNID_list))}', 452, 0)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Data Updated Successfully', 'Data': updated_count})

            elif mode == "Sale":
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'No Data Updated', 'Data': []})

            else:
                return JsonResponse({'StatusCode': 400, 'Status': False, 'Message': 'Invalid mode', 'Data': []})

        except Exception as e:
            create_transaction_logNew(request, GRNData, 0, f'UpdateIsTallySaveView: {str(e)}', 33, 0)
            return JsonResponse({'StatusCode': 500, 'Status': False, 'Message': str(e), 'Data': []})
