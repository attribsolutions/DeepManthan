from django.http import JsonResponse
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
# from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import transaction
from rest_framework.parsers import JSONParser
from ..Views.V_TransactionNumberfun import GetMaxNumber, GetPrifix,SystemBatchCodeGeneration
from ..Serializer.S_WorkOrder import *
from ..Serializer.S_MaterialIssue import *
from ..models import *
from datetime import datetime, timedelta
from django.db.models import Sum


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
                # NoOfLots=WorkOrderDetailsdata['NoOfLots']
                # CustomPrint(NoOfLots)
                # today = datetime.now().date()
                Query = T_WorkOrder.objects.filter(
                    id=WorkOrderID, Item_id=ItemID, Company_id=CompanyID, Party_id=PartyID)  
                # CustomPrint(Query.query)
                # return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': str(Query.query)})
                if Query.exists():
                    WorkOrder_Serializer = WorkOrderSerializerSecond(
                        Query, many=True).data                    
                    # return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': WorkOrder_Serializer})
                    # print(WorkOrder_Serializer)
                    # productionQty = (T_Production.objects.filter(Item=ItemID, ProductionDate=today)
                    #                 .aggregate(total=Sum('ActualQuantity'))['total'] or 0
                    #             )
                    for a in WorkOrder_Serializer:
                        MaterialDetails = list()
                        workorderqty = a['Quantity'] 
                        # unit_id=a['Unit']['UnitID']['id']                       
                        # query3 = O_DateWiseLiveStock.objects.filter(
                        # StockDate=today, Party=PartyID, Item=ItemID).values('ClosingBalance', 'Unit_id')                        
                        # if query3:

                        #     ClosingBalance = UnitwiseQuantityConversion(
                        #         ItemID, query3[0]['ClosingBalance'], 0, query3[0]['Unit_id'], 0, unit_id, 0).ConvertintoSelectedUnit() 
                            
                            
                        # else:
                        #     ClosingBalance = 0.00
                            
                        for b in a['WorkOrderItems']:
                            
                            Item = b['Item']['id']
                            # print(Item)
                            Child_Item_BOM_id= list(M_BillOfMaterial.objects.filter(Item_id=Item,IsDelete=0).values('id'))
                            if Child_Item_BOM_id:
                                Child_Item_BOM = Child_Item_BOM_id[0]['id']
                            else:
                                Child_Item_BOM = None 
                            # print(Child_Item_BOM)
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
                                        "ObatchwiseQuantity": StockQty,
                                        "BaseUnitQuantity": c['Quantity'],
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
                                "OriginalWorkOrderQty":b['Quantity'],
                                # "ProductionQty":productionQty,
                                # "StockQty":ClosingBalance,
                                "Bom_id":Child_Item_BOM,
                                "BatchesData": stockDatalist 
                                                             
                                # "Status":a['Status']
                            })
                            # CustomPrint(MaterialDetails)
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
                Party=MaterialIsssuedata['Party']
                today = datetime.now().date()
                if(FromDate=="" and ToDate=="" ): 
                    query = T_MaterialIssue.objects.filter(~Q(Status=2),Party_id=Party,IsDelete=0) 
                else: 
                    query = T_MaterialIssue.objects.filter(MaterialIssueDate__range=[FromDate, ToDate],Party_id=Party,IsDelete=0)                 
                if query:
                    MaterialIsssue_serializerdata = MatetrialIssueSerializerSecond( query, many=True).data
                    
                    # return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':'','Data': MaterialIsssue_serializerdata})
                    MaterialIsssueListData = list()
                   
                    for a in MaterialIsssue_serializerdata:
                        # if(a['RemainNumberOfLot']!=0):                            
                        #     if(a['NumberOfLot']!=a['RemainNumberOfLot']):
                        #         # print(a['RemainNumberOfLot'],a['NumberOfLot'])
                        #         Percentage=(1-float(a['RemainNumberOfLot'])/float(a['NumberOfLot'])*100) 
                            
                        #         # Percentage=100-Percentage
                        #     else:
                        #         Percentage=0
                        # else:  
                        #     Percentage=100   
                        total_lot = float(a['NumberOfLot'])
                        remaining_lot = float(a['RemainNumberOfLot'])

                        if remaining_lot == 0:
                            Percentage = 100  
                        elif remaining_lot == total_lot:
                            Percentage = 0  
                        else:
                            Percentage = round((1 - (remaining_lot / total_lot)) * 100, 2)
                            
                        ItemShelflife=MC_ItemShelfLife.objects.filter(Item_id=a['Item']['id'],IsDeleted=0).values('Days')
                        
                        if ItemShelflife:
                            today = datetime.today()
                            shelf_date = today + timedelta(days=ItemShelflife[0]['Days'])
                            shelf_date = shelf_date.strftime("%Y-%m-%d")
                        else:
                            shelf_date = today                            
                        
                        Productionquery1 = T_MaterialIssue.objects.filter(Item_id=a['Item']['id']).values('id')                
                        BatchCode = SystemBatchCodeGeneration.GetGrnBatchCode(a['Item']['id'], a['Party']['id'], Productionquery1.count())                     
                        productionQty = (T_Production.objects.filter(Item=a['Item']['id'], ProductionDate=today)
                                    .aggregate(total=Sum('ActualQuantity'))['total'] or 0
                                )
                        UnitID = MC_ItemUnits.objects.filter(id=a['Unit']['id']).values('UnitID_id')                        
                        unit_id=UnitID[0]['UnitID_id']    
                        # print(unit_id)                   
                        query3 = O_DateWiseLiveStock.objects.filter(
                        StockDate=today, Party=Party, Item=a['Item']['id']).values('ClosingBalance', 'Unit_id')                        
                        if query3:

                            ClosingBalance = UnitwiseQuantityConversion(
                                a['Item']['id'], query3[0]['ClosingBalance'], 0, query3[0]['Unit_id'], 0, unit_id, 0).ConvertintoSelectedUnit() 
                            # print(ClosingBalance)
                            
                        else:
                            ClosingBalance = 0.00
                        
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
                            "Status":a['Status'],
                            "ProductionQty":productionQty,
                            "StockQty":ClosingBalance,
                            "PrintedBatchCode":BatchCode,
                            "Percentage":Percentage ,
                            "ShelfDate":shelf_date                       
                           
                        })                        
                        # CustomPrint(MaterialIsssueListData)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': MaterialIsssueListData})
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Record Not Found', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})


class MaterialIssueView(CreateAPIView):

    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                MaterialIssueData = JSONParser().parse(request)               
                # CustomPrint(MaterialIssueData)
                Party = MaterialIssueData['Party']
               
                MaterialIssueDate = MaterialIssueData['MaterialIssueDate']
                NoOfLotsQty=MaterialIssueData['NumberOfLot']
                NoOfQuantity=MaterialIssueData['LotQuantity']
                # CustomPrint(NoOfQuantity)
                a = GetMaxNumber.GetMaterialIssueNumber(
                    Party, MaterialIssueDate)
               
                MaterialIssueData['MaterialIssueNumber'] = a
                '''Get Order Prifix '''
                b = GetPrifix.GetMaterialIssuePrifix(Party)
                MaterialIssueData['FullMaterialIssueNumber'] = b+""+str(a)
                MaterialIssueData['Status']=0
                MaterialIssueData['RemainNumberOfLot']=MaterialIssueData['NumberOfLot']
                # print(MaterialIssueData['RemainNumberOfLot'])
                
                MaterialIssueData['RemaninLotQuantity']=MaterialIssueData['LotQuantity']
                # print(MaterialIssueData['RemaninLotQuantity'])
                
                MaterialIssueItems = MaterialIssueData['MaterialIssueItems']
                MaterialWorkOrder=MaterialIssueData['MaterialIssueWorkOrder']   
                for MWorkOrder in  MaterialWorkOrder:     
                     WorkOrderID= MWorkOrder['WorkOrder']                  
                WorkOrderNOofLots = T_WorkOrder.objects.filter(id=WorkOrderID).values('RemainNumberOfLot','RemaninQuantity')
                if WorkOrderNOofLots:
                    RemaningLots=WorkOrderNOofLots[0]['RemainNumberOfLot']
                    RamaningQty = float(WorkOrderNOofLots[0]['RemaninQuantity'])          
                    
                O_BatchWiseLiveStockList = list()
               
                for MaterialIssueItem in MaterialIssueItems:
                    # CustomPrint(MaterialIssueItem)
                    BaseUnitQuantity = UnitwiseQuantityConversion(
                        MaterialIssueItem['Item'], 
                        MaterialIssueItem['IssueQuantity'], 
                        MaterialIssueItem['Unit'], 0, 0, 0, 1).GetBaseUnitQuantity()
                   
                    O_BatchWiseLiveStockList.append({
                        "Quantity": MaterialIssueItem['BatchID'],
                        "Item": MaterialIssueItem['Item'],
                        "BaseUnitQuantity": BaseUnitQuantity
                    })                    
                    
                MaterialIssueData.update(
                    {"obatchwiseStock": O_BatchWiseLiveStockList })
                
               
                MaterialIssue_Serializer = MaterialIssueSerializer(
                    data=MaterialIssueData)
                # return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': MaterialIssue_Serializer})
                # CustomPrint(MaterialIssue_Serializer)                
                if MaterialIssue_Serializer.is_valid():
                    MaterialIssue_Serializer.save()                     
                    RemainNumberOfLot=float(RemaningLots)-float(NoOfLotsQty)
                    RemaninQuantity=float(RamaningQty)-float(NoOfQuantity) 
                    # if(RemaningLots==NoOfLotsQty):        
                    if RemainNumberOfLot == 0:              
                       query = T_WorkOrder.objects.filter(id=WorkOrderID).update(Status=2,RemainNumberOfLot=RemainNumberOfLot,RemaninQuantity=RemaninQuantity)
                    else:                       
                       query = T_WorkOrder.objects.filter(id=WorkOrderID).update(Status=1,RemainNumberOfLot=RemainNumberOfLot,RemaninQuantity=RemaninQuantity)                       
                        
                    
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Material Issue Save Successfully', 'Data': []})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': MaterialIssue_Serializer.errors, 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': Exception(e), 'Data': []})


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
        


    
    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication
    
    @transaction.atomic()
    def post(self, request):       
        ItemID = request.data['ItemID']
        current_date = datetime.now().date() 
        # CustomPrint(ItemID) 
        # CustomPrint(current_date)        
        try:
            with transaction.atomic():
                # CustomPrint("shruti")          
                ProductionItemCount=T_Production.objects.filter(Item_id=ItemID, ProductionDate=current_date).count()
                # CustomPrint(ProductionItemCount)
                               
                CountList = []                  
                for a in ProductionItemCount:                       
                        CountList.append({
                            "ProductionItemCount":ProductionItemCount,
                        })
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': CountList})
        except Exception as e:
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': Exception(e), 'Data': []})


   
    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                MaterialIssueItemdata = T_MaterialIssue.objects.all().filter(id=id)
                
                MaterialIssueItemdataserializer = MatetrialIssueSerializerForDelete(
                    MaterialIssueItemdata, many=True).data
                CustomPrint(MaterialIssueItemdataserializer)
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
                    UpdateQuery=O_BatchWiseLiveStock.objects.filter(LiveBatche=a['LiveBatchID']).update(BaseUnitQuantity = float(selectQuery[0]['BaseUnitQuantity'] )+float(BaseUnitQuantity11))
                    
                # MaterialIssueItemdataserializer = obatchwiseStockSerializerfordelete(
                #     data=O_BatchWiseLiveStockList)

                # if MaterialIssueItemdataserializer.is_valid():
                #     MaterialIssueItemdataserializer.save()
                MaterialissueworkorderID=TC_MaterialIssueWorkOrders.objects.filter(MaterialIssue_id=id).values('WorkOrder_id')                
                workOrderID=MaterialissueworkorderID[0]['WorkOrder_id']
                MLot=MaterialIssueItemdataserializer[0]['NumberOfLot']
                MQuantity=MaterialIssueItemdataserializer[0]['LotQuantity']
                query1 = T_WorkOrder.objects.filter(id=workOrderID).values('RemainNumberOfLot','RemaninQuantity','NumberOfLot')
                ActualLot=float(query1[0]['RemainNumberOfLot'] ) + float(MLot)
                ActualQty=float(query1[0]['RemaninQuantity'])+float(MQuantity)
                orignalLot=query1[0]['NumberOfLot']                
                if(orignalLot==ActualLot):
                     Status=0
                else:
                     Status=1
                query = T_WorkOrder.objects.filter(id=workOrderID).update(Status=Status,RemainNumberOfLot=ActualLot,RemaninQuantity=ActualQty)
                # MaterialIssuedata = T_MaterialIssue.objects.get(id=id)
                # MaterialIssuedata.delete()
                MaterialIssuedata = T_MaterialIssue.objects.filter(id=id).update(IsDelete = 1)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Material Issue Delete Successfully', 'Data': []})
                # else:
                #     transaction.set_rollback(True)
                #     return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': MaterialIssueItemdataserializer.errors, 'Data': []})
        except T_MaterialIssue.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Material Issue Not available', 'Data': []})
        except IntegrityError:
            return JsonResponse({'StatusCode': 226, 'Status': True, 'Message': 'Material Issue used in another table', 'Data': []})



    
