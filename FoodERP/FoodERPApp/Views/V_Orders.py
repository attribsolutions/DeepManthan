from django.http import JsonResponse
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, connection, transaction
from rest_framework.parsers import JSONParser

from ..Views.V_TransactionNumberfun import GetMaxNumber,GetPrifix
from ..Serializer.S_Orders import *
from ..Serializer.S_Items import *
from ..Serializer.S_PartyItems import *

from ..models import  *
class TermsAndCondtions(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    authentication__Class = JSONWebTokenAuthentication  
# =================================================================================================
    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                TermsCondition = JSONParser().parse(request)
                TermsCondition_serializer = M_TermsAndConditionsSerializer(data=TermsCondition)
                if TermsCondition_serializer.is_valid():
                    TermsCondition_serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True,  'Message': 'TermsAndCondtions Save Successfully' , 'Data':[] })
                return JsonResponse({'StatusCode': 406, 'Status': True,  'Message': TermsCondition_serializer.errors , 'Data':[]})
        except Exception as e:
                return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})   

    @transaction.atomic()
    def get(self, request ):
        try:
            with transaction.atomic():
                TermsCondition = M_TermsAndConditions.objects.all()
                if TermsCondition.exists():
                    TermsCondition_serializer = M_TermsAndConditionsSerializer(
                    TermsCondition, many=True)
                    return JsonResponse({'StatusCode': 200, 'Status': True,'Message': '','Data': TermsCondition_serializer.data })
                return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'TermsAndConditions Not available', 'Data': []})    
        except Exception as e:
                return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})
# ==================================================================================================
class OrderListFilterView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request,id=0):
        try:
            with transaction.atomic():
                Orderdata = JSONParser().parse(request)
                FromDate = Orderdata['FromDate']
                ToDate = Orderdata['ToDate']
                Customer = Orderdata['Customer']
                Supplier = Orderdata['Supplier']
                if(Supplier==''):
                    query = T_Orders.objects.filter(OrderDate__range=[FromDate,ToDate],Customer_id=Customer)
                else:
                    query = T_Orders.objects.filter(OrderDate__range=[FromDate,ToDate],Customer_id=Customer,Supplier_id=Supplier)
                # return JsonResponse({'query': str(Orderdata.query)})
                if query:
                    Order_serializer = T_OrderSerializerSecond(query, many=True).data
                    # return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':'','Data': Order_serializer})
                    OrderListData = list()
                    for a in Order_serializer:   
                        OrderListData.append({
                        "id": a['id'],
                        "OrderDate": a['OrderDate'],
                        "FullOrderNumber" : a['FullOrderNumber'],
                        "DeliveryDate": a['DeliveryDate'],
                        "Customer": a['Customer']['Name'],
                        "Supplier": a['Supplier']['Name'],
                        "OrderAmount": a['OrderAmount'],
                        "Description": a['Description'],
                        "BillingAddress" : a['BillingAddress']['Address'],
                        "ShippingAddress" : a['ShippingAddress']['Address'],
                        "CreatedBy" : a['CreatedBy'],
                        "CreatedOn" : a['CreatedOn']
                        
                        }) 
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':'','Data': OrderListData})
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':'Record Not Found','Data': []})
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
                '''Get Max Order Number'''
                a=GetMaxNumber.GetOrderNumber(Division,OrderType)
                Orderdata['OrderNo']= a
                '''Get Order Prifix '''
                b=GetPrifix.GetOrderPrifix(Division)
                Orderdata['FullOrderNumber']= b+""+str(a)
                # return JsonResponse({ 'Data': Orderdata })
                Order_serializer = T_OrderSerializer(data=Orderdata)
                if Order_serializer.is_valid():
                    Order_serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True,  'Message': 'Order Save Successfully' , 'Data':[] })
                return JsonResponse({'StatusCode': 406, 'Status': True,  'Message': Order_serializer.errors , 'Data':[]})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})

class T_OrdersViewSecond(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    authentication__Class = JSONWebTokenAuthentication
    
    def get(self, request,id=0):
        try:
            with transaction.atomic():
                OrderQuery = T_Orders.objects.filter(id=id)
                if OrderQuery.exists():
                    OrderSerializedata = T_OrderSerializerThird(OrderQuery, many=True).data
                    # return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': OrderSerializedata})
                    OrderData=list()
                    for a in OrderSerializedata:
                        
                        OrderTermsAndCondition=list()
                        for b in a['OrderTermsAndConditions']:
                            OrderTermsAndCondition.append({
                                "id": b['TermsAndCondition']['id'],
                                "TermsAndCondition":b['TermsAndCondition']['Name'],
                            })
                        
                        OrderItemDetails=list()
                        for b in a['OrderItem']:
                            OrderItemDetails.append({
                                "id": b['id'],
                                "Item":b['Item']['id'],
                                "ItemName":b['Item']['Name'],
                                "Quantity": b['Quantity'],
                                "MRP": b['MRP']['id'],
                                "MRPValue": b['MRP']['MRP'],
                                "Rate": b['Rate'],
                                "Unit": b['Unit']['id'],
                                "UnitName": b['Unit']['UnitID']['Name'],
                                "BaseUnitQuantity": b['BaseUnitQuantity'],
                                "GSTPercentage": b['GSTPercentage'],
                                "Margin":b['Margin']['id'],
                                "MarginValue":b['Margin']['Margin'],
                                "BasicAmount": b['BasicAmount'],
                                "GSTAmount": b['GSTAmount'],
                                "CGST": b['CGST'],
                                "SGST": b['SGST'],
                                "IGST": b['IGST'],
                                "CGSTPercentage": b['CGSTPercentage'],
                                "SGSTPercentage": b['SGSTPercentage'],
                                "IGSTPercentage": b['IGSTPercentage'],
                                "Amount": b['Amount'],
                            })
                        OrderData.append({
                            "id": a['id'],
                            "OrderDate": a['OrderDate'],
                            "DeliveryDate": a['DeliveryDate'],
                            "OrderAmount": a['OrderAmount'],
                            "Description": a['Description'],
                            "Customer": a['Customer']['id'],
                            "CustomerName": a['Customer']['Name'],
                            "Supplier": a['Supplier']['id'],
                            "SupplierName": a['Supplier']['Name'],
                            "BillingAddressID" :a['BillingAddress']['id'],
                            "BillingAddress" :a['BillingAddress']['Address'],
                            "ShippingAddressID" :a['ShippingAddress']['id'],
                            "ShippingAddress" :a['ShippingAddress']['Address'],
                            "OrderItem" : OrderItemDetails,
                            "OrderTermsAndCondition" : OrderTermsAndCondition
                        })      
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': OrderData[0]})
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Order Data Not available ', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})
    
    
    
    
    

    def put(self, request, id=0):
        try:
            with transaction.atomic():
                Orderupdatedata = JSONParser().parse(request)
                OrderupdateByID = T_Orders.objects.get(id=id)
                
                Orderupdate_Serializer = T_OrderSerializer(OrderupdateByID, data=Orderupdatedata)
                if Orderupdate_Serializer.is_valid():
                    Orderupdate_Serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Order Updated Successfully','Data':[]})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': Orderupdate_Serializer.errors ,'Data':[]})
        except Exception as e:
                return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})  
        
    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                Order_Data = T_Orders.objects.get(id=id)
                Order_Data.delete()
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Order Deleted Successfully','Data':[]})
        except T_Orders.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Record Not available', 'Data': []})
        except IntegrityError:   
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'T_Orders used in another tbale', 'Data': []}) 
        except Exception as e:
                return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})

class GetItemsForOrderView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    authentication__Class = JSONWebTokenAuthentication
    
    def post(self, request):
            try:
                with transaction.atomic():
                    # DivisionID = request.data['Division']
                    Supplier = request.data['Supplier'] # Order Page Supplier Id
                    EffectiveDate = request.data['EffectiveDate']
                    query = MC_PartyItems.objects.filter(Party_id = Supplier)
                    # return JsonResponse({ 'query': str(query.query)})
                    if not query:
                        return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'Items Not available', 'Data': []})
                    else:
                        Items_Serializer = MC_PartyItemSerializerSecond(query, many=True).data
                        ItemList = list()
                        for a in Items_Serializer:
                            ItemID =a['Item']['id']
                            Gst = GSTHsnCodeMaster(ItemID,EffectiveDate).GetTodaysGstHsnCode()
                            UnitDetails=list()
                            for d in a['Item']['ItemUnitDetails']:
                                if d['IsDeleted']== 0 :
                                    UnitDetails.append({
                                        "UnitID": d['id'],
                                        # "UnitID": d['UnitID']['id'],
                                        "UnitName": d['UnitID']['Name'],
                                        "BaseUnitQuantity": d['BaseUnitQuantity']
                                    })
                            
                            ItemList.append({
                                "id":a['Item']['id'],
                                "Name": a['Item']['Name'],
                                "Gstid":Gst[0]['Gstid'],
                                "GST":Gst[0]['GST'],
                                "UnitDetails":UnitDetails
                            })
                        return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data':ItemList })
            except Exception as e:
                return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})
        
    
    
                    