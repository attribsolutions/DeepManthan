
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, connection, transaction
from rest_framework.parsers import JSONParser

from ..Views.V_CommFunction import UnitwiseQuantityConversion

from ..Serializer.S_MaterialIssue import StockQtyserializerForMaterialIssue

from ..Serializer.S_ProductionReIssue import *

from ..Serializer.S_Modules import *

from ..models import *

class MaterialIssueItemsView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                WorkOrderDetailsdata = JSONParser().parse(request)
                ProductionID = WorkOrderDetailsdata['ProductionID']
                PartyID = WorkOrderDetailsdata['PartyID']
                ProductionMaterialIssue = TC_ProductionMaterialIssue.objects.filter(Production = ProductionID).values('MaterialIssue')
                MaterialIssueItems= TC_MaterialIssueItems.objects.filter(MaterialIssue=ProductionMaterialIssue[0]['MaterialIssue'])
                
                if MaterialIssueItems.exists():
                    MaterialIssueItems_Serializer = MaterialIssueItemsSerializer(MaterialIssueItems, many=True).data
                    ItemDetails=list()
                    for b in MaterialIssueItems_Serializer:
                            Item = b['Item']['id']
                            z = 0
                          
                            obatchwisestockquery = O_BatchWiseLiveStock.objects.filter(Item_id=Item, Party_id=PartyID, BaseUnitQuantity__gt=0)
                            # return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': str(obatchwisestockquery.query)})
                            if obatchwisestockquery == "":
                                StockQtySerialize_data = []
                            else:
                                StockQtySerialize_data = StockQtyserializerForMaterialIssue(
                                    obatchwisestockquery, many=True).data
                                stockDatalist=list()
                                for c in StockQtySerialize_data:

                                    StockQty = UnitwiseQuantityConversion(
                                        b['Item']['id'], c['BaseUnitQuantity'], 0, 0, b['Unit']['id'], 0,1).ConvertintoSelectedUnit()
                                    
                                    stockDatalist.append({
                                        "id": c['id'],
                                        "Item": c['Item'],
                                        "BatchDate": c['LiveBatche']['BatchDate'],
                                        "BatchCode": c['LiveBatche']['BatchCode'],
                                        "SystemBatchDate": c['LiveBatche']['SystemBatchDate'],
                                        "SystemBatchCode": c['LiveBatche']['SystemBatchCode'],
                                        "LiveBatchID": c['LiveBatche']['id'],
                                        "ObatchwiseQuantity": c['Quantity'],
                                        "BaseUnitQuantity": StockQty,
                                        "Qty": ""
                                    })
                            ItemDetails.append({
                                "id": b['id'],
                                "Item": b['Item']['id'],
                                "ItemName": b['Item']['Name'],
                                "Unit": b['Unit']['id'],
                                "UnitName": b['Unit']['UnitID']['Name'],
                                "Quantity": "",
                                "BatchesData": stockDatalist
                            })
                    return JsonResponse({'StatusCode': 200, 'Status': True,'Message': '','Data': ItemDetails })
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})
        
# class ProductionMaterialIssueItemsView(CreateAPIView):
    
#     permission_classes = (IsAuthenticated,)
#     authentication_class = JSONWebTokenAuthentication
    
#     @transaction.atomic()
#     def post(self, request):
#         try:
#             with transaction.atomic():
#                 data = JSONParser().parse(request)
               
#                 ProductionID = data['ProductionID']
#                 PartyID=data['PartyID']
                
                
                
#             #    return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'Modules Not available', 'Data': []})    
#         except Exception as e:
#             return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})
         
class ProductionReIssueView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication 
    
    @transaction.atomic()
    def post(self, request, id=0):
        try:
            with transaction.atomic():
                MaterialIssueData = JSONParser().parse(request)
                ProductionReIssueItems = MaterialIssueData['ProductionReIssueItems']
                O_BatchWiseLiveStockList = list()
                for a in ProductionReIssueItems:
                   
                    BaseUnitQuantity = UnitwiseQuantityConversion(a['Item'], a['IssueQuantity'], a['Unit'], 0, 0, 0, 1).GetBaseUnitQuantity()
                    print(BaseUnitQuantity)
                
                    O_BatchWiseLiveStockList.append({
                        "Quantity": a['BatchID'],
                        "Item": a['Item'],
                        "BaseUnitQuantity": BaseUnitQuantity
                    })
                    MaterialIssueData.update({"obatchwiseStock": O_BatchWiseLiveStockList})
                
                # return JsonResponse({'StatusCode': 200, 'Status': True,'Data':MaterialIssueData})
                MaterialIssue_Serializer = ProductionReIssueSerializerForSave(data=MaterialIssueData)
                # return JsonResponse({'StatusCode': 200, 'Status': True,'Data':MaterialIssue_Serializer.data})

                if MaterialIssue_Serializer.is_valid():
                    MaterialIssue_Serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Material Issue Save Successfully', 'Data': []})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': MaterialIssue_Serializer.errors, 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': e.__dict__, 'Data': []})
 

class ProductionReIssueViewSecond(RetrieveAPIView):
    
    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request, id=0):
        try:
            with transaction.atomic():
                ProductionReIssuedata = T_ProductionReIssue.objects.get(id=id)
                ProductionReIssue_Serializer = ProductionReIssueSerializer(ProductionReIssuedata)
                return JsonResponse({'StatusCode': 200, 'Status': True,'Message': '','Data': ProductionReIssue_Serializer.data})
        except H_Modules.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Module Not available', 'Data': []})
           

    @transaction.atomic()
    def put(self, request, id=0):
        try:
            with transaction.atomic():
                Modulesdata = JSONParser().parse(request)
                ModulesdataByID = H_Modules.objects.get(id=id)
                Modules_Serializer = H_ModulesSerializer(ModulesdataByID, data=Modulesdata)
                if Modules_Serializer.is_valid():
                    Modules_Serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Module Updated Successfully','Data':[]})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': Modules_Serializer.errors,'Data' :[]})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})            

    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                Modulesdata = H_Modules.objects.get(id=id)
                Modulesdata.delete()
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Module  Deleted Successfully', 'Data':[]})
        except H_Modules.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Module Not available', 'Data': []})    
        except IntegrityError:   
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Module used in another table', 'Data': []})    