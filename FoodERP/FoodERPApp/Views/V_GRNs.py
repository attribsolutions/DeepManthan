from django.http import JsonResponse
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, connection, transaction
from rest_framework.parsers import JSONParser

from ..Serializer.S_GRNs import *
from ..Serializer.S_Orders import *

from ..models import  *


class T_GRNView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request,id=0):
        try:
            with transaction.atomic():
                query = T_GRNs.objects.all()
                if not query:
                    return JsonResponse({'StatusCode': 200, 'Status': True,'Message':  'Records Not available', 'Data': []})
                else:
                    GRN_serializer = T_GRNSerializer(query, many=True).data
                    return JsonResponse({'StatusCode': 200, 'Status': 'true', 'Data': GRN_serializer})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})

    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                GRNdata = JSONParser().parse(request)
                GRN_serializer = T_GRNSerializer(data=GRNdata)
                if GRN_serializer.is_valid():
                    GRN_serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': 'true',  'Message': 'GRN Save Successfully', 'Data':[]})
                return JsonResponse({'StatusCode': 200, 'Status': 'true',  'Message': GRN_serializer.errors, 'Data':[]})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})

class T_GRNViewSecond(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request,id=0):
        try:
            with transaction.atomic():
                GRNdata = T_GRNs.objects.get(id=id)
                GRN_serializer = T_GRNSerializer(GRNdata)
                return JsonResponse({'StatusCode': 200, 'Status': 'true', 'Data': GRN_serializer.data})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})
   

    @transaction.atomic()
    def put(self, request, id=0):
        try:
            with transaction.atomic():
                GRN_data = JSONParser().parse(request)
                GRN_dataByID = T_GRNs.objects.get(id=id)
                GRN_Serializer = T_GRNSerializer(GRN_dataByID, data=GRN_data)
                if GRN_Serializer.is_valid():
                    GRN_Serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'GRN  Updated Successfully','Data':{}})
                return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': GRN_Serializer.errors ,'Data':[]})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})
   
    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                GRN_Data = T_GRNs.objects.get(id=id)
                GRN_Data.delete()
                return JsonResponse({'StatusCode': 200, 'Status': 'true', 'Message': 'GRN Deleted Successfully', 'Data':[]})
        except T_GRNs.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Record Not available', 'Data': []})
        except IntegrityError:   
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'T_GRN used in another tbale', 'Data': []})    



class GetOrderDetailsForGrnView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    authentication__Class = JSONWebTokenAuthentication
    
    
    def post(self, request,id=0):
        try:
            with transaction.atomic():
                POOrderIDs = request.data['OrderIDs']
                Order_list = POOrderIDs.split(",")
                AllData = list()
                for OrderID in Order_list:
                    OrderQuery = T_Orders.objects.filter(id=OrderID)
                    if OrderQuery.exists():
                        OrderSerializedata = T_OrderSerializerThird(OrderQuery, many=True).data
                        # return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': OrderSerializedata})
                        OrderData=list()
                        for a in OrderSerializedata:
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
                                    "GST": b['GST']['id'],
                                    "GSTPercentage": b['GST']['GSTPercentage'],
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
                            })        
                        AllData.append({"Data":OrderData})
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': AllData})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})
    
    