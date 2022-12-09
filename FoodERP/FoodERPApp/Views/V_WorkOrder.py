from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, connection, transaction
from rest_framework.parsers import JSONParser
from django.db.models import Sum
from ..Serializer.S_Orders import *
from ..Serializer.S_Bom import *
from ..Serializer.S_WorkOrder import *
from ..models import *

class BomDetailsView(CreateAPIView):
   
    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                BomDetailsdata = JSONParser().parse(request)
                BomID = BomDetailsdata['BomID']
                ItemID = BomDetailsdata['ItemID']
                GetQuantity = BomDetailsdata['Quantity']
                Query = M_BillOfMaterial.objects.filter(id=BomID,Item_id=ItemID)
                if Query.exists():
                    BOM_Serializer = M_BOMSerializerSecond(Query,many=True).data
                    BillofmaterialData = list()
                    # return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': BOM_Serializer})
                    for a in BOM_Serializer:
                        MaterialDetails =list()
                        total=0
                        for b in a['BOMItems']:
                            Item = b['Item']['id']
                            # obatchwisestockquery = O_BatchWiseLiveStock.objects.filter(Item_id=Item).values('Item').annotate(actualStock=Sum('BaseUnitQuantity')).values('actualStock')
                            obatchwisestockquery=O_BatchWiseLiveStock.objects.raw(''' SELECT O_BatchWiseLiveStock.id,O_BatchWiseLiveStock.Item_id,SUM(O_BatchWiseLiveStock.BaseUnitQuantity) AS actualStock FROM O_BatchWiseLiveStock WHERE O_BatchWiseLiveStock.Item_id = %s GROUP BY O_BatchWiseLiveStock.Item_id''', [Item])
                            if not obatchwisestockquery:
                                StockQty =0.0
                            else:
                                Serialize_data = StockQtyserializer(obatchwisestockquery, many=True).data
                                StockQty = Serialize_data[0]['actualStock']
                            Qty = float(b['Quantity']) /float(a['EstimatedOutputQty'])
                            ActualQty = float(GetQuantity * Qty)
                            MaterialDetails.append({
                                "id": b['id'],
                                "Item":b['Item']['id'],
                                "ItemName":b['Item']['Name'], 
                                "Unit": b['Unit']['id'],
                                "UnitName": b['Unit']['UnitID']['Name'],
                                "StockQuantity":StockQty,
                                "BomQuantity":b['Quantity'],
                                "Quantity":ActualQty
                            })
                        BillofmaterialData.append({
                            "id": a['id'],
                            "IsActive": a['IsActive'],
                            "Item":a['Item']['id'],
                            "ItemName":a['Item']['Name'],
                            "EstimatedOutputQty": round(GetQuantity, 2),  
                            "Unit": a['Unit']['id'],
                            "UnitName": a['Unit']['UnitID']['Name'],
                            "BOMItems":MaterialDetails
                        })
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': BillofmaterialData[0]})
        except M_BillOfMaterial.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Bill Of Material Not available', 'Data': []})


class WorkOrderList(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                WorkOrderdata = JSONParser().parse(request)
                FromDate = WorkOrderdata['FromDate']
                ToDate = WorkOrderdata['ToDate']
                query = T_WorkOrder.objects.filter(WorkOrderDate__range=[FromDate,ToDate])
                if query:
                    WorkOrder_serializerdata = WorkOrderSerializerSecond(query, many=True).data
                    # return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':'','Data': WorkOrder_serializerdata})
                    WorkOrderListData = list()
                    for a in WorkOrder_serializerdata:   
                        WorkOrderListData.append({
                        "id": a['id'],
                        "WorkOrderDate": a['WorkOrderDate'],
                        "Item":a['Item']['id'],
                        "ItemName":a['Item']['Name'],
                        "Bom": a['Bom'],
                        "NumberOfLot": a['NumberOfLot'],
                        "Quantity":a["Quantity"],
                        "Company": a['Company']['id'],
                        "CompanyName":a['Company']['Name'],
                        "EstimatedOutputQty": a['Quantity'],  
                        }) 
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':'','Data': WorkOrderListData})
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':'Record Not Found','Data': []})
        except Exception as e:
                return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})



class WorkOrderView(CreateAPIView):
       
    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication  
    
    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                WorkOrderData = JSONParser().parse(request)
                WorkOrder_Serializer = WorkOrderSerializer(data=WorkOrderData)
                if WorkOrder_Serializer.is_valid():
                    WorkOrder_Serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Work Order Save Successfully', 'Data': []})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': WorkOrder_Serializer.errors, 'Data': []})
        except Exception as e:
                return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})  

class WorkOrderViewSecond(RetrieveAPIView):
       
    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication
    
    @transaction.atomic()
    def get(self, request, id=0,Company=0):
        try:
            with transaction.atomic():
                Query = T_WorkOrder.objects.filter(id=id)
                if Query.exists():
                    WorkOrder_serializer = WorkOrderSerializerSecond(Query,many=True).data
                    WorkOrderData = list()
                    # return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': BOM_Serializer})
                    ActualBomqty =0
                    for a in WorkOrder_serializer:
                        ActualBomqty = float(a['Quantity']) /float(a['NumberOfLot'])
                        MaterialDetails =list()
                        for b in a['WorkOrderItems']:  
                            MaterialDetails.append({
                                "id": b['id'],
                                "Item":b['Item']['id'],
                                "ItemName":b['Item']['Name'], 
                                "Unit": b['Unit']['id'],
                                "UnitName": b['Unit']['UnitID']['Name'],
                                "BomQuantity":b['BomQuantity'],
                                "Quantity":b['Quantity'], 
                            })
                        
                        WorkOrderData.append({
                            "id": a['id'],
                            "WorkOrderDate": a['WorkOrderDate'],
                            "Item":a['Item']['id'],
                            "ItemName":a['Item']['Name'],
                            "Bom": a['Bom'],
                            "ActualBomqty": ActualBomqty,
                            "NumberOfLot": a['NumberOfLot'],
                            "Quantity":a["Quantity"],
                            "Company": a['Company']['id'],
                            "CompanyName":a['Company']['Name'],
                            "EstimatedOutputQty": a['Quantity'],  
                            "WorkOrderItems":MaterialDetails,
                        })
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': WorkOrderData})
        except T_WorkOrder.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Work Orders Not available', 'Data': []})
    
    
    @transaction.atomic()
    def delete(self, request, id=0,Company=0):
        try:
            with transaction.atomic():
                WorkOrderdata = T_WorkOrder.objects.get(id=id)
                WorkOrderdata.delete()
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Work Order Deleted Successfully', 'Data': []})
        except T_WorkOrder.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Work Order Not available', 'Data': []})
        except IntegrityError:
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Work Order used in another table', 'Data': []})                