from django.http import JsonResponse
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, connection, transaction
from rest_framework.parsers import JSONParser

from ..Views.V_TransactionNumberfun import *

from ..Serializer.S_GRNs import *
from ..Serializer.S_Orders import *

from ..models import  *
from django.db.models import *


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
                    GRN_serializer = T_GRNSerializerForGET(query, many=True).data
                    GRNListData = list()
                    for a in GRN_serializer:   
                        GRNListData.append({
                        "id": a['id'],
                        "GRNDate": a['GRNDate'],
                        "Customer": a['Customer']['id'],
                        "CustomerName": a['Customer']['Name'],
                        "GRNNumber": 1,
                        "FullGRNNumber": "1",
                        "GrandTotal": "5250.00",
                        "Party": a['Party']['id'],
                        "PartyName": a['Party']['Name'],
                        "CreatedBy": 1,
                        "UpdatedBy": 1,

                        })
                    
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': GRNListData})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})

    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                GRNdata = JSONParser().parse(request)
               
                Customer = GRNdata['Customer']
                '''Get Max GRN Number'''
                a=GetMaxNumber.GetGrnNumber(Customer)
                GRNdata['GRNNumber']= a
                '''Get Order Prifix '''
                b=GetPrifix.GetGrnPrifix(Customer)
                GRNdata['FullGRNNumber']= b+""+str(a)
                GRN_serializer = T_GRNSerializer(data=GRNdata)
                if GRN_serializer.is_valid():
                    GRN_serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True,  'Message': 'GRN Save Successfully', 'Data':[]})
                return JsonResponse({'StatusCode': 400, 'Status': True,  'Message': GRN_serializer.errors, 'Data':[]})
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
                GRN_serializer = T_GRNSerializerForGET(GRNdata).data
                GRNItemListData = list()
                for a in GRN_serializer['GRNItems']:   
                        GRNItemListData.append({
                        "Item": a['Item']['id'],
                        "ItemName":a['Item']['Name'],
                        "Quantity": a['Quantity'],
                        "Unit" :a['Unit']['id'],    
                        "UnitName" :a['Unit']['UnitID'],    
                        "BaseUnitQuantity": a['BaseUnitQuantity'],
                        "MRP": a['MRP'],
                        "ReferenceRate": a['ReferenceRate'],
                        "Rate": a['Rate'],
                        "BasicAmount": a['BasicAmount'],
                        "TaxType": a['TaxType'],
                        "GSTPercentage": a['GSTPercentage'],
                        "GSTAmount": a['GSTAmount'],
                        "Amount": a['Amount'],
                        "DiscountType": a['DiscountType'],
                        "Discount": a['Discount'],
                        "DiscountAmount": a['DiscountAmount'],
                        "CGST": a['CGST'],
                        "SGST": a['SGST'],
                        "IGST": a['IGST'],
                        "CGSTPercentage": a['CGSTPercentage'],
                        "SGSTPercentage": a['SGSTPercentage'],
                        "IGSTPercentage": a['IGSTPercentage'],
                        "BatchDate": a['BatchDate'],
                        "BatchCode": a['BatchCode'],
                    })

                GRNListData = list()
                a=GRN_serializer
                GRNListData.append({
                    "id": a['id'],
                    "GRNDate": a['GRNDate'],
                    "Customer": a['Customer']['id'],
                    "CustomerName": a['Customer']['Name'],
                    "GRNNumber": a['GRNNumber'],
                    "FullGRNNumber": a['FullGRNNumber'],
                    "GrandTotal": a['GrandTotal'],
                    "Party": a['Party']['id'],
                    "PartyName": a['Party']['Name'],
                    "CreatedBy": a['CreatedBy'],
                    "UpdatedBy": a['UpdatedBy'],
                    "GRNReferences": 
                        {
                            "Invoice": a['GRNReferences']['Invoice'],
                            "Order": a['GRNReferences']['Order'],
                            "ChallanNo":a['GRNReferences']['ChallanNo'],
                        },
                    "GRNItems" : GRNItemListData  

                    })  
                
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': GRNListData})
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
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'GRN Deleted Successfully', 'Data':[]})
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
                for OrderId in Order_list:
                    OrderQuery = T_Orders.objects.filter(id=OrderId)
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
                        return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': OrderData[0]})
                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Order Data Not available ', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})
    # def post(self, request,id=0):
    #     try:
    #         with transaction.atomic():
    #             POOrderIDs = request.data['OrderIDs']
    #             Order_list = POOrderIDs.split(",")
    #             # return JsonResponse({'StatusCode': 400, 'Status': True,'Data':Order_list}) 
    #             # OrderQuery = T_Orders.objects.filter(id__in=Order_list).annotate(total=Sum('OrderAmount')).order_by("Supplier_id")
    #             OrderQuery =  T_Orders.objects.values("Supplier_id","Customer_id").annotate(Supplier=F("Supplier_id"),Customer=F("Customer_id"),OrderAmount=Sum('OrderAmount')).filter(id__in =Order_list).order_by("Supplier_id")
    #             if OrderQuery.exists():
    #                 OrderSerializedata = OrderSerializerForGrn(OrderQuery, many=True).data
    #                 return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': OrderSerializedata[0]})
    #             #return JsonResponse({'StatusCode': 400, 'Status': True,'Data':str(OrderQuery.query)})      
    #     except Exception as e:
    #         return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})     