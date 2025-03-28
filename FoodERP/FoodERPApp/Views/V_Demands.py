from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
# from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, transaction
from rest_framework.parsers import JSONParser
from ..Views.V_TransactionNumberfun import GetMaxNumber, GetPrifix
from ..Serializer.S_Demands import *
from ..Serializer.S_Items import *
from ..Serializer.S_PartyItems import *
from ..Serializer.S_Bom import *
from django.db.models import Sum
from ..models import *


class InterBranchDivisionView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request, id=0):
        Divisiondata = JSONParser().parse(request)
        try:
            with transaction.atomic():
                Company = Divisiondata['Company']
                Party = Divisiondata['Party']
                query = M_Parties.objects.filter(Company=Company,IsDivision=1).filter(~Q(id=Party))
                if query:
                    party_serializer = DivisionsSerializer(query, many=True).data
                    DivisionListData = list()
                    for a in party_serializer:
                        DivisionListData.append({
                            "id": a['id'],
                            "Name": a['Name']
                        })
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': DivisionListData})
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Record Not Found', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})
    
# class InterBranchItemsView(CreateAPIView):
#     permission_classes = (IsAuthenticated,)
#     # authentication__Class = JSONWebTokenAuthentication

#     def post(self, request):
#         try:
#             with transaction.atomic():
#                 Party = request.data['Party']  # Demand Page Supplier DropDown
#                 Customer = request.data['Customer']
#                 EffectiveDate = request.data['EffectiveDate']
#                 DemandID = request.data['OrderID']
#                 RateParty = request.data['RateParty']
#                 Itemquery = TC_DemandItems.objects.raw(f'''select a.id, a.Item_id,M_Items.Name ItemName,a.Quantity,M_MRPMaster.id MRP_id,M_MRPMaster.MRP MRPValue,a.Unit_id,M_Units.Name UnitName,a.BaseUnitQuantity,a.GST_id,M_GSTHSNCode.GSTPercentage,
# M_GSTHSNCode.HSNCode,a.Margin_id,M_MarginMaster.Margin MarginValue,a.BasicAmount,a.GSTAmount,a.CGST,a.SGST,a.IGST,a.CGSTPercentage,a.SGSTPercentage,a.IGSTPercentage,a.Amount,M_Items.Sequence
# ,M_Group.ID GroupID,M_Group.Name GroupName,MC_SubGroup.id SubGroupID,MC_SubGroup.Name SubGroupName, Round(GetTodaysDateRate(a.Item_id, '{EffectiveDate}','{Party}',0,2),2) AS Rate
#                 from
# ((SELECT 0 id,`Item_id`,`Quantity`, `MRP_id`, `Rate`, `Unit_id`, `BaseUnitQuantity`, `GST_id`, `Margin_id`, `BasicAmount`, `GSTAmount`, `CGST`, `SGST`, `IGST`, `CGSTPercentage`, `SGSTPercentage`, `IGSTPercentage`, `Amount`
# FROM `TC_DemandItems` WHERE (`TC_DemandItems`.`IsDeleted` = False AND `TC_DemandItems`.`Demand_id` = %s)) 
# UNION 
# (SELECT 1 id,M_Items.id `Item_id`, NULL AS `Quantity`, NULL AS `MRP`, NULL AS `Rate`, NULL AS `Unit`, NULL AS `BaseUnitQuantity`, NULL AS `GST`, NULL AS `Margin`, NULL AS `BasicAmount`, NULL AS `GSTAmount`, NULL AS `CGST`, NULL AS `SGST`, NULL AS `IGST`, NULL AS `CGSTPercentage`, NULL AS `SGSTPercentage`, NULL AS `IGSTPercentage`, NULL AS `Amount`
# FROM `M_Items` Join MC_PartyItems a On M_Items.id = a.Item_id
# join MC_PartyItems b On M_Items.id = b.Item_id  WHERE M_Items.IsActive=1 and  a.Party_id =%s AND b.Party_id =%s))a

# join M_Items on M_Items.id=a.Item_id 
# JOIN MC_ItemGroupDetails on MC_ItemGroupDetails.item_id=a.Item_id
# JOIN M_Group on M_Group.id=MC_ItemGroupDetails.group_id
# JOIN MC_SubGroup on MC_SubGroup.id=MC_ItemGroupDetails.SubGroup_id
# left join M_MRPMaster on M_MRPMaster.Item_id =M_Items.id
# left join MC_ItemUnits on MC_ItemUnits.id=a.Unit_id
# left join M_Units on M_Units.id=MC_ItemUnits.UnitID_id
# left join M_GSTHSNCode on M_GSTHSNCode.id=a.GST_id
# left join M_MarginMaster on M_MarginMaster.id=a.Margin_id group by Item_id Order By M_Items.Sequence''', ([DemandID], [Party], [Customer]))
#                 CustomPrint(Itemquery.query)
#                 # return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  '', 'Data': str(Itemquery.query)})
#                 DemandItemSerializer = DemandEditserializer(
#                     Itemquery, many=True).data
#                 # return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  '', 'Data': OrderItemSerializer})

#                 for b in DemandItemSerializer:
#                     ItemID = b['Item_id']
#                     GSTID = b['GST_id']
#             # =====================GST================================================
#                     if GSTID is None:
#                         Gst = GSTHsnCodeMaster(
#                             ItemID, EffectiveDate).GetTodaysGstHsnCode()
#                         b['GST_id'] = Gst[0]['Gstid']
#                         b['GSTPercentage'] = Gst[0]['GST']
#             # =====================Stock================================================

#                     stockquery = O_BatchWiseLiveStock.objects.filter(
#                         Item=ItemID, Party=Customer).aggregate(Qty=Sum('BaseUnitQuantity'))
#                     if stockquery['Qty'] is None:
#                         Stock = 0.0
#                     else:
#                         Stock = stockquery['Qty']
#             # =====================Rate================================================

#                     # ratequery = TC_DemandItems.objects.filter(
#                     #     Item_id=ItemID).values('Rate').order_by('-id')[:1]
#                     # if not ratequery:
#                     #     r = 0.00
#                     # else:
#                     #     r = ratequery[0]['Rate']
#                     # ratequery= M_RateMaster.objects.raw(f'''Select 1 id, Round(GetTodaysDateRate('{ItemID}', '{EffectiveDate}','{Party}',0,2),2) AS Rate''')
#                     # CustomPrint(ratequery)                    
#                     # if not ratequery:
#                     #         r = 0.00
#                     # else:
#                     #     for a in ratequery:
#                     #         r=a.Rate    
                        
#                     # if b['Rate'] is None:
#                     #     b['Rate'] = r
#             # =====================Rate================================================
#                     # UnitDetails = list()
#                     # ItemUnitquery = MC_ItemUnits.objects.filter(
#                     #     Item=ItemID, IsDeleted=0)
#                     # ItemUnitqueryserialize = Mc_ItemUnitSerializerThird(
#                     #     ItemUnitquery, many=True).data

#                     for b in DemandItemSerializer:
                      
#                         # UnitDetails.append({
#                         #     "UnitID": d['id'],
#                         #     "UnitName": d['BaseUnitConversion'],
#                         #     "BaseUnitQuantity": d['BaseUnitQuantity'],
#                         #     "PODefaultUnit": d['PODefaultUnit'],
#                         #     "SODefaultUnit": d['SODefaultUnit'],

#                         # })
#             # =====================IsDefaultTermsAndConditions================================================

#                     # b.update({"StockQuantity": Stock,
#                     #           "UnitDetails": UnitDetails
#                     #           })
#                         b.update({  #"StockQuantity": Stock,
#                               "UnitDetails": UnitDropdown(ItemID, RateParty, 0)
#                               })

#                 if DemandID != 0:
#                     DemandQuery = T_Demands.objects.get(id=DemandID)
#                     a = TC_DemandSerializerThird(DemandQuery).data

#                     DemandData = list()
#                     DemandData.append({
#                         "id": a['id'],
#                         "OrderDate": a['DemandDate'],
#                         "OrderNo": a['DemandNo'],
#                         "FullOrderNumber": a['FullDemandNumber'],
#                         "OrderAmount": a['DemandAmount'],
#                         "Comment": a['Comment'],
#                         "Customer": a['Customer']['id'],
#                         "CustomerName": a['Customer']['Name'],
#                         "Supplier": a['Supplier']['id'],
#                         "SupplierName": a['Supplier']['Name'],
#                         "BillingAddressID": "",
#                         "BillingAddress": "",
#                         "ShippingAddressID": "",
#                         "ShippingAddress": "",
#                         "MaterialIssue":a['MaterialIssue'],
#                         "DeliveryDate": "",
#                         "POFromDate": "",
#                         "POToDate": "",
#                         "POType": "",
#                         "POTypeName": "",
#                         "Description": "",
#                         "Inward": "",
#                         "TermsAndConditions": [],
#                         "OrderItems": DemandItemSerializer,
                        
#                     })
#                     FinalResult = DemandData[0]
#                 else:

#                     NewDemand = list()
#                     NewDemand.append({
#                         "id": "",
#                         "OrderDate": "",
#                         "OrderNo":"",
#                         "FullOrderNumber":"",
#                         "OrderAmount": "",
#                         "Comment": "",
#                         "Customer": "",
#                         "CustomerName": "",
#                         "Supplier": "",
#                         "SupplierName": "",
#                         "BillingAddressID": "",
#                         "BillingAddress": "",
#                         "ShippingAddressID": "",
#                         "ShippingAddress": "",
#                         "MaterialIssue":"",
#                         "DeliveryDate": "",
#                         "POFromDate": "",
#                         "POToDate": "",
#                         "POType": "",
#                         "POTypeName": "",
#                         "Description": "",
#                         "Inward": "",
#                         "TermsAndConditions": [],
#                         "OrderItems": DemandItemSerializer,
#                     })

#                     FinalResult = NewDemand[0]

#                 return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':  '', 'Data': FinalResult})
#         except Exception as e:
#             return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})    
    
    

class DemandListFilterView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request, id=0):
        Demanddata = JSONParser().parse(request)
        try:
            with transaction.atomic():
                FromDate = Demanddata['FromDate']
                ToDate = Demanddata['ToDate']
                Customer = Demanddata['Customer'] # Customer Compansary
                Supplier = Demanddata['Supplier']
                IBType = Demanddata['IBType']
                if (IBType == "IBSO" ): # InterBranch Sales Order 
                    if(Supplier == ''):
                        if(FromDate=="" and ToDate=="" ):
                            query = T_Demands.objects.filter(Supplier_id=Customer)
                        else:
                            query = T_Demands.objects.filter(DemandDate__range=[FromDate, ToDate],Supplier_id=Customer)                            
                    else:
                        if(FromDate=="" and ToDate=="" ):
                            query = T_Demands.objects.filter(Customer_id=Supplier, Supplier_id=Customer)  
                        else:
                            query = T_Demands.objects.filter(DemandDate__range=[FromDate, ToDate], Customer_id=Supplier, Supplier_id=Customer)  
                            
                elif(IBType == "IBPO"):
                    if(Supplier == ''): # InterBranch Purchase Order
                        query = T_Demands.objects.filter(DemandDate__range=[FromDate, ToDate],Customer_id=Customer)
                    else:
                        query = T_Demands.objects.filter(DemandDate__range=[FromDate, ToDate], Customer_id=Customer, Supplier_id=Supplier)
                else:
                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Record Not Found', 'Data': []})
                              
                if query:
                    Demand_serializer = T_DemandSerializerSecond(query, many=True).data
                    # return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':'','Data': Demand_serializer})
                    DemandListData = list()
                    for a in Demand_serializer:
                       
                        Count = TC_ChallanReferences.objects.filter(
                                Demands=a['id']).count()
                        if Count == 0:
                            InvoiceCreated = False
                        else:
                            InvoiceCreated = True
                        
                        DemandListData.append({
                            "id": a['id'],
                            "OrderDate": a['DemandDate'],
                            "DeliveryDate": a['DemandDate'],
                            "Description": a['Comment'],
                            "FullOrderNumber": a['FullDemandNumber'],
                            "CustomerID": a['Customer']['id'],
                            "Customer": a['Customer']['Name'],
                            "SupplierID": a['Supplier']['id'],
                            "Supplier": a['Supplier']['Name'],
                            "OrderAmount": a['DemandAmount'],
                            "InvoiceCreated": InvoiceCreated,
                            # "BillingAddress": a['BillingAddress']['Address'],
                            # "ShippingAddress": a['ShippingAddress']['Address'],
                            "CreatedBy": a['CreatedBy'],
                            "CreatedOn": a['CreatedOn'],
                         
                        })
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': DemandListData})
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Record Not Found', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})


class DemandView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request):
        Demanddata = JSONParser().parse(request)
        try:
            with transaction.atomic():
                Division = Demanddata['Division']
                Customer = Demanddata['Customer']
                DemandDate = Demanddata['DemandDate']

                '''Get Max Demand Number'''
                a = GetMaxNumber.GetDemandNumber(Division, Customer, DemandDate)
                # return JsonResponse({'StatusCode': 200, 'Status': a })
                for aa in Demanddata['DemandItem']:
                    BaseUnitQuantity=UnitwiseQuantityConversion(aa['Item'],aa['Quantity'],aa['Unit'],0,0,0,1).GetBaseUnitQuantity()
                    aa['BaseUnitQuantity'] =  BaseUnitQuantity 
                
                Demanddata['DemandNo'] = a
                '''Get Demand Prifix '''
                b = GetPrifix.GetDemandPrifix(Division)
                Demanddata['FullDemandNumber'] = b+""+str(a)
               
                Demand_serializer = T_DemandSerializer(data=Demanddata)
                if Demand_serializer.is_valid():
                    Demand_serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True,  'Message': 'IB Purchase Order Save Successfully', 'Data': []})
                return JsonResponse({'StatusCode': 406, 'Status': True,  'Message': Demand_serializer.errors, 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})


class DemandViewSecond(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication   
    
    
    def get(self, request, id=0):
        try:
            with transaction.atomic():
                OrderQuery = T_Demands.objects.filter(id=id)
                CustomPrint(OrderQuery.query)
                if OrderQuery.exists():
                    # CustomPrint("Shr")
                    OrderSerializedata = TC_DemandSerializerThird(OrderQuery, many=True).data
                    # return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': OrderSerializedata})
                    # CustomPrint(OrderSerializedata)
                    OrderData = list()
                    for a in OrderSerializedata:
                        # CustomPrint(a)
                        # OrderTermsAndCondition = list()
                        # for b in a['OrderTermsAndConditions']:
                        #     OrderTermsAndCondition.append({
                        #         "id": b['TermsAndCondition']['id'],
                        #         "TermsAndCondition": b['TermsAndCondition']['Name'],
                        #     })

                        OrderItemDetails = list()
                        for b in a['DemandItem']:
                            # CustomPrint(a['OrderItem'])
                            if(b['IsDeleted'] == 0):
                                
                                aaaa = UnitwiseQuantityConversion(
                                    b['Item']['id'], b['Quantity'], b['Unit']['id'], 0, 0, 0, 1).GetConvertingBaseUnitQtyBaseUnitName()
                                
                                if (aaaa == b['Unit']['UnitID']['Name']):
                                    bb=''
                                else:
                                    bb=aaaa
                                
                                OrderItemDetails.append({
                                    "id": b['id'],
                                    "Item": b['Item']['id'],
                                    "ItemName": b['Item']['Name'],
                                    "ItemSAPCode":"",
                                    "Quantity": b['Quantity'],
                                    "QuantityInNo": UnitwiseQuantityConversion(b['Item']['id'], b['Quantity'], b['Unit']['id'], 0, 0, 1, 1).ConvertintoSelectedUnit(),
                                    "MRP": b['MRP']['id'],
                                    "MRPValue": b['MRP']['MRP'],
                                    "Rate": b['Rate'],
                                    "Unit": b['Unit']['id'],
                                    "PrimaryUnitName":b['Unit']['UnitID']['Name'],
                                    "UnitName": bb,
                                    "SAPUnitName": "",
                                    "BaseUnitQuantity": b['BaseUnitQuantity'],
                                    "GST":  b['GST']['id'],
                                    "GSTPercentage": b['GST']['GSTPercentage'],
                                    "HSNCode": b['GST']['HSNCode'],
                                    "Margin": b['Margin']['id'],
                                    "MarginValue": b['Margin']['Margin'],
                                    "BasicAmount": b['BasicAmount'],
                                    "GSTAmount": b['GSTAmount'],
                                    "CGST": b['CGST'],
                                    "SGST": b['SGST'],
                                    "IGST": b['IGST'],
                                    "CGSTPercentage": b['CGSTPercentage'],
                                    "SGSTPercentage": b['SGSTPercentage'],
                                    "IGSTPercentage": b['IGSTPercentage'],
                                    "Amount": b['Amount'],
                                    "DiscountType":"",
                                    "Discount":"",
                                    "DiscountAmount":"",
                                    "Comment": "",
                                })
                                CustomPrint(OrderItemDetails)
                        # inward = 0
                        # for c in a['OrderReferences']:
                        #     if(c['Inward'] == 1):
                        #         inward = 1
                                Address = GetPartyAddressDetails(
                                    a['Supplier']['id']).PartyAddress()
                                OrderData.append({
                                    "id": a['id'],
                                    "OrderDate": a['DemandDate'],
                                    "DeliveryDate": "",
                                    "OrderNo": a['DemandNo'],
                                    "FullOrderNumber": a['FullDemandNumber'],
                                    "POFromDate": "",
                                    "POToDate": "",
                                    "POType": "",
                                    "POTypeName": "",
                                    "OrderAmount": a['DemandAmount'],
                                    "Description": "",
                                    "Customer": a['Customer']['id'],
                                    "CustomerSAPCode": a['Customer']['SAPPartyCode'],
                                    "CustomerName": a['Customer']['Name'],
                                    "CustomerGSTIN":a['Customer']['GSTIN'],
                                    "Supplier": a['Supplier']['id'],
                                    "SupplierSAPCode": a['Supplier']['SAPPartyCode'],
                                    "SupplierName": a['Supplier']['Name'],
                                    "SupplierGSTIN":a['Supplier']['GSTIN'],
                                    "SupplierFssai": Address[0]['FSSAINo'],
                                    "SupplierAddress": Address[0]['Address'],
                                    "SupplierPIN": Address[0]['Pin'],
                                    "BillingAddressID": a['BillingAddress']['id'],
                                    "BillingAddress": a['BillingAddress']['Address'],
                                    "BillingFssai": a['BillingAddress']['FSSAINo'],
                                    "ShippingAddressID": a['ShippingAddress']['id'],
                                    "ShippingAddress": a['ShippingAddress']['Address'],
                                    "ShippingFssai": a['ShippingAddress']['FSSAINo'],
                                    "Inward": "",
                                    "CreatedOn":a['CreatedOn'],
                                    "OrderItem": OrderItemDetails,
                                    # "OrderTermsAndCondition": [],
                                })
                                CustomPrint(OrderData)
                    log_entry = create_transaction_logNew(request, {'OrderID':id}, a['Supplier']['id'],'DemandDate:'+a['DemandDate']+','+'Supplier:'+str(a['Supplier']['id']),62,id,"","",a['Customer']['id'])
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': OrderData})
                log_entry = create_transaction_logNew(request, {'OrderID':id}, a['Supplier']['id'], 'Order Not Found',62,0,0,0,a['Customer']['id'])
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Order Data Not available ', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, 0, 0,'SingleOrder:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})

    
    
         
    def put(self, request, id=0):
        Demandupdatedata = JSONParser().parse(request)
        try:
            with transaction.atomic():
                DemandupdateByID = T_Demands.objects.get(id=id)
                Demandupdate_Serializer = T_DemandSerializer(
                    DemandupdateByID, data=Demandupdatedata)
                if Demandupdate_Serializer.is_valid():
                    Demandupdate_Serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'IB Purchase Order Updated Successfully', 'Data': []})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': Demandupdate_Serializer.errors, 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})    
        
        
    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                Demand_Data = T_Demands.objects.get(id=id)
                Demand_Data.delete()
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'IB Purchase Order Deleted Successfully', 'Data': []})
        except T_Demands.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Record Not available', 'Data': []})
        except IntegrityError:
            return JsonResponse({'StatusCode': 226, 'Status': True, 'Message': 'This Transaction used in another table', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})
