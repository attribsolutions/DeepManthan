
from django.http import JsonResponse
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
# from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import transaction
from rest_framework.parsers import JSONParser

from ..Views.V_CommFunction import UnitwiseQuantityConversion

from ..Serializer.S_MaterialIssue import StockQtyserializerForMaterialIssue

from ..Serializer.S_ProductionReIssue import *

from ..Serializer.S_Modules import *

from ..models import *


class MaterialIssueItemsView(CreateAPIView):

    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                WorkOrderDetailsdata = JSONParser().parse(request)
                ProductionID = WorkOrderDetailsdata['ProductionID']
                PartyID = WorkOrderDetailsdata['PartyID']
                ProductionMaterialIssue = TC_ProductionMaterialIssue.objects.filter(
                    Production=ProductionID).values('MaterialIssue')
                MaterialIssueItems = TC_MaterialIssueItems.objects.filter(
                    MaterialIssue=ProductionMaterialIssue[0]['MaterialIssue'])

                if MaterialIssueItems.exists():
                    MaterialIssueItems_Serializer = MaterialIssueItemsSerializer(
                        MaterialIssueItems, many=True).data
                    ItemDetails = list()
                    for b in MaterialIssueItems_Serializer:
                        Item = b['Item']['id']
                        z = 0

                        obatchwisestockquery = O_BatchWiseLiveStock.objects.filter(
                            Item_id=Item, Party_id=PartyID, BaseUnitQuantity__gt=0)
                        # return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': str(obatchwisestockquery.query)})
                        if obatchwisestockquery == "":
                            StockQtySerialize_data = []
                        else:
                            StockQtySerialize_data = StockQtyserializerForMaterialIssue(
                                obatchwisestockquery, many=True).data
                            stockDatalist = list()
                            for c in StockQtySerialize_data:

                                StockQty = UnitwiseQuantityConversion(
                                    b['Item']['id'], c['BaseUnitQuantity'], 0, 0, b['Unit']['id'], 0, 1).ConvertintoSelectedUnit()

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
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': ItemDetails})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})

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
    # authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request, id=0):
        try:
            with transaction.atomic():
                ProductionReIssueData = JSONParser().parse(request)
                ProductionReIssueItems = ProductionReIssueData['ProductionReIssueItems']
                O_BatchWiseLiveStockList = list()
                for a in ProductionReIssueItems:

                    BaseUnitQuantity = UnitwiseQuantityConversion(
                        a['Item'], a['IssueQuantity'], a['Unit'], 0, 0, 0, 1).GetBaseUnitQuantity()
                    print(BaseUnitQuantity)

                    O_BatchWiseLiveStockList.append({
                        "Quantity": a['BatchID'],
                        "Item": a['Item'],
                        "BaseUnitQuantity": BaseUnitQuantity
                    })
                    ProductionReIssueData.update(
                        {"obatchwiseStock": O_BatchWiseLiveStockList})

                # return JsonResponse({'StatusCode': 200, 'Status': True,'Data':MaterialIssueData})
                ProductionReIssue_Serializer = ProductionReIssueSerializerForSave(
                    data=ProductionReIssueData)
                # return JsonResponse({'StatusCode': 200, 'Status': True,'Data':MaterialIssue_Serializer.data})

                if ProductionReIssue_Serializer.is_valid():
                    ProductionReIssue_Serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Production ReIssue Save Successfully', 'Data': []})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': ProductionReIssue_Serializer.errors, 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': e.__dict__, 'Data': []})


class ProductionReIssueViewSecond(RetrieveAPIView):

    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request, id=0):
        try:
            with transaction.atomic():
                ProductionReIssuedata = T_ProductionReIssue.objects.get(id=id)
                ProductionReIssue_Serializer = ProductionReIssueSerializer(
                    ProductionReIssuedata)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': ProductionReIssue_Serializer.data})
        except H_Modules.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Module Not available', 'Data': []})

    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                MaterialIssueItemdata = T_ProductionReIssue.objects.all().filter(id=id)
                MaterialIssueItemdataserializer = ProductionReIssueSerializerForDelete(
                    MaterialIssueItemdata, many=True).data

                for a in MaterialIssueItemdataserializer[0]['ProductionReIssueItems']:
                    BaseUnitQuantity11 = UnitwiseQuantityConversion(
                        a['Item'], a['IssueQuantity'], a['Unit'], 0, 0, 0, 1).GetBaseUnitQuantity()

                    selectQuery = O_BatchWiseLiveStock.objects.filter(
                        LiveBatche=a['LiveBatchID']).values('BaseUnitQuantity')
                    UpdateQuery = O_BatchWiseLiveStock.objects.filter(LiveBatche=a['LiveBatchID']).update(
                        BaseUnitQuantity=int(selectQuery[0]['BaseUnitQuantity'])+int(BaseUnitQuantity11))

                MaterialIssuedata = T_ProductionReIssue.objects.get(id=id)
                MaterialIssuedata.delete()
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Material Issue Delete Successfully', 'Data': []})

        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})

class ProductionReIsssueFilter(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                ProductionReIsssuedata = JSONParser().parse(request)
                FromDate = ProductionReIsssuedata['FromDate']
                ToDate = ProductionReIsssuedata['ToDate']
                query = T_ProductionReIssue.objects.filter(Date__range=[FromDate, ToDate])
                print(str(query.query))
                if query:
                    ProductionReIsssue_serializerdata = ProductionReIssueSerializer(
                        query, many=True).data
                    # return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':'','Data': MaterialIsssue_serializerdata})
                    # ProductionReIsssueListData = list()
                    # for a in ProductionReIsssue_serializerdata:
                       
                    #     ProductionReIsssueListData.append({
                    #         "id": a['id'],
                    #         "MaterialIssueDate": a['MaterialIssueDate'],
                    #         "MaterialIssueNumber": a['MaterialIssueNumber'],
                    #         "FullMaterialIssueNumber": a['FullMaterialIssueNumber'],
                    #         "Item": a['Item']['id'],
                    #         "ItemName": a['Item']['Name'],
                    #         "Unit": a['Unit']['id'],
                    #         "UnitName": a['Unit']['BaseUnitConversion'],
                    #         "NumberOfLot": a['NumberOfLot'],
                    #         "LotQuantity": a["LotQuantity"],
                    #         "Company": a['Company']['id'],
                    #         "CompanyName": a['Company']['Name'],
                    #         "Party": a['Party']['id'],
                    #         "PartyName": a['Party']['Name'],
                    #         "CreatedOn": a['CreatedOn'],
                    #     })
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': ProductionReIsssue_serializerdata})
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Record Not Found', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  e, 'Data': []})