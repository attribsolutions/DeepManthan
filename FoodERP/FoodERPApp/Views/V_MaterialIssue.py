from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, connection, transaction
from rest_framework.parsers import JSONParser
from django.db.models import Sum
from ..Serializer.S_WorkOrder import *
from ..Serializer.S_MaterialIssue import *
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
                PartyID = WorkOrderDetailsdata['Party']
                GetQuantity = WorkOrderDetailsdata['Quantity']
                Query = T_WorkOrder.objects.filter(id=WorkOrderID,Item_id=ItemID,Company_id=CompanyID,Party_id=PartyID)
                # return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': str(Query.query)})
                if Query.exists():
                    WorkOrder_Serializer = WorkOrderSerializerSecond(Query,many=True).data
                    WorkOrderData = list()
                    # return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': WorkOrder_Serializer})
                    for a in WorkOrder_Serializer:
                        MaterialDetails =list()
                        for b in a['WorkOrderItems']:
                            Item = b['Item']['id']
                            obatchwisestockquery= O_BatchWiseLiveStock.objects.filter(Item_id=Item,Party_id=PartyID)
                            # return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': str(obatchwisestockquery.query)})
                            if not obatchwisestockquery:
                                StockQtySerialize_data =[]
                            else:
                                StockQtySerialize_data = StockQtyserializerForMaterialIssue(obatchwisestockquery, many=True).data
                                Qty = float(b['Quantity']) /float(GetQuantity)
                                ActualQty = float(GetQuantity * Qty)
                                stockDatalist = list()
                                add=0
                                amount = 0
                                p =0
                                for c in StockQtySerialize_data:
                                    if amount==0:
                                        if(float(c['BaseUnitQuantity']) > float(ActualQty)):
                                            p=float(ActualQty)
                                            add=float(add) + float(ActualQty)
                                        else:
                                            p=float(c['BaseUnitQuantity'])
                                            amount = float(ActualQty)- float(c['BaseUnitQuantity'])
                                            add = float(add) + float(c['BaseUnitQuantity'])
                                    else:
                                        if(float(amount) > float(c['BaseUnitQuantity'])):
                                            p=float(c['BaseUnitQuantity'])
                                            amount = float(amount)-float(c['BaseUnitQuantity'])
                                            add = float(add) + float(c['BaseUnitQuantity'])
                                        else:
                                            p=float(amount)
                                            add = float(add) + float(amount) 
                                            amount= float(c['BaseUnitQuantity'])-float(amount)           
                                  
                                          
                                    stockDatalist.append({
                                        "id": c['id'],
                                        "Item":c['Item'],
                                        "BatchDate":c['BatchDate'],
                                        "BatchCode":c['BatchCode'],
                                        "SystemBatchDate":c['SystemBatchDate'],
                                        "SystemBatchCode":c['SystemBatchCode'],
                                        "ObatchwiseQuantity":c['Quantity'],
                                        "BaseUnitQuantity":c['BaseUnitQuantity'],
                                        "Qty":p
                                    })
                            MaterialDetails.append({
                                "id": b['id'],
                                "Item":b['Item']['id'],
                                "ItemName":b['Item']['Name'], 
                                "Unit": b['Unit']['id'],
                                "UnitName": b['Unit']['UnitID']['Name'],
                                "Quantity":b['Quantity'],
                                "BatchesData":stockDatalist   
                            })
                        WorkOrderData.append({
                            "ItemsData":MaterialDetails
                        })    
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data':WorkOrderData[0]})
        except T_WorkOrder.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Bill Of Material Not available', 'Data': []})
