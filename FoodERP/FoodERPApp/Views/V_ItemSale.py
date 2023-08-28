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
from django.db.models import F, Q

class ItemSaleReportView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    def post(self, request, id=0):
        try:
            with transaction.atomic():
                Reportdata = JSONParser().parse(request)
                FromDate = Reportdata['FromDate']
                ToDate = Reportdata['ToDate']
                PartyType =Reportdata['PartyType']
                Party = Reportdata['Party']
                if int(Party) > 0:
                    query = T_Invoices.objects.raw('''SELECT T_Invoices.id, InvoiceDate, SupPartyType.Name SaleMadeFrom, CustPartyType.Name SaleMadeTo, FullInvoiceNumber,Sup.Name SupplierName, M_Routes.Name RouteName, Cust.Name CustomerName, M_Group.Name GroupName, MC_SubGroup.Name SubGroupName, M_Items.Name ItemName, QtyInKg, QtyInNo, QtyInBox, Rate, BasicAmount, DiscountAmount, GSTPercentage, GSTAmount, Amount, T_Invoices.GrandTotal, RoundOffAmount, TCSAmount, T_GRNs.FullGRNNumber FROM T_Invoices JOIN TC_InvoiceItems ON Invoice_id = T_Invoices.id JOIN M_Parties Cust ON Customer_id = Cust.id JOIN M_Parties Sup ON Party_id = Sup.id JOIN M_PartyType CustPartyType ON Cust.PartyType_id = CustPartyType.id JOIN M_PartyType SupPartyType ON Sup.PartyType_id = SupPartyType.id JOIN M_Items ON Item_id = M_Items.id JOIN MC_ItemGroupDetails ON TC_InvoiceItems.Item_id = MC_ItemGroupDetails.Item_id AND GroupType_id = 1 JOIN M_Group ON MC_ItemGroupDetails.Group_id = M_Group.ID JOIN MC_SubGroup ON MC_ItemGroupDetails.SubGroup_id = MC_SubGroup.id JOIN MC_PartySubParty ON MC_PartySubParty.SubParty_id = Cust.id AND MC_PartySubParty.Party_id = Sup.id LEFT JOIN M_Routes ON MC_PartySubParty.Route_id = M_Routes.id LEFT JOIN TC_GRNReferences ON TC_GRNReferences.Invoice_id = T_Invoices.id LEFT JOIN T_GRNs ON GRN_id = T_GRNs.ID WHERE T_Invoices.InvoiceDate BETWEEN %s AND %s AND Sup.id=%s ''',[FromDate,ToDate,Party])
                elif int(PartyType) > 0:
                    query = T_Invoices.objects.raw('''SELECT T_Invoices.id, InvoiceDate, SupPartyType.Name SaleMadeFrom, CustPartyType.Name SaleMadeTo, FullInvoiceNumber,Sup.Name SupplierName, M_Routes.Name RouteName, Cust.Name CustomerName, M_Group.Name GroupName, MC_SubGroup.Name SubGroupName, M_Items.Name ItemName, QtyInKg, QtyInNo, QtyInBox, Rate, BasicAmount, DiscountAmount, GSTPercentage, GSTAmount, Amount, T_Invoices.GrandTotal, RoundOffAmount, TCSAmount, T_GRNs.FullGRNNumber FROM T_Invoices JOIN TC_InvoiceItems ON Invoice_id = T_Invoices.id JOIN M_Parties Cust ON Customer_id = Cust.id JOIN M_Parties Sup ON Party_id = Sup.id JOIN M_PartyType CustPartyType ON Cust.PartyType_id = CustPartyType.id JOIN M_PartyType SupPartyType ON Sup.PartyType_id = SupPartyType.id AND SupPartyType.id=%s JOIN M_Items ON Item_id = M_Items.id JOIN MC_ItemGroupDetails ON TC_InvoiceItems.Item_id = MC_ItemGroupDetails.Item_id AND GroupType_id = 1 JOIN M_Group ON MC_ItemGroupDetails.Group_id = M_Group.ID JOIN MC_SubGroup ON MC_ItemGroupDetails.SubGroup_id = MC_SubGroup.id JOIN MC_PartySubParty ON MC_PartySubParty.SubParty_id = Cust.id AND MC_PartySubParty.Party_id = Sup.id LEFT JOIN M_Routes ON MC_PartySubParty.Route_id = M_Routes.id LEFT JOIN TC_GRNReferences ON TC_GRNReferences.Invoice_id = T_Invoices.id LEFT JOIN T_GRNs ON GRN_id = T_GRNs.ID WHERE T_Invoices.InvoiceDate BETWEEN %s AND %s  ''',[PartyType,FromDate,ToDate])
                else:
                    query = T_Invoices.objects.raw('''SELECT T_Invoices.id, InvoiceDate, SupPartyType.Name SaleMadeFrom, CustPartyType.Name SaleMadeTo, FullInvoiceNumber,Sup.Name SupplierName, M_Routes.Name RouteName, Cust.Name CustomerName, M_Group.Name GroupName, MC_SubGroup.Name SubGroupName, M_Items.Name ItemName, QtyInKg, QtyInNo, QtyInBox, Rate, BasicAmount, DiscountAmount, GSTPercentage, GSTAmount, Amount, T_Invoices.GrandTotal, RoundOffAmount, TCSAmount, T_GRNs.FullGRNNumber FROM T_Invoices JOIN TC_InvoiceItems ON Invoice_id = T_Invoices.id JOIN M_Parties Cust ON Customer_id = Cust.id JOIN M_Parties Sup ON Party_id = Sup.id JOIN M_PartyType CustPartyType ON Cust.PartyType_id = CustPartyType.id JOIN M_PartyType SupPartyType ON Sup.PartyType_id = SupPartyType.id JOIN M_Items ON Item_id = M_Items.id JOIN MC_ItemGroupDetails ON TC_InvoiceItems.Item_id = MC_ItemGroupDetails.Item_id AND GroupType_id = 1 JOIN M_Group ON MC_ItemGroupDetails.Group_id = M_Group.ID JOIN MC_SubGroup ON MC_ItemGroupDetails.SubGroup_id = MC_SubGroup.id JOIN MC_PartySubParty ON MC_PartySubParty.SubParty_id = Cust.id AND MC_PartySubParty.Party_id = Sup.id LEFT JOIN M_Routes ON MC_PartySubParty.Route_id = M_Routes.id LEFT JOIN TC_GRNReferences ON TC_GRNReferences.Invoice_id = T_Invoices.id LEFT JOIN T_GRNs ON GRN_id = T_GRNs.ID WHERE T_Invoices.InvoiceDate BETWEEN %s AND %s  ''',[FromDate,ToDate])

                if query:
                    ItemSaleSerializer=ItemSaleReportSerializer(query, many=True).data
                    return JsonResponse({'StatusCode': 200, 'Status': True,'Message':'', 'Data': ItemSaleSerializer})
                else:
                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Records Not available ', 'Data': []})  
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})      
                                            
                                                                             
                                

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
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': Partylist})
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Parties Not available ', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})
        
        
class ItemSaleItemDropdownView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)

    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                Itemdata = JSONParser().parse(request)
                Group = Itemdata['Group']
                SubGroup = Itemdata['SubGroup']
              
                if int(Group) > 0 :
                    query = M_Items.objects.raw('''SELECT M_Items.id,M_Items.Name FROM M_Items JOIN MC_ItemGroupDetails ON MC_ItemGroupDetails.Item_id=M_Items.id JOIN M_Group ON M_Group.id  = MC_ItemGroupDetails.Group_id WHERE MC_ItemGroupDetails.Group_id=%s ''',[Group])
                elif int(SubGroup) > 0:
                    query = M_Items.objects.raw('''SELECT M_Items.id, M_Items.Name FROM M_Items JOIN MC_ItemGroupDetails on MC_ItemGroupDetails.Item_id=M_Items.id JOIN MC_SubGroup ON MC_SubGroup.id  = MC_ItemGroupDetails.SubGroup_id WHERE MC_ItemGroupDetails.SubGroup_id = %s''',[SubGroup])
                else:
                    query = M_Items.objects.raw('''SELECT M_Items.id,M_Items.Name FROM M_Items''')  
                if query:
                    Item_serializer = ItemSaleItemSerializer(query, many=True).data
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': Item_serializer})
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Items Not available ', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})        
        
        
        
        
        