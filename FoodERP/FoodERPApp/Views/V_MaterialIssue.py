from django.http import JsonResponse
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
# from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import transaction
from rest_framework.parsers import JSONParser
from ..Views.V_TransactionNumberfun import GetMaxNumber, GetPrifix
from ..Serializer.S_WorkOrder import *
from ..Serializer.S_MaterialIssue import *
from ..models import *



class WorkOrderDetailsView(CreateAPIView):

    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication

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
                Query = T_WorkOrder.objects.filter(
                    id=WorkOrderID, Item_id=ItemID, Company_id=CompanyID, Party_id=PartyID)
                # return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': str(Query.query)})
                if Query.exists():
                    WorkOrder_Serializer = WorkOrderSerializerSecond(
                        Query, many=True).data
                    # return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': WorkOrder_Serializer})
                    for a in WorkOrder_Serializer:
                        MaterialDetails = list()
                        workorderqty = a['Quantity']

                        for b in a['WorkOrderItems']:
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

                                Qty = float(b['Quantity']) / \
                                    float(workorderqty)
                                ActualQty = float(GetQuantity * Qty)
                                stockDatalist = list()
                                add = 0
                                amount = 0
                                # p =0
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
                                        # "Qty":p
                                        "Qty": ""
                                    })
                            MaterialDetails.append({
                                "id": b['id'],
                                "Item": b['Item']['id'],
                                "ItemName": b['Item']['Name'],
                                "Unit": b['Unit']['id'],
                                "UnitName": b['Unit']['BaseUnitConversion'],
                                "Quantity": round(ActualQty, 3),
                                "BatchesData": stockDatalist
                            })
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': MaterialDetails})
        except T_WorkOrder.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Material Issue Not available', 'Data': []})


class MaterialIsssueList(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                MaterialIsssuedata = JSONParser().parse(request)
                FromDate = MaterialIsssuedata['FromDate']
                ToDate = MaterialIsssuedata['ToDate']
                query = T_MaterialIssue.objects.filter(
                    MaterialIssueDate__range=[FromDate, ToDate])
                if query:
                    MaterialIsssue_serializerdata = MatetrialIssueSerializerSecond(
                        query, many=True).data
                    # return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':'','Data': MaterialIsssue_serializerdata})
                    MaterialIsssueListData = list()
                    for a in MaterialIsssue_serializerdata:
                       
                        MaterialIsssueListData.append({
                            "id": a['id'],
                            "MaterialIssueDate": a['MaterialIssueDate'],
                            "MaterialIssueNumber": a['MaterialIssueNumber'],
                            "FullMaterialIssueNumber": a['FullMaterialIssueNumber'],
                            "Item": a['Item']['id'],
                            "ItemName": a['Item']['Name'],
                            "Unit": a['Unit']['id'],
                            "UnitName": a['Unit']['BaseUnitConversion'],
                            "NumberOfLot": a['NumberOfLot'],
                            "LotQuantity": a["LotQuantity"],
                            "Company": a['Company']['id'],
                            "CompanyName": a['Company']['Name'],
                            "Party": a['Party']['id'],
                            "PartyName": a['Party']['Name'],
                            "CreatedOn": a['CreatedOn'],
                        })
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': MaterialIsssueListData})
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Record Not Found', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})


class MaterialIssueView(CreateAPIView):

    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                MaterialIssueData = JSONParser().parse(request)
                
                Party = MaterialIssueData['Party']
               
                MaterialIssueDate = MaterialIssueData['MaterialIssueDate']
                
                a = GetMaxNumber.GetMaterialIssueNumber(
                    Party, MaterialIssueDate)
               
                MaterialIssueData['MaterialIssueNumber'] = a
                '''Get Order Prifix '''
                b = GetPrifix.GetMaterialIssuePrifix(Party)
                MaterialIssueData['FullMaterialIssueNumber'] = b+""+str(a)
                MaterialIssueItems = MaterialIssueData['MaterialIssueItems']
                
                O_BatchWiseLiveStockList = list()
                for MaterialIssueItem in MaterialIssueItems:
                    BaseUnitQuantity = UnitwiseQuantityConversion(
                        MaterialIssueItem['Item'], MaterialIssueItem['IssueQuantity'], MaterialIssueItem['Unit'], 0, 0, 0, 1).GetBaseUnitQuantity()

                    O_BatchWiseLiveStockList.append({
                        "Quantity": MaterialIssueItem['BatchID'],
                        "Item": MaterialIssueItem['Item'],
                        "BaseUnitQuantity": BaseUnitQuantity
                    })
                MaterialIssueData.update(
                    {"obatchwiseStock": O_BatchWiseLiveStockList})
               
                MaterialIssue_Serializer = MaterialIssueSerializer(
                    data=MaterialIssueData)
                
                if MaterialIssue_Serializer.is_valid():
                    MaterialIssue_Serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Material Issue Save Successfully', 'Data': []})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': MaterialIssue_Serializer.errors, 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': e.__dict__, 'Data': []})


class MaterialIssueViewSecond(RetrieveAPIView):

    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication
    
    @transaction.atomic()
    def get(self, request, id=0):
        try:
            with transaction.atomic():
                Query = T_MaterialIssue.objects.filter(id=id)
                if Query.exists():
                    MaterialIssue_serializer = TestMaterialIssueShowSerializer(Query, many=True).data
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': MaterialIssue_serializer})
        except T_MaterialIssue.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Material Issue Not available', 'Data': []})
    
    
    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                MaterialIssueItemdata = T_MaterialIssue.objects.all().filter(id=id)
                MaterialIssueItemdataserializer = MatetrialIssueSerializerForDelete(
                    MaterialIssueItemdata, many=True).data
                # return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'IBChallan Delete Successfully', 'Data':MaterialIssueItemdataserializer})
    
                for a in MaterialIssueItemdataserializer[0]['MaterialIssueItems']:
                    BaseUnitQuantity11 = UnitwiseQuantityConversion(
                        a['Item'], a['IssueQuantity'], a['Unit'], 0, 0, 0, 1).GetBaseUnitQuantity()

                    # O_BatchWiseLiveStockList.update({
                    #     "Item": a['Item'],
                    #     "Quantity": a['IssueQuantity'],
                    #     "Unit": a['Unit'],
                    #     "BaseUnitQuantity": BaseUnitQuantity,
                    #     "OriginalBaseUnitQuantity": BaseUnitQuantity,
                    #     "Party": MaterialIssueItemdataserializer[0]['Party'],
                    #     "LiveBatche": a['LiveBatchID'],
                    #     "CreatedBy": 1,
                    # })
                    selectQuery=O_BatchWiseLiveStock.objects.filter(LiveBatche=a['LiveBatchID']).values('BaseUnitQuantity')
                    UpdateQuery=O_BatchWiseLiveStock.objects.filter(LiveBatche=a['LiveBatchID']).update(BaseUnitQuantity = int(selectQuery[0]['BaseUnitQuantity'] )+int(BaseUnitQuantity11))
                    
                # MaterialIssueItemdataserializer = obatchwiseStockSerializerfordelete(
                #     data=O_BatchWiseLiveStockList)

                # if MaterialIssueItemdataserializer.is_valid():
                #     MaterialIssueItemdataserializer.save()

                MaterialIssuedata = T_MaterialIssue.objects.get(id=id)
                MaterialIssuedata.delete()
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Material Issue Delete Successfully', 'Data': []})
                # else:
                #     transaction.set_rollback(True)
                #     return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': MaterialIssueItemdataserializer.errors, 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})




    
