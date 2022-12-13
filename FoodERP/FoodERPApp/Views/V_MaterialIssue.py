from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, connection, transaction
from rest_framework.parsers import JSONParser
from django.db.models import Sum
from ..Serializer.S_Orders import *
from ..Serializer.S_WorkOrder import *
from ..models import *

class WorkOrderDetailsView(CreateAPIView):
       
    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                WorkOrderDetailsdata = JSONParser().parse(request)
                WorkOrderID = WorkOrderDetailsdata['WorkOrder']
                ItemID = WorkOrderDetailsdata['Item']
                CompanyID = WorkOrderDetailsdata['Company']
                DivisionID = WorkOrderDetailsdata['Division']
                Query = T_WorkOrder.objects.filter(id=WorkOrderID,Item_id=ItemID,Company_id=CompanyID,Division_id=DivisionID)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': str(Query.query)})
                if Query.exists():
                    WorkOrder_Serializer = WorkOrderSerializerSecond(Query,many=True).data
                    WorkOrderData = list()
                    # return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': WorkOrder_Serializer})
                    for a in WorkOrder_Serializer:
                        MaterialDetails =list()
                        total=0
                        for b in a['WorkOrderItems']:
                            Item = b['Item']['id']
                            obatchwisestockquery=O_BatchWiseLiveStock.objects.raw(''' SELECT O_BatchWiseLiveStock.id,O_BatchWiseLiveStock.Item_id,SUM(O_BatchWiseLiveStock.BaseUnitQuantity) AS actualStock FROM O_BatchWiseLiveStock WHERE O_BatchWiseLiveStock.Item_id = %s AND O_BatchWiseLiveStock.Party_id= GROUP BY O_BatchWiseLiveStock.Item_id''', [Item])
                            if not obatchwisestockquery:
                                StockQty =0.0
                            else:
                                StockQtySerialize_data = StockQtyserializer(obatchwisestockquery, many=True).data
                                StockQty = StockQtySerialize_data[0]['actualStock']
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
                            "Stock":Stock,
                            "EstimatedOutputQty": round(GetQuantity, 2),  
                            "Unit": a['Unit']['id'],
                            "UnitName": a['Unit']['UnitID']['Name'],
                            "BOMItems":MaterialDetails
                        })
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': BillofmaterialData[0]})
        except M_BillOfMaterial.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Bill Of Material Not available', 'Data': []})
