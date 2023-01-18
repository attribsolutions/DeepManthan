from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, connection, transaction
from rest_framework.parsers import JSONParser
from django.db.models import Sum
from ..Views.V_TransactionNumberfun import GetMaxNumber, GetPrifix
from ..Serializer.S_WorkOrder import *
from ..Serializer.S_MaterialIssue import *
from ..models import *
from rest_framework.views import exception_handler

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
                    # return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': WorkOrder_Serializer})
                    for a in WorkOrder_Serializer:
                        MaterialDetails =list()
                        workorderqty=a['Quantity']
                        
                        for b in a['WorkOrderItems']:
                            Item = b['Item']['id']
                            z=0
                            obatchwisestockquery= O_BatchWiseLiveStock.objects.filter(Item_id=Item,Party_id=PartyID,BaseUnitQuantity__gt=0)
                            # return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': str(obatchwisestockquery.query)})
                            if obatchwisestockquery == "":
                                StockQtySerialize_data =[]
                            else:
                                StockQtySerialize_data = StockQtyserializerForMaterialIssue(obatchwisestockquery, many=True).data
                                print(StockQtySerialize_data)
                                Qty = float(b['Quantity']) /float(workorderqty)
                                ActualQty = float(GetQuantity * Qty)
                                stockDatalist = list()
                                add=0
                                amount = 0
                                # p =0
                                for c in StockQtySerialize_data:
                                    # if(add >= float(ActualQty)):
                                    #     p=0
                                    # else:    
                                    #     if amount==0:
                                    #         if(float(c['BaseUnitQuantity']) > float(ActualQty)):
                                    #             p=float(ActualQty)
                                    #             add=float(add) + float(ActualQty)

                                    #         else:
                                    #             p=float(c['BaseUnitQuantity'])
                                    #             amount = float(ActualQty)- float(c['BaseUnitQuantity'])
                                    #             add = float(add) + float(c['BaseUnitQuantity'])
                                    #     else:
                                    #         if(float(amount) > float(c['BaseUnitQuantity'])):
                                    #             p=float(c['BaseUnitQuantity'])
                                    #             amount = float(amount)-float(c['BaseUnitQuantity'])
                                    #             add = float(add) + float(c['BaseUnitQuantity'])
                                    #         else:
                                    #             p=float(amount)
                                    #             add = float(add) + float(amount) 
                                    #             amount= float(c['BaseUnitQuantity'])-float(amount)            
                                    
                                    StockQty=UnitwiseQuantityConversion(b['Item']['id'],c['BaseUnitQuantity'],0,0,b['Unit']['id'],0).ConvertintoSelectedUnit()
                                    
                                    stockDatalist.append({
                                        "id": c['id'],
                                        "Item":c['Item'],
                                        "BatchDate":c['LiveBatche']['BatchDate'],
                                        "BatchCode":c['LiveBatche']['BatchCode'],
                                        "SystemBatchDate":c['LiveBatche']['SystemBatchDate'],
                                        "SystemBatchCode":c['LiveBatche']['SystemBatchCode'],
                                        "LiveBatchID" : c['LiveBatche']['id'],
                                        "ObatchwiseQuantity":c['Quantity'],
                                        "BaseUnitQuantity":StockQty,
                                        # "Qty":p
                                        "Qty":""
                                    })
                            MaterialDetails.append({
                                "id": b['id'],
                                "Item":b['Item']['id'],
                                "ItemName":b['Item']['Name'], 
                                "Unit": b['Unit']['id'],
                                "UnitName": b['Unit']['UnitID']['Name'],
                                "Quantity":round(ActualQty, 3),
                                "BatchesData":stockDatalist   
                            })
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data':MaterialDetails})
        except T_WorkOrder.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Material Issue Not available', 'Data': []})


class MaterialIsssueList(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                MaterialIsssuedata = JSONParser().parse(request)
                FromDate = MaterialIsssuedata['FromDate']
                ToDate = MaterialIsssuedata['ToDate']
                query = T_MaterialIssue.objects.filter(MaterialIssueDate__range=[FromDate,ToDate])
                if query:
                    MaterialIsssue_serializerdata = MatetrialIssueSerializerSecond(query, many=True).data
                    # return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':'','Data': MaterialIsssue_serializerdata})
                    MaterialIsssueListData = list()
                    for a in MaterialIsssue_serializerdata:
                        baseunitconcat=ShowBaseUnitQtyOnUnitDropDown(a['Item']['id'],a['Unit']['id'],a['Unit']['BaseUnitQuantity']).ShowDetails()   
                        MaterialIsssueListData.append({
                        "id": a['id'],
                        "MaterialIssueDate": a['MaterialIssueDate'],
                        "MaterialIssueNumber": a['MaterialIssueNumber'],
                        "FullMaterialIssueNumber": a['FullMaterialIssueNumber'],
                        "Item":a['Item']['id'],
                        "ItemName":a['Item']['Name'],
                        "Unit": a['Unit']['id'],
                        "UnitName": a['Unit']['UnitID']['Name']+baseunitconcat,
                        "NumberOfLot": a['NumberOfLot'],
                        "LotQuantity":a["LotQuantity"],
                        "Company": a['Company']['id'],
                        "CompanyName":a['Company']['Name'],
                        "Party":a['Party']['id'],
                        "PartyName":a['Party']['Name'],
                        "CreatedOn": a['CreatedOn'],
                        }) 
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':'','Data': MaterialIsssueListData})
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':'Record Not Found','Data': []})
        except Exception as e:
                return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})

class MaterialIssueView(CreateAPIView):
       
    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication  
    
    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                MaterialIssueData = JSONParser().parse(request)
                Party = MaterialIssueData['Party']
                MaterialIssueDate = MaterialIssueData['MaterialIssueDate']
                a = GetMaxNumber.GetMaterialIssueNumber(Party, MaterialIssueDate)
                # return JsonResponse({'StatusCode': 200, 'Status': True,   'Data':[] })
                MaterialIssueData['MaterialIssueNumber'] = a
                '''Get Order Prifix '''
                b = GetPrifix.GetMaterialIssuePrifix(Party)
                MaterialIssueData['FullMaterialIssueNumber'] = b+""+str(a)
                MaterialIssueItems = MaterialIssueData['MaterialIssueItems']
                O_BatchWiseLiveStockList=list()
                for MaterialIssueItem in MaterialIssueItems:
                    O_BatchWiseLiveStockList.append({
                        "Quantity" : MaterialIssueItem['BatchID'],
                        "Item" : MaterialIssueItem['Item'],
                        "BaseUnitQuantity" : MaterialIssueItem['IssueQuantity']
                    })
                        
                MaterialIssueData.update({"obatchwiseStock":O_BatchWiseLiveStockList}) 
                # return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Material Issue Save Successfully', 'Data': MaterialIssueData})
                MaterialIssue_Serializer = MaterialIssueSerializer(data=MaterialIssueData)
                
                if MaterialIssue_Serializer.is_valid():
                    MaterialIssue_Serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Material Issue Save Successfully', 'Data': []})
                else:
                   
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': MaterialIssue_Serializer.errors, 'Data': []})
                    
        except Exception as e:
               
                return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': e.__dict__, 'Data': []})
                  

class MaterialIssueViewSecond(RetrieveAPIView):
       
    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication
    
    @transaction.atomic()
    def get(self, request, id=0,Company=0):
        try:
            with transaction.atomic():
                Check = TC_MaterialIssueWorkOrders.objects.filter(WorkOrder_id=id)
                # return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': str(Check.query)})
                if Check.exists():
                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Material Issue used in Material Issue', 'Data': []})
                else:
                    Query = T_MaterialIssue.objects.filter(id=id)
                    if Query.exists():
                        MaterialIssue_serializer = WorkOrderSerializerSecond(Query,many=True).data
                        MaterialIssueData = list()
                        # return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': BOM_Serializer})
                        ActualBomqty =0
                        for a in MaterialIssue_serializer:
                            Item = a['Item']['id']
                                # obatchwisestockquery = O_BatchWiseLiveStock.objects.filter(Item_id=Item).values('Item').annotate(actualStock=Sum('BaseUnitQuantity')).values('actualStock')
                            obatchwisestockquery=O_BatchWiseLiveStock.objects.raw(''' SELECT O_BatchWiseLiveStock.id,O_BatchWiseLiveStock.Item_id,SUM(O_BatchWiseLiveStock.BaseUnitQuantity) AS actualStock FROM O_BatchWiseLiveStock WHERE O_BatchWiseLiveStock.Item_id = %s GROUP BY O_BatchWiseLiveStock.Item_id''', [Item])
                            if not obatchwisestockquery:
                                StockQty =0.0
                            else:
                                StockQtySerialize_data = StockQtyserializerForMaterialIssue(obatchwisestockquery, many=True).data
                                StockQty = StockQtySerialize_data[0]['actualStock']
                            
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
                            
                            MaterialIssueData.append({
                                "id": a['id'],
                                "WorkOrderDate": a['WorkOrderDate'],
                                "Item":a['Item']['id'],
                                "ItemName":a['Item']['Name'],
                                "Unit": a['Unit']['id'],
                                "UnitName": a['Unit']['UnitID']['Name'],
                                "Bom": a['Bom'],
                                "Stock":StockQty,
                                "ActualBomqty": ActualBomqty,
                                "NumberOfLot": a['NumberOfLot'],
                                "Quantity":a["Quantity"],
                                "Company": a['Company']['id'],
                                "CompanyName":a['Company']['Name'],
                                "Party": a['Party']['id'],
                                "PartyName": a['Party']['Name'],
                                "EstimatedOutputQty": a['Quantity'],  
                                "WorkOrderItems":MaterialDetails,
                            })
                        return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': MaterialIssueData})
        except T_MaterialIssue.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Material Issue Not available', 'Data': []})
    
    @transaction.atomic()
    def put(self, request, id=0, Company=0):
        try:
            with transaction.atomic():
                MaterialIssueData = JSONParser().parse(request)
                # return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': Bomsdata })
                MaterialIssueDataByID = T_MaterialIssue.objects.get(id=id)
                # return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': str(BomsdataByID.query)})
                MaterialIssue_Serializer = MaterialIssueSerializer(MaterialIssueDataByID, data=MaterialIssueData)
                if MaterialIssue_Serializer.is_valid():
                    MaterialIssue_Serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Material IssueUpdated Successfully', 'Data': []})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': MaterialIssue_Serializer.errors, 'Data': []})
        except Exception as e:
                return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})
            
    @transaction.atomic()
    def delete(self, request, id=0,Company=0):
        try:
            with transaction.atomic():
                MaterialIssueItemdata=T_MaterialIssue.objects.all().filter(id=id)
                MaterialIssueItemdataserializer=MatetrialIssueSerializerForDelete(MaterialIssueItemdata,many=True).data
                
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Material Issue Deleted Successfully', 'Data': MaterialIssueItemdataserializer})
                O_BatchWiseLiveStockList=list()
                O_LiveBatchesList=list()
                for a in MaterialIssueItemdataserializer:
                    
                    BaseUnitQuantity=UnitwiseQuantityConversion(a['Item'],a['IssueQuantity'],0,0,0,0).GetBaseUnitQuantity(),
                   
                    jsonbody.append({
                    "Item": a['Item'],
                    "Quantity": a['IssueQuantity'],
                    "ItemExpiryDate":'2023-01-10',
                    "Unit": a['Unit'],
                    "BaseUnitQuantity": BaseUnitQuantity,
                    "OriginalBaseUnitQuantity": BaseUnitQuantity,
                    "MRP": "",
                    "Rate": 0,
                    "GST": 5,
                    "Party": 4,
                    "SystemBatchDate": a['SystemBatchDate'],
                    "SystemBatchCode": a['SystemBatchCode'],
                    "BatchDate": a['BatchDate'],
                    "BatchCode": a['BatchCode'],
                    "CreatedBy":1,
                    })

                    O_BatchWiseLiveStockList.append({
                    "Item": a['Item'],
                    "Quantity": a['Quantity'],
                    "Unit": a['Unit'],
                    "BaseUnitQuantity": BaseUnitQuantity,
                    "OriginalBaseUnitQuantity": BaseUnitQuantity,
                    "Party": Customer,
                    "CreatedBy":CreatedBy,
                    
                    })
                    O_LiveBatchesList.append({
                    
                    "ItemExpiryDate":date.today()+ datetime.timedelta(days = query2[0]['Days']),
                    "MRP": a['MRP'],
                    "Rate": a['Rate'],
                    "GST": a['GST'],
                    "SystemBatchDate": a['SystemBatchDate'],
                    "SystemBatchCode": a['SystemBatchCode'],
                    "BatchDate": a['BatchDate'],
                    "BatchCode": a['BatchCode'],
                    "O_BatchWiseLiveStockList" :O_BatchWiseLiveStockList                   
                    
                    })
                    bb=O_BatchWiseLiveStock.objects.create(jsonbody)
                    bb.save()
                
                MaterialIssuedata = T_MaterialIssue.objects.get(id=id)
                print('aaaaa')
                # MaterialIssuedata.delete()
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Material Issue Deleted Successfully', 'Data': []})
        except T_MaterialIssue.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Material Issue Not available', 'Data': []})
        except IntegrityError:
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Material Issue used in another table', 'Data': []})  
        except Exception as  e:
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': e, 'Data': []})   
                            