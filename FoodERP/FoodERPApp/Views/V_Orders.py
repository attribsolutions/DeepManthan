from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from django.db import IntegrityError, transaction
from rest_framework.parsers import JSONParser
from ..Views.V_TransactionNumberfun import GetMaxNumber, GetPrifix
from ..Views.V_CommFunction import *
from ..Serializer.S_Orders import *
from ..Serializer.S_Items import *
from ..Serializer.S_PartyItems import *
from ..Serializer.S_Bom import *
from ..Serializer.S_Challan import *
from ..Serializer.S_Invoices import *
from django.db.models import Sum
from ..models import *


class POTypeView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request):
        try:
            with transaction.atomic():
                PoTypedata = M_POType.objects.all()
                if PoTypedata.exists():
                    PoTypedata_serializer = M_POTypeserializer(
                        PoTypedata, many=True)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': PoTypedata_serializer.data})
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':  'POType Not available', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})


class OrderListFilterView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request, id=0):
        try:
            with transaction.atomic():
                Orderdata = JSONParser().parse(request)
                FromDate = Orderdata['FromDate']
                ToDate = Orderdata['ToDate']
                Customer = Orderdata['Customer']
                Supplier = Orderdata['Supplier']
                OrderType = Orderdata['OrderType']
                d = date.today()
                if(OrderType == 1): #OrderType -1 PO Order
                    if(Supplier == ''):
                       
                        query = T_Orders.objects.filter(
                            OrderDate__range=[FromDate, ToDate], Customer_id=Customer, OrderType=1)
                        queryForOpenPO = T_Orders.objects.filter(
                             POFromDate=FromDate, POToDate=ToDate, Customer_id=Customer, OrderType=1)
                        q = query.union(queryForOpenPO)
                    else:
                       
                        query = T_Orders.objects.filter(OrderDate__range=[
                                                        FromDate, ToDate], Customer_id=Customer, Supplier_id=Supplier, OrderType=1)
                        queryForOpenPO = T_Orders.objects.filter(POFromDate=FromDate, POToDate=ToDate, Customer_id=Customer, Supplier_id=Supplier, OrderType=1)
                        q = query.union(queryForOpenPO)
                else: #OrderType -2 Sales Order
                    # Pradnya :  OrderType=2 filter remove form all ORM Query coz parasnath purches order is katraj div sale order 
                    if(Customer == ''):
                       
                        query = T_Orders.objects.filter(
                            OrderDate__range=[FromDate, ToDate], Supplier_id=Supplier)
                        queryForOpenPO = T_Orders.objects.filter(POFromDate__lte=d, POToDate__gte=d, Supplier_id=Supplier)
                        q = query.union(queryForOpenPO)
                    else:
                        
                        query = T_Orders.objects.filter(OrderDate__range=[FromDate, ToDate], Customer_id=Customer, Supplier_id=Supplier )
                        queryForOpenPO = T_Orders.objects.filter(POFromDate__lte=d, POToDate__gte=d, Customer_id=Customer, Supplier_id=Supplier)
                        q = query.union(queryForOpenPO)      
                # return JsonResponse({'query': str(q.query)})
                if q :
                    Order_serializer = T_OrderSerializerSecond(q, many=True).data
                    # return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':'','Data': Order_serializer})
                    OrderListData = list()
                    for a in Order_serializer:
                        inward = 0
                        for c in a['OrderReferences']:
                            if(c['Inward'] == 1):
                                inward = 1

                        Count = TC_InvoicesReferences.objects.filter(Order = a['id']).count()
                        if Count == 0 :
                            InvoiceCreated = False
                        else:
                            InvoiceCreated = True 
                        OrderListData.append({
                            "id": a['id'],
                            "OrderDate": a['OrderDate'],
                            "FullOrderNumber": a['FullOrderNumber'],
                            "DeliveryDate": a['DeliveryDate'],
                            "CustomerID": a['Customer']['id'],
                            "Customer": a['Customer']['Name'],
                            "SupplierID": a['Supplier']['id'],
                            "Supplier": a['Supplier']['Name'],
                            "OrderAmount": a['OrderAmount'],
                            "Description": a['Description'],
                            "OrderType" : a['OrderType'],
                            "POType" : a['POType']['Name'],
                            "BillingAddress": a['BillingAddress']['Address'],
                            "ShippingAddress": a['ShippingAddress']['Address'],
                            "InvoiceCreated": InvoiceCreated,
                            "CreatedBy": a['CreatedBy'],
                            "CreatedOn": a['CreatedOn'],
                            "Inward": inward
                            })
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': OrderListData}) 
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Order Data Not available ', 'Data': []})   
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})

class OrderListFilterViewSecond(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request, id=0):
        try:
            with transaction.atomic():
                Orderdata = JSONParser().parse(request)
                FromDate = Orderdata['FromDate']
                ToDate = Orderdata['ToDate']
                Customer = Orderdata['Customer']
                Supplier = Orderdata['Supplier']
                OrderType = Orderdata['OrderType']
                
                d = date.today()
                
                if(OrderType == 3):# OrderType - 3 for GRN STP Showing Invoices for Making GRN
                    if(Supplier == ''):
                        query = T_Invoices.objects.filter(InvoiceDate__range=[FromDate, ToDate], Customer_id=Customer)
                    else:
                        query = T_Invoices.objects.filter(InvoiceDate__range=[FromDate, ToDate], Customer_id=Customer,Party=Supplier)    
                    # return JsonResponse({'query': str(Orderdata.query)})
                    if query:
                        Invoice_serializer = InvoiceSerializerSecond(query, many=True).data
                        # return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':'','Data': Order_serializer})
                        InvoiceListData = list()
                        for a in Invoice_serializer:
                            InvoiceListData.append({
                                "id": a['id'],
                                "OrderDate": a['InvoiceDate'],
                                "FullOrderNumber": a['FullInvoiceNumber'],
                                "DeliveryDate": "",
                                "CustomerID": a['Customer']['id'],
                                "Customer": a['Customer']['Name'],
                                "SupplierID": a['Party']['id'],
                                "Supplier": a['Party']['Name'],
                                "OrderAmount": a['GrandTotal'],
                                "Description": "",
                                "OrderType" : "",
                                "POType" : "",
                                "BillingAddress": "",
                                "ShippingAddress": "",
                                "CreatedBy": a['CreatedBy'],
                                "CreatedOn": a['CreatedOn'],
                                "Inward": "",
                                "Percentage" : "",
                            })
                        return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': InvoiceListData})
                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Record Not Found', 'Data': []})

                elif(OrderType == 1): #OrderType -1 PO Order
                    if(Supplier == ''):
                        query = T_Orders.objects.filter(OrderDate__range=[FromDate, ToDate], Customer_id=Customer,  OrderType=1)
                        queryForOpenPO = T_Orders.objects.filter(POFromDate__lte=d, POToDate__gte=d, Customer_id=Customer, OrderType=1)
                        q = query.union(queryForOpenPO)
                    else:
                        query = T_Orders.objects.filter(OrderDate__range=[FromDate, ToDate], Customer_id=Customer, Supplier_id=Supplier, OrderType=1)
                        queryForOpenPO = T_Orders.objects.filter(POFromDate__lte=d, POToDate__gte=d, Customer_id=Customer, Supplier_id=Supplier, OrderType=1)
                        q = query.union(queryForOpenPO)
                else: #OrderType -2 Sales Order
                    if(Customer == ''):
                        query = T_Orders.objects.filter(
                            OrderDate__range=[FromDate, ToDate], Supplier_id=Supplier, OrderType=2)
                        queryForOpenPO = T_Orders.objects.filter(POFromDate__lte=d, POToDate__gte=d, Supplier_id=Supplier, OrderType=2)
                        q = query.union(queryForOpenPO)
                    else:
                        query = T_Orders.objects.filter(OrderDate__range=[FromDate, ToDate], Customer_id=Customer, Supplier_id=Supplier, OrderType=2)
                        queryForOpenPO = T_Orders.objects.filter(POFromDate__lte=d, POToDate__gte=d, Customer_id=Customer, Supplier_id=Supplier, OrderType=2)
                        q = query.union(queryForOpenPO)      
                # return JsonResponse({'query': str(Orderdata.query)})
               
                Order_serializer = T_OrderSerializerSecond(q, many=True).data
                # return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':'','Data': Order_serializer})
                OrderListData = list()
                for a in Order_serializer:
                    inward = 0
                    for c in a['OrderReferences']:
                        if(c['Inward'] == 1):
                            inward = 1
                    OrderListData.append({
                        "id": a['id'],
                        "OrderDate": a['OrderDate'],
                        "FullOrderNumber": a['FullOrderNumber'],
                        "DeliveryDate": a['DeliveryDate'],
                        "CustomerID": a['Customer']['id'],
                        "Customer": a['Customer']['Name'],
                        "SupplierID": a['Supplier']['id'],
                        "Supplier": a['Supplier']['Name'],
                        "OrderAmount": a['OrderAmount'],
                        "Description": a['Description'],
                        "OrderType" : a['OrderType'],
                        "POType" : a['POType']['Name'],
                        "BillingAddress": a['BillingAddress']['Address'],
                        "ShippingAddress": a['ShippingAddress']['Address'],
                        "CreatedBy": a['CreatedBy'],
                        "CreatedOn": a['CreatedOn'],
                        "Inward": inward,
                        "Percentage" : "",
                        
                        })
                      
                Challanquery = T_Challan.objects.filter(Party=Customer)
                Challan_serializer = ChallanSerializerList(Challanquery, many=True).data
                for a in Challan_serializer:
                    Query=TC_GRNReferences.objects.filter(Challan_id=a['id']).select_related('GRN').values('GRN_id')
                    GRNList = list()
                    for b in Query:
                        GRNList.append(b['GRN_id'])
                        if not GRNList:
                            Percentage = 0 
                        else:
                            y=tuple(GRNList)
                            Itemsquery = TC_GRNItems.objects.filter(GRN__in=y).aggregate(Sum('Quantity'))
                            Percentage = (float(Itemsquery['Quantity__sum'])/float(a['ChallanItems'][0]['Quantity']) )*100
                    
                    OrderListData.append({
                        "id": a['id'],
                        "OrderDate": a['ChallanDate'],
                        "DeliveryDate": "",
                        "FullOrderNumber": a['FullChallanNumber'],
                        "CustomerID": a['Customer']['id'],
                        "Customer": a['Customer']['Name'],
                        "SupplierID": a['Party']['id'],
                        "Supplier": a['Party']['Name'],
                        "OrderAmount": a['GrandTotal'],
                        "Description": "",
                        "OrderType" : "",
                        "POType" : "Challan",
                        "BillingAddress": "",
                        "ShippingAddress": "",
                        "CreatedBy": a['CreatedBy'],
                        "CreatedOn": a['CreatedOn'],
                        "Inward": "",
                        "Percentage" : Percentage,
                             
                    })
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': OrderListData})    
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Order Data Not available ', 'Data': []})          
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})
        
class T_OrdersView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                Orderdata = JSONParser().parse(request)
                Division = Orderdata['Division']
                OrderType = Orderdata['OrderType']
                OrderDate = Orderdata['OrderDate']

                '''Get Max Order Number'''
                a = GetMaxNumber.GetOrderNumber(Division, OrderType, OrderDate)
                # return JsonResponse({'StatusCode': 200, 'Status': True,   'Data':[] })
                for aa in Orderdata['OrderItem']:
                    
                    BaseUnitQuantity=UnitwiseQuantityConversion(aa['Item'],aa['Quantity'],aa['Unit'],0,0,0,0).GetBaseUnitQuantity()
                    
                    aa['BaseUnitQuantity'] =  BaseUnitQuantity 
                
                Orderdata['OrderNo'] = a
                '''Get Order Prifix '''
                b = GetPrifix.GetOrderPrifix(Division)
                Orderdata['FullOrderNumber'] = b+""+str(a)
                # return JsonResponse({ 'Data': Orderdata })
                Order_serializer = T_OrderSerializer(data=Orderdata)
                if Order_serializer.is_valid():
                    Order_serializer.save()
                    OrderID=Order_serializer.data['id']
                    return JsonResponse({'StatusCode': 200, 'Status': True,  'Message': 'Order Save Successfully' ,'OrderID':OrderID, 'Data': []})
                return JsonResponse({'StatusCode': 406, 'Status': True,  'Message': Order_serializer.errors, 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})


class T_OrdersViewSecond(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    def get(self, request, id=0):
        try:
            with transaction.atomic():
                OrderQuery = T_Orders.objects.filter(id=id)
                if OrderQuery.exists():
                    OrderSerializedata = T_OrderSerializerThird(
                        OrderQuery, many=True).data
                    # return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': OrderSerializedata})
                    OrderData = list()
                    for a in OrderSerializedata:

                        OrderTermsAndCondition = list()
                        for b in a['OrderTermsAndConditions']:
                            OrderTermsAndCondition.append({
                                "id": b['TermsAndCondition']['id'],
                                "TermsAndCondition": b['TermsAndCondition']['Name'],
                            })

                        OrderItemDetails = list()
                        for b in a['OrderItem']:
                            if(b['IsDeleted'] == 0):
                                OrderItemDetails.append({
                                    "id": b['id'],
                                    "Item": b['Item']['id'],
                                    "ItemName": b['Item']['Name'],
                                    "ItemSAPCode": b['Item']['SAPItemCode'],
                                    "Quantity": b['Quantity'],
                                    "QuantityInNo": UnitwiseQuantityConversion(b['Item']['id'],b['Quantity'],b['Unit']['id'],0,0,1,0).ConvertintoSelectedUnit(),
                                    "MRP": b['MRP']['id'],
                                    "MRPValue": b['MRP']['MRP'],
                                    "Rate": b['Rate'],
                                    "Unit": b['Unit']['id'],
                                    "UnitName": b['Unit']['BaseUnitConversion'],
                                    "SAPUnitName": b['Unit']['UnitID']['SAPUnit'],
                                    "BaseUnitQuantity": b['BaseUnitQuantity'],
                                    "GST": b['GST']['id'],
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
                                    "Comment": b['Comment'],
                                })
                        inward = 0
                        for c in a['OrderReferences']:
                            if(c['Inward'] == 1):
                                inward = 1
                        Address=GetPartyAddressDetails(a['Supplier']['id']).PartyAddress()

                        OrderData.append({
                            "id": a['id'],
                            "OrderDate": a['OrderDate'],
                            "DeliveryDate": a['DeliveryDate'],
                            "OrderNo": a['OrderNo'],
                            "FullOrderNumber": a['FullOrderNumber'],
                            "POFromDate": a['POFromDate'],
                            "POToDate": a['POToDate'],
                            "POType": a['POType']['id'],
                            "POTypeName": a['POType']['Name'],
                            "OrderAmount": a['OrderAmount'],
                            "Description": a['Description'],
                            "Customer": a['Customer']['id'],
                            "CustomerSAPCode": a['Customer']['SAPPartyCode'],
                            "CustomerName": a['Customer']['Name'],
                            "Supplier": a['Supplier']['id'],
                            "SupplierSAPCode":a['Supplier']['SAPPartyCode'],
                            "SupplierName": a['Supplier']['Name'],
                            "SupplierFssai":Address[0]['FSSAINo'],
                            "BillingAddressID": a['BillingAddress']['id'],
                            "BillingAddress": a['BillingAddress']['Address'],
                            "BillingFssai": a['BillingAddress']['FSSAINo'],
                            "ShippingAddressID": a['ShippingAddress']['id'],
                            "ShippingAddress": a['ShippingAddress']['Address'],
                            "ShippingFssai": a['ShippingAddress']['FSSAINo'],
                            "Inward": inward,
                            "OrderItem": OrderItemDetails,
                            "OrderTermsAndCondition": OrderTermsAndCondition
                        })
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': OrderData[0]})
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Order Data Not available ', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})

    def put(self, request, id=0):
        try:
            with transaction.atomic():
                Orderupdatedata = JSONParser().parse(request)
                OrderupdateByID = T_Orders.objects.get(id=id)

                Orderupdate_Serializer = T_OrderSerializer(
                    OrderupdateByID, data=Orderupdatedata)
                if Orderupdate_Serializer.is_valid():
                    Orderupdate_Serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Order Updated Successfully', 'Data': []})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': Orderupdate_Serializer.errors, 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})

    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                Order_Data = T_Orders.objects.get(id=id)
                Order_Data.delete()
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Order Deleted Successfully', 'Data': []})
        except T_Orders.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Record Not available', 'Data': []})
        except IntegrityError:
            return JsonResponse({'StatusCode': 226, 'Status': True, 'Message': 'This Transaction used in another table', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})


class EditOrderView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    def post(self, request):

        try:
            with transaction.atomic():
                # DivisionID = request.data['Division']
                Party = request.data['Party']  # Order Page Supplier DropDown
                # Order Page Login Customer
                Customer = request.data['Customer']
                # Who's Rate you want 
                RateParty = request.data['RateParty']
                q1= M_Parties.objects.filter(id=Customer).values('PartyType')
                q2 = M_PartyType.objects.filter(id =q1[0]['PartyType']).values('IsRetailer','IsSCM')
                
                if (q2[0]['IsRetailer'] == 0 and q2[0]['IsSCM'] == 1): # Is Not Retailer but is SSDD Order
                    PartyItem = Customer
                else:
                    PartyItem = Party
      
                EffectiveDate = request.data['EffectiveDate']
                OrderID = request.data['OrderID']

                Itemquery = TC_OrderItems.objects.raw('''select a.Item id, a.Item_id,M_Items.Name ItemName,a.Quantity,a.MRP_id,M_MRPMaster.MRP MRPValue,a.Rate,a.Unit_id,M_Units.Name UnitName,a.BaseUnitQuantity,a.GST_id,M_GSTHSNCode.GSTPercentage,
M_GSTHSNCode.HSNCode,a.Margin_id,M_MarginMaster.Margin MarginValue,a.BasicAmount,a.GSTAmount,a.CGST,a.SGST,a.IGST,a.CGSTPercentage,a.SGSTPercentage,a.IGSTPercentage,a.Amount,a.Comment,M_Items.Sequence ,M_Items.SAPItemCode,M_Units.SAPUnit SAPUnitName
                from
(select * from (SELECT `Item_id` FROM `MC_PartyItems` WHERE `MC_PartyItems`.`Party_id` = %s)b 
left join

(SELECT `Item_id` Item,`Quantity`, `MRP_id`, `Rate`, `Unit_id`, `BaseUnitQuantity`, `GST_id`, `Margin_id`, `BasicAmount`, `GSTAmount`, `CGST`, `SGST`, `IGST`, `CGSTPercentage`, `SGSTPercentage`, `IGSTPercentage`, `Amount`,`Comment`
FROM `TC_OrderItems` WHERE (`TC_OrderItems`.`IsDeleted` = False AND `TC_OrderItems`.`Order_id` = %s))c
on b.Item_id=c.Item )a


join M_Items on M_Items.id=Item_id 
left join M_MRPMaster on M_MRPMaster.id =a.MRP_id
left join MC_ItemUnits on MC_ItemUnits.id=a.Unit_id
left join M_Units on M_Units.id=MC_ItemUnits.UnitID_id
left join M_GSTHSNCode on M_GSTHSNCode.id=a.GST_id
left join M_MarginMaster on M_MarginMaster.id=a.Margin_id group by Item_id Order By M_Items.Sequence''', ([PartyItem],[OrderID]))
               
                OrderItemSerializer = OrderEditserializer(Itemquery, many=True).data
               
                for b in OrderItemSerializer:
                    ItemID = b['Item_id']
                    GSTID = b['GST_id']
                    # print('**********************',ItemID)
            # =====================GST================================================
                    if GSTID is None:
                        Gst = GSTHsnCodeMaster(
                            ItemID, EffectiveDate).GetTodaysGstHsnCode()
                        b['GST_id'] = Gst[0]['Gstid']
                        b['GSTPercentage'] = Gst[0]['GST']
                        # print('ttttttGST',Gst[0]['GST'])
            # =====================Stock================================================

                    stockquery = O_BatchWiseLiveStock.objects.filter(
                        Item=ItemID, Party=Customer).aggregate(Qty=Sum('BaseUnitQuantity'))
                    if stockquery['Qty'] is None:
                        Stock = 0.0
                    else:
                        Stock = stockquery['Qty']
                        
            # =====================Current MRP================================================
                    TodaysMRP=MRPMaster(ItemID,0,0,EffectiveDate).GetTodaysDateMRP()
                  
                    b['MRP_id'] = TodaysMRP[0]['Mrpid']
                    b['MRPValue'] = TodaysMRP[0]['TodaysMRP']
                    # print('ttttttttttMRP',TodaysMRP[0]['TodaysMRP'])   
            # =====================Rate================================================

                    ratequery = TC_OrderItems.objects.filter(
                        Item_id=ItemID).values('Rate').order_by('-id')[:1]
                    if not ratequery:
                        r = 0.00
                    else:
                        r = ratequery[0]['Rate']

                    if b['Rate'] is None:
                        b['Rate'] = r
            # # =====================Unit================================================
            #         UnitDetails = list()
            #         ItemUnitquery = MC_ItemUnits.objects.filter(
            #             Item=ItemID, IsDeleted=0)
            #         ItemUnitqueryserialize = Mc_ItemUnitSerializerThird(
            #             ItemUnitquery, many=True).data
                    
            #         RateMcItemUnit = ""    
            #         for d in ItemUnitqueryserialize:
            #             if (d['PODefaultUnit'] == True):
            #                 RateMcItemUnit = d['id']
            #             print(0,ItemID,RateParty,0,0,d['id'])
            #             CalculatedRateusingMRPMargin=RateCalculationFunction(0,ItemID,RateParty,0,0,d['id']).RateWithGST()
            #             UnitDetails.append({
            #                 "UnitID": d['id'],
            #                 "UnitName": d['BaseUnitConversion'] ,
            #                 "BaseUnitQuantity": d['BaseUnitQuantity'],
            #                 "PODefaultUnit": d['PODefaultUnit'],
            #                 "SODefaultUnit": d['SODefaultUnit'],
            #                 "Rate" : CalculatedRateusingMRPMargin[0]["RateWithoutGST"]

            #             })
             
                   
            # =====================IsDefaultTermsAndConditions================================================

                    b.update({"StockQuantity": Stock,
                              "UnitDetails": UnitDropdown(ItemID,RateParty,0)
                              })
                    
                    bomquery = MC_BillOfMaterialItems.objects.filter(Item_id=ItemID,BOM__IsVDCItem=1).select_related('BOM')
                    if bomquery.exists():
                        b.update({"Bom": True })
                    else:
                        b.update({"Bom": False })
                            
                if OrderID != 0:
                    OrderQuery = T_Orders.objects.get(id=OrderID)
                    a = T_OrderSerializerThird(OrderQuery).data
                   
                    OrderTermsAndCondition = list()
                    for b in a['OrderTermsAndConditions']:
                        # print(b['TermsAndCondition']['IsDeleted'])
                        if b['IsDeleted'] == 0:
                            OrderTermsAndCondition.append({
                                "id": b['TermsAndCondition']['id'],
                                "TermsAndCondition": b['TermsAndCondition']['Name'],
                            })
                    inward = 0
                    for c in a['OrderReferences']:
                        if(c['Inward'] == 1):
                            inward = 1

                    OrderData = list()
                    OrderData.append({
                        "id": a['id'],
                        "OrderDate": a['OrderDate'],
                        "DeliveryDate": a['DeliveryDate'],
                        "POFromDate": a['POFromDate'],
                        "POToDate": a['POToDate'],
                        "POType": a['POType']['id'],
                        "POTypeName": a['POType']['Name'],
                        "OrderAmount": a['OrderAmount'],
                        "Description": a['Description'],
                        "Customer": a['Customer']['id'],
                        "CustomerSAPCode": a['Customer']['SAPPartyCode'],
                        "CustomerName": a['Customer']['Name'],
                        "Supplier": a['Supplier']['id'],
                        "SupplierSAPCode":a['Supplier']['SAPPartyCode'],
                        "SupplierName": a['Supplier']['Name'],
                        "BillingAddressID": a['BillingAddress']['id'],
                        "BillingAddress": a['BillingAddress']['Address'],
                        "ShippingAddressID": a['ShippingAddress']['id'],
                        "ShippingAddress": a['ShippingAddress']['Address'],
                        "Inward": inward,
                        "OrderItems": OrderItemSerializer,
                        "TermsAndConditions": OrderTermsAndCondition
                    })
                    FinalResult = OrderData[0]
                else:

                    TermsAndConditions = list()
                    TermsAndConditionsquery = M_TermsAndConditions.objects.filter(
                    IsDefault=1)
                    TermsAndConditionsSerializer = M_TermsAndConditionsSerializer(
                    TermsAndConditionsquery, many=True).data

                    for d in TermsAndConditionsSerializer:
                        TermsAndConditions.append({
                            "id": d['id'],
                            "TermsAndCondition": d['Name']
                        })

                    NewOrder = list()
                    NewOrder.append({
                        "id": "",
                        "OrderDate": "",
                        "DeliveryDate": "",
                        "POFromDate": "",
                        "POToDate": "",
                        "POType": "",
                        "POTypeName": "",
                        "OrderAmount": "",
                        "Description": "",
                        "Customer": "",
                        "CustomerName": "",
                        "Supplier": "",
                        "SupplierName": "",
                        "BillingAddressID": "",
                        "BillingAddress": "",
                        "ShippingAddressID": "",
                        "ShippingAddress": "",
                        "Inward": "",
                        "OrderItems": OrderItemSerializer,
                        "TermsAndConditions": TermsAndConditions
                    })

                    FinalResult = NewOrder[0]

                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':  '', 'Data': FinalResult})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  e, 'Data': []})
        
        
class TestOrdersView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    def get(self, request, id=0):
        try:
            with transaction.atomic():
                OrderQuery = T_Orders.objects.filter(id=id)
                if OrderQuery.exists():
                    OrderSerializedata = TestOrderSerializer(OrderQuery, many=True).data
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': OrderSerializedata })
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Order Data Not available ', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})        
