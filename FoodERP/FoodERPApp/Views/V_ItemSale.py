from django.http import JsonResponse
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
# from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, transaction
from rest_framework.parsers import JSONParser
from ..Serializer.S_Employees import *
from ..Serializer.S_Parties import *
from ..Serializer.S_ItemSale import *
from ..models import *
from ..Views.V_CommFunction import *
from django.db.models import F, Q
from SweetPOS.models import *

class ItemSaleReportView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    def post(self, request, id=0):
        Reportdata = JSONParser().parse(request)
        try:
            with transaction.atomic():
                FromDate = Reportdata['FromDate']
                ToDate = Reportdata['ToDate']
                PartyType =Reportdata['PartyType']
                Party = Reportdata['Party']
                EmployeeID = Reportdata['Employee']
                
                Invoicequery = '''SELECT T_Invoices.id, T_Invoices.InvoiceDate, SupPartyType.Name SaleMadeFrom, CustPartyType.Name SaleMadeTo, FullInvoiceNumber,Sup.Name SupplierName, M_Routes.Name RouteName, Cust.Name CustomerName, M_Group.Name GroupName, MC_SubGroup.Name SubGroupName, M_Items.Name ItemName, QtyInKg, QtyInNo, QtyInBox, Rate, BasicAmount, DiscountAmount, GSTPercentage, GSTAmount, Amount, T_Invoices.GrandTotal, RoundOffAmount, TCSAmount, T_GRNs.FullGRNNumber, TC_InvoiceItems.MRPValue, 0 MobileNo, "" CashierName FROM T_Invoices JOIN TC_InvoiceItems ON Invoice_id = T_Invoices.id JOIN M_Parties Cust ON Customer_id = Cust.id JOIN M_Parties Sup ON Party_id = Sup.id JOIN M_PartyType CustPartyType ON Cust.PartyType_id = CustPartyType.id JOIN M_PartyType SupPartyType ON Sup.PartyType_id = SupPartyType.id JOIN M_Items ON Item_id = M_Items.id left JOIN MC_ItemGroupDetails ON TC_InvoiceItems.Item_id = MC_ItemGroupDetails.Item_id AND GroupType_id = 1 JOIN M_Group ON MC_ItemGroupDetails.Group_id = M_Group.ID JOIN MC_SubGroup ON MC_ItemGroupDetails.SubGroup_id = MC_SubGroup.id JOIN MC_PartySubParty ON MC_PartySubParty.SubParty_id = Cust.id AND MC_PartySubParty.Party_id = Sup.id LEFT JOIN M_Routes ON MC_PartySubParty.Route_id = M_Routes.id LEFT JOIN TC_GRNReferences ON TC_GRNReferences.Invoice_id = T_Invoices.id LEFT JOIN T_GRNs ON GRN_id = T_GRNs.ID WHERE T_Invoices.InvoiceDate BETWEEN %s AND %s'''
                            
                SPOSInvoicequery='''SELECT A.id, A.InvoiceDate, SupPartyType.Name SaleMadeFrom, CustPartyType.Name SaleMadeTo, A.FullInvoiceNumber, Sup.Name SupplierName, M_Routes.Name RouteName, Cust.Name CustomerName, M_Group.Name GroupName, MC_SubGroup.Name SubGroupName, M_Items.Name ItemName, B.QtyInKg, B.QtyInNo, B.QtyInBox, B.Rate, B.BasicAmount, A.DiscountAmount, B.GSTPercentage, B.GSTAmount, B.Amount, A.GrandTotal, A.RoundOffAmount, A.TCSAmount, T_GRNs.FullGRNNumber, B.MRPValue, A.MobileNo , M.LoginName CashierName  FROM SweetPOS.T_SPOSInvoices A 
                                JOIN SweetPOS.TC_SPOSInvoiceItems B ON Invoice_id = A.id 
                                JOIN FoodERP.M_Parties Cust ON A.Customer = Cust.id 
                                JOIN FoodERP.M_Parties Sup ON A.Party = Sup.id 
                                JOIN FoodERP.M_PartyType CustPartyType ON Cust.PartyType_id = CustPartyType.id 
                                JOIN FoodERP.M_PartyType SupPartyType ON Sup.PartyType_id = SupPartyType.id 
                                JOIN FoodERP.M_Items ON B.Item = M_Items.id  
                                LEFT JOIN FoodERP.MC_ItemGroupDetails C ON B.Item = C.Item_id AND GroupType_id = 5 
                                JOIN FoodERP.M_Group ON C.Group_id = M_Group.ID 
                                LEFT JOIN FoodERP.MC_SubGroup ON C.SubGroup_id = MC_SubGroup.id
                                left JOIN FoodERP.MC_PartySubParty D ON D.SubParty_id = Cust.id AND D.Party_id = Sup.id
                                LEFT JOIN FoodERP.M_Routes ON D.Route_id = M_Routes.id 
                                LEFT JOIN FoodERP.TC_GRNReferences ON TC_GRNReferences.Invoice_id = A.id 
                                LEFT JOIN FoodERP.T_GRNs ON GRN_id = T_GRNs.ID
                                JOIN SweetPOS.M_SweetPOSUser M ON M.id = A.CreatedBy
                                WHERE A.InvoiceDate BETWEEN %s AND %s'''
                parameters = [FromDate,ToDate]
                if int(Party) > 0: 
                    Invoicequery += ' AND Sup.id = %s'
                    SPOSInvoicequery += ' AND Sup.id = %s'
                    parameters.append(Party)
                    
                elif int(PartyType) > 0: 
                    Invoicequery += ' AND Sup.id = %s'
                    SPOSInvoicequery += ' AND Sup.id = %s'
                    parameters.append(PartyType)
                else:
                    if int(EmployeeID) > 0:
                        EmpParties = MC_ManagementParties.objects.filter(Employee=EmployeeID).values('Party')
                        party_values = [str(record['Party']) for record in EmpParties]
                        Invoicequery += ' AND Sup.id IN %s'
                        SPOSInvoicequery += ' AND Sup.id IN %s'
                        parameters.append(party_values)
                    else:    
                        Invoicequery += ' AND Sup.id = %s'
                        SPOSInvoicequery += ' AND Sup.id = %s'

                q1 = T_Invoices.objects.raw(Invoicequery,parameters)
                q2 = T_SPOSInvoices.objects.using('sweetpos_db').raw(SPOSInvoicequery,parameters)
                combined_invoices = list(q1) + list(q2)   
                if combined_invoices:
                    ItemList = list()
                    for a in combined_invoices:
                        ItemList.append({
                                "id":a.id,
                                "InvoiceDate": a.InvoiceDate,
                                "SaleMadeFrom": a.SaleMadeFrom,
                                "SaleMadeTo":a.SaleMadeTo,
                                "FullInvoiceNumber":a.FullInvoiceNumber,
                                "SupplierName":a.SupplierName,
                                "RouteName": a.RouteName,
                                "CustomerName":a.CustomerName,
                                "GroupName":a.GroupName,
                                "SubGroupName":a.SubGroupName,
                                "ItemName":a.ItemName,
                                "QtyInKg":a.QtyInKg,
                                "QtyInNo" :a.QtyInNo,
                                "QtyInBox":a.QtyInBox,
                                "Rate":a.Rate,
                                "BasicAmount":a.BasicAmount,
                                "DiscountAmount":a.DiscountAmount,
                                "GSTPercentage":a.GSTPercentage,
                                "GSTAmount":a.GSTAmount,
                                "Amount":a.Amount,
                                "GrandTotal":a.GrandTotal,
                                "RoundOffAmount":a.RoundOffAmount,
                                "TCSAmount":a.TCSAmount,
                                "FullGRNNumber":a.FullGRNNumber,
                                "MRPValue":a.MRPValue,
                                "MobileNo": a.MobileNo,
                                "CashierName": a.CashierName
                                })
                    log_entry = create_transaction_logNew(request, Reportdata, Party, 'From:'+FromDate+','+'To:'+ToDate,281,0,FromDate,ToDate,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True,'Message':'', 'Data': ItemList})
                
                log_entry = create_transaction_logNew(request, Reportdata, Party, 'Records Not available',281,0,FromDate,ToDate,0)
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Records Not available', 'Data': []})  
        except Exception as e:
            log_entry = create_transaction_logNew(request, Reportdata, 0,'ItemSaleReport:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})      
                                            
                                                                             
                                

class ItemSaleSupplierDropdownView(CreateAPIView):

    permission_classes = (IsAuthenticated,)

    @transaction.atomic()
    def get(self, request, id=0,PartyType=0):
        try:
            with transaction.atomic():
                query = MC_ManagementParties.objects.filter(
                    Employee=id).values('Party')
                if query.exists():
                    q2 = M_Parties.objects.filter(id__in=query,PartyType=PartyType)
                    Parties_serializer = ItemSaleSupplierSerializer(q2, many=True).data
                    Partylist = list()
                    for a in Parties_serializer:
                        Partylist.append({
                            'id':  a['id'],
                            'Name':  a['Name']
                        })
                        log_entry = create_transaction_logNew(request, ItemSaleSupplierSerializer,0,'',282,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': Partylist})
                log_entry = create_transaction_logNew(request, ItemSaleSupplierSerializer,0,'Parties Not available',282,0)
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Parties Not available ', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, 0, 0,'ItemSaleSupplierDropdown:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})
        
        
class ItemSaleItemDropdownView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)

    @transaction.atomic()
    def post(self, request):
        Itemdata = JSONParser().parse(request)
        try:
            with transaction.atomic():
                Group = Itemdata['Group']
                SubGroup = Itemdata['SubGroup']
              
                if int(Group) > 0 :
                    query = M_Items.objects.raw('''SELECT M_Items.id,M_Items.Name FROM M_Items left JOIN MC_ItemGroupDetails ON MC_ItemGroupDetails.Item_id=M_Items.id and MC_ItemGroupDetails.GroupType_id=1 JOIN M_Group ON M_Group.id  = MC_ItemGroupDetails.Group_id WHERE MC_ItemGroupDetails.Group_id=%s ''',[Group])
                elif int(SubGroup) > 0:
                    query = M_Items.objects.raw('''SELECT M_Items.id, M_Items.Name FROM M_Items left JOIN MC_ItemGroupDetails on MC_ItemGroupDetails.Item_id=M_Items.id and MC_ItemGroupDetails.GroupType_id=1 JOIN MC_SubGroup ON MC_SubGroup.id  = MC_ItemGroupDetails.SubGroup_id WHERE MC_ItemGroupDetails.SubGroup_id = %s''',[SubGroup])
                else:
                    query = M_Items.objects.raw('''SELECT M_Items.id,M_Items.Name FROM M_Items''')  
                if query:
                    Item_serializer = ItemSaleItemSerializer(query, many=True).data
                    CustomPrint("aaaaa")
                    log_entry = create_transaction_logNew(request, Itemdata,0,'',283,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': Item_serializer})
                CustomPrint("bbbbbbbb")
                log_entry = create_transaction_logNew(request, Itemdata,0,'Items Not available ',283,0)
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Items Not available ', 'Data': []})
        except Exception as e:
            CustomPrint("cccc")
            log_entry = create_transaction_logNew(request, Itemdata, 0,'ItemSaleItemDropdown:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})        
        
        
        
        
        