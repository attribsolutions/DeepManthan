from typing import Concatenate
from django.http import JsonResponse
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, connection, transaction
from rest_framework.parsers import JSONParser
from ..Views.V_TransactionNumberfun import GetMaxNumber, GetPrifix
from ..Serializer.S_Orders import *
from ..Serializer.S_Items import *
from ..Serializer.S_PartyItems import *
from ..Serializer.S_Bom import *
from django.db.models import Sum
from ..models import *


class POTypeView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    authentication__Class = JSONWebTokenAuthentication

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
    authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request, id=0):
        try:
            with transaction.atomic():
                Orderdata = JSONParser().parse(request)
                FromDate = Orderdata['FromDate']
                ToDate = Orderdata['ToDate']
                Customer = Orderdata['Customer']
                Supplier = Orderdata['Supplier']
                d = date.today()
                if(Supplier == ''):
                    query = T_Orders.objects.filter(
                        OrderDate__range=[FromDate, ToDate], Customer_id=Customer, IsOpenPO=0)
                    queryForOpenPO = T_Orders.objects.filter(
                        IsOpenPO=1, POFromDate__lte=d, POToDate__gte=d, Customer_id=Customer)
                    q = query.union(queryForOpenPO)
                else:
                    query = T_Orders.objects.filter(OrderDate__range=[
                                                    FromDate, ToDate], Customer_id=Customer, Supplier_id=Supplier, IsOpenPO=0)
                    queryForOpenPO = T_Orders.objects.filter(
                        IsOpenPO=1, POFromDate__lte=d, POToDate__gte=d, Customer_id=Customer, Supplier_id=Supplier)
                    q = query.union(queryForOpenPO)
                # return JsonResponse({'query': str(Orderdata.query)})
                if q:
                    Order_serializer = T_OrderSerializerSecond(
                        q, many=True).data
                    # return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':'','Data': Order_serializer})
                    OrderListData = list()
                    for a in Order_serializer:
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
                            "BillingAddress": a['BillingAddress']['Address'],
                            "ShippingAddress": a['ShippingAddress']['Address'],
                            "CreatedBy": a['CreatedBy'],
                            "CreatedOn": a['CreatedOn'],
                            "Inward": a['Inward']

                        })
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': OrderListData})
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Record Not Found', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})


class T_OrdersView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    authentication__Class = JSONWebTokenAuthentication

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
                print(a)
                Orderdata['OrderNo'] = a
                '''Get Order Prifix '''
                b = GetPrifix.GetOrderPrifix(Division)
                Orderdata['FullOrderNumber'] = b+""+str(a)
                # return JsonResponse({ 'Data': Orderdata })
                Order_serializer = T_OrderSerializer(data=Orderdata)
                if Order_serializer.is_valid():
                    Order_serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True,  'Message': 'Order Save Successfully', 'Data': []})
                return JsonResponse({'StatusCode': 406, 'Status': True,  'Message': Order_serializer.errors, 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})


class T_OrdersViewSecond(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    authentication__Class = JSONWebTokenAuthentication

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
                                    "Quantity": b['Quantity'],
                                    "MRP": b['MRP']['id'],
                                    "MRPValue": b['MRP']['MRP'],
                                    "Rate": b['Rate'],
                                    "Unit": b['Unit']['id'],
                                    "UnitName": b['Unit']['UnitID']['Name'],
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
                            "CustomerName": a['Customer']['Name'],
                            "Supplier": a['Supplier']['id'],
                            "SupplierName": a['Supplier']['Name'],
                            "BillingAddressID": a['BillingAddress']['id'],
                            "BillingAddress": a['BillingAddress']['Address'],
                            "ShippingAddressID": a['ShippingAddress']['id'],
                            "ShippingAddress": a['ShippingAddress']['Address'],
                            "Inward": a['Inward'],
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
                    return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': Orderupdate_Serializer.errors, 'Data': []})
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
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'T_Orders used in another tbale', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})


class GetItemsForOrderView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    authentication__Class = JSONWebTokenAuthentication

    def post(self, request):
        try:
            with transaction.atomic():
                # DivisionID = request.data['Division']
                Party = request.data['Party']  # Order Page Party Id
                EffectiveDate = request.data['EffectiveDate']
                query = MC_PartyItems.objects.filter(Party_id=Party)
                # return JsonResponse({ 'query': str(query.query)})
                if not query:
                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':  'Items Not available', 'Data': []})
                else:
                    Items_Serializer = MC_PartyItemSerializerSecond(
                        query, many=True).data
                    ItemList = list()
                    for a in Items_Serializer:
                        ItemID = a['Item']['id']
                        stockquery = O_BatchWiseLiveStock.objects.filter(
                            Item_id=ItemID).aggregate(Qty=Sum('BaseUnitQuantity'))
                        if stockquery['Qty'] is None:
                            Stock = 0.0
                        else:
                            Stock = stockquery['Qty']
                        ratequery = TC_OrderItems.objects.filter(
                            Item_id=ItemID).values('Rate').order_by('-id')[:1]
                        # print(ratequery)
                        if not ratequery:
                            r = 0.00
                        else:
                            r = ratequery[0]['Rate']
                        Gst = GSTHsnCodeMaster(
                            ItemID, EffectiveDate).GetTodaysGstHsnCode()
                        UnitDetails = list()
                        for d in a['Item']['ItemUnitDetails']:
                            if d['IsDeleted'] == 0:
                                ItemUnitquery = MC_ItemUnits.objects.filter(Item=ItemID, IsBase=1).values('UnitID')
                                qwer=ItemUnitquery[0]['UnitID']
                                BaseUnitNamequery = M_Units.objects.filter(id=qwer).values('Name')
                                q=BaseUnitNamequery[0]['Name']
                                baseunitconcat=" ("+d['BaseUnitQuantity']+" "+q+")"
                                UnitDetails.append({
                                    # Below UnitID is MC_ItemUnits Primary id
                                    "UnitID": d['id'],
                                    # "UnitID": d['UnitID']['id'],
                                    "UnitName": d['UnitID']['Name']+ baseunitconcat,
                                    "BaseUnitQuantity": d['BaseUnitQuantity'],
                                })

                        ItemList.append({
                            "id": a['Item']['id'],
                            "Name": a['Item']['Name'],
                            "Gstid": Gst[0]['Gstid'],
                            "StockQuantity": Stock,
                            "Rate": r,
                            "GSTPercentage": Gst[0]['GST'],
                            "UnitDetails": UnitDetails
                        })
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': ItemList})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})


class EditOrderView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    authentication__Class = JSONWebTokenAuthentication

    def post(self, request):

        try:
            with transaction.atomic():
                # DivisionID = request.data['Division']
                Party = request.data['Party']  # Order Page Supplier DropDown
                # Order Page Login Customer
                Customer = request.data['Customer']
                EffectiveDate = request.data['EffectiveDate']
                OrderID = request.data['OrderID']
                
                Itemquery = TC_OrderItems.objects.raw('''select a.id, a.Item_id,M_Items.Name ItemName,a.Quantity,a.MRP_id,m_mrpmaster.MRP MRPValue,a.Rate,a.Unit_id,m_units.Name UnitName,a.BaseUnitQuantity,a.GST_id,m_gsthsncode.GSTPercentage,
m_gsthsncode.HSNCode,a.Margin_id,m_marginmaster.Margin MarginValue,a.BasicAmount,a.GSTAmount,a.CGST,a.SGST,a.IGST,a.CGSTPercentage,a.SGSTPercentage,a.IGSTPercentage,a.Amount,a.Comment,M_Items.Sequence 
                from
((SELECT 0 id,`Item_id`,`Quantity`, `MRP_id`, `Rate`, `Unit_id`, `BaseUnitQuantity`, `GST_id`, `Margin_id`, `BasicAmount`, `GSTAmount`, `CGST`, `SGST`, `IGST`, `CGSTPercentage`, `SGSTPercentage`, `IGSTPercentage`, `Amount`,`Comment`
FROM `TC_OrderItems` WHERE (`TC_OrderItems`.`IsDeleted` = False AND `TC_OrderItems`.`Order_id` = %s)) 
UNION 
(SELECT 1 id,`Item_id`, NULL AS `Quantity`, NULL AS `MRP`, NULL AS `Rate`, NULL AS `Unit`, NULL AS `BaseUnitQuantity`, NULL AS `GST`, NULL AS `Margin`, NULL AS `BasicAmount`, NULL AS `GSTAmount`, NULL AS `CGST`, NULL AS `SGST`, NULL AS `IGST`, NULL AS `CGSTPercentage`, NULL AS `SGSTPercentage`, NULL AS `IGSTPercentage`, NULL AS `Amount`,NULL AS `Comment` 
FROM `MC_PartyItems` WHERE `MC_PartyItems`.`Party_id` = %s))a
join m_items on m_items.id=a.Item_id 
left join m_mrpmaster on m_mrpmaster.id =a.MRP_id
left join mc_itemunits on mc_itemunits.id=a.Unit_id
left join m_units on m_units.id=mc_itemunits.UnitID_id
left join m_gsthsncode on m_gsthsncode.id=a.GST_id
left join m_marginmaster on m_marginmaster.id=a.Margin_id group by Item_id Order By m_items.Sequence''', ([OrderID], [Party]))

                OrderItemSerializer = OrderEditserializer(
                    Itemquery, many=True).data
                # return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  '', 'Data': OrderItemSerializer})

                for b in OrderItemSerializer:
                    ItemID = b['Item_id']
                    GSTID = b['GST_id']
            # =====================GST================================================
                    if GSTID is None:
                        Gst = GSTHsnCodeMaster(
                            ItemID, EffectiveDate).GetTodaysGstHsnCode()
                        b['GST_id'] = Gst[0]['Gstid']
                        b['GSTPercentage'] = Gst[0]['GST']
            # =====================Stock================================================

                    stockquery = O_BatchWiseLiveStock.objects.filter(
                        Item=ItemID, Party=Customer).aggregate(Qty=Sum('BaseUnitQuantity'))
                    if stockquery['Qty'] is None:
                        Stock = 0.0
                    else:
                        Stock = stockquery['Qty']
            # =====================Rate================================================

                    ratequery = TC_OrderItems.objects.filter(
                        Item_id=ItemID).values('Rate').order_by('-id')[:1]
                    if not ratequery:
                        r = 0.00
                    else:
                        r = ratequery[0]['Rate']

                    if b['Rate'] is None:
                       b['Rate'] = r
            # =====================Rate================================================
                    UnitDetails = list()
                    ItemUnitquery = MC_ItemUnits.objects.filter(
                        Item=ItemID, IsDeleted=0)
                    ItemUnitqueryserialize = Mc_ItemUnitSerializerThird(
                        ItemUnitquery, many=True).data
                    
                    for d in ItemUnitqueryserialize:
                        baseunitconcat=ShowBaseUnitQtyOnUnitDropDown(ItemID,d['id'],d['BaseUnitQuantity']).ShowDetails()
                        UnitDetails.append({
                            "UnitID": d['id'],
                            "UnitName": d['UnitID']['Name'] + str(baseunitconcat),
                            "BaseUnitQuantity": d['BaseUnitQuantity'],  
                           
                         
                        })
            # =====================IsDefaultTermsAndConditions================================================
                    TermsAndConditions = list()
                    TermsAndConditionsquery = M_TermsAndConditions.objects.filter(IsDefault=1)
                    TermsAndConditionsSerializer=M_TermsAndConditionsSerializer(TermsAndConditionsquery,many=True).data  
                    

                    for d in TermsAndConditionsSerializer:
                        TermsAndConditions.append({
                            "id": d['id'],
                            "TermsAndCondition": d['Name']
                            
                        })            

                    
                    
                    
                    b.update({"StockQuantity": Stock,
                              "UnitDetails": UnitDetails
                              })
                    
                          
                                
                if OrderID != 0:
                    OrderQuery=T_Orders.objects.get(id=OrderID)
                    a=T_OrderSerializerThird(OrderQuery).data
                   
                    OrderTermsAndCondition = list()
                    for b in a['OrderTermsAndConditions']:
                       # print(b['TermsAndCondition']['IsDeleted'])
                        if b['IsDeleted'] ==0:
                            OrderTermsAndCondition.append({
                                "id": b['TermsAndCondition']['id'],
                                "TermsAndCondition": b['TermsAndCondition']['Name'],
                            })


                    OrderData=list()
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
                                "CustomerName": a['Customer']['Name'],
                                "Supplier": a['Supplier']['id'],
                                "SupplierName": a['Supplier']['Name'],
                                "BillingAddressID": a['BillingAddress']['id'],
                                "BillingAddress": a['BillingAddress']['Address'],
                                "ShippingAddressID": a['ShippingAddress']['id'],
                                "ShippingAddress": a['ShippingAddress']['Address'],
                                "Inward": a['Inward'],  
                                "OrderItems": OrderItemSerializer,
                                "OrderTermsAndCondition" : OrderTermsAndCondition
                    })
                    FinalResult=OrderData[0]
                else:
                    NewOrder=list()
                    NewOrder.append({
                                "id": "",
                                "OrderDate":"",
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
                                "OrderItems":OrderItemSerializer,
                                "TermsAndConditions" : TermsAndConditions
                                })

                    FinalResult=NewOrder[0]
                         

                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':  '', 'Data': FinalResult})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})
