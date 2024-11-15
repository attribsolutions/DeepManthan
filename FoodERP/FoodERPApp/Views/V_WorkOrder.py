from django.http import JsonResponse
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
# from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, transaction
from rest_framework.parsers import JSONParser
from ..Views.V_TransactionNumberfun import GetMaxNumber, GetPrifix
from django.db.models import Sum
from ..Serializer.S_Orders import *
from ..Serializer.S_Bom import *
from ..Serializer.S_WorkOrder import *
from ..models import *


class BomDetailsView(CreateAPIView):

    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                BomDetailsdata = JSONParser().parse(request)
                BomID = BomDetailsdata['Bom']
                ItemID = BomDetailsdata['Item']
                GetQuantity = BomDetailsdata['Quantity']
                Party = BomDetailsdata['Party']
                Query = M_BillOfMaterial.objects.filter(id=BomID)
                
                if Query.exists():
                    BOM_Serializer = M_BOMSerializerSecond001(
                        Query, many=True).data
                    BillofmaterialData = list()
                    # return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': BOM_Serializer})
                    for a in BOM_Serializer:
                        
                        Stock = float(GetO_BatchWiseLiveStock(
                            a['Item']['id'], Party))
                        StockintoSelectedUnit = UnitwiseQuantityConversion(
                            a['Item']['id'], Stock, 0, 0, a['Unit']['id'], 0,1).ConvertintoSelectedUnit()
                        MaterialDetails = list()
                        total = 0
                        for b in a['BOMItems']:
                            Item = b['Item']['id']
                            Stock = float(GetO_BatchWiseLiveStock(
                                b['Item']['id'], Party))

                            StockQty = UnitwiseQuantityConversion(
                                b['Item']['id'], Stock, 0, 0, b['Unit']['id'], 0,1).ConvertintoSelectedUnit()

                            Qty = float(b['Quantity']) / \
                                float(a['EstimatedOutputQty'])
                            ActualQty = float(GetQuantity * Qty)
                            MaterialDetails.append({
                                "id": b['id'],
                                "Item": b['Item']['id'],
                                "ItemName": b['Item']['Name'],
                                "Unit": b['Unit']['id'],
                                "UnitName": b['Unit']['BaseUnitConversion'],
                                "StockQuantity": StockQty,
                                "BomQuantity": b['Quantity'],
                                "Quantity": round(ActualQty,3)
                            })
                        BillofmaterialData.append({
                            "id": a['id'],
                            "IsActive": a['IsActive'],
                            "Item": a['Item']['id'],
                            "ItemName": a['Item']['Name'],
                            "Stock": StockintoSelectedUnit,
                            "EstimatedOutputQty": round(GetQuantity, 3),
                            "Unit": a['Unit']['id'],
                            "UnitName": a['Unit']['BaseUnitConversion'],
                            "BOMItems": MaterialDetails                            
                        })
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': BillofmaterialData[0]})
        except M_BillOfMaterial.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Bill Of Material Not available', 'Data': []})


class WorkOrderList(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                WorkOrderdata = JSONParser().parse(request)
                FromDate = WorkOrderdata['FromDate']
                ToDate = WorkOrderdata['ToDate']
                if(FromDate=="" and ToDate=="" ):                    
                    query = T_WorkOrder.objects.filter(~Q(Status=2))                    
                else:                    
                    query = T_WorkOrder.objects.filter( WorkOrderDate__range=[FromDate, ToDate])
                if query:
                    WorkOrder_serializerdata = WorkOrderSerializerSecond(
                        query, many=True).data
                    
                    # return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':'','Data': WorkOrder_serializerdata})
                    WorkOrderListData = list()
                    for a in WorkOrder_serializerdata:
                        Percentage = 0
                        RemaningQty = a["RemaninQuantity"]
                        NumberOFLots =a['RemainNumberOfLot'] 
                        Query=TC_MaterialIssueWorkOrders.objects.filter(WorkOrder_id=a['id']).select_related('MaterialIssue').values('MaterialIssue__id')
                        
                        MaterialIssueList = list()
                        for b in Query:                            
                            MaterialIssueList.append(b['MaterialIssue__id'])                            
                            if not MaterialIssueList:
                                Percentage = 0 
                            else:
                                y=tuple(MaterialIssueList)  
                                Itemsquery = T_MaterialIssue.objects.filter(id__in=y).aggregate(Sum('LotQuantity'))                                
                                Percentage = (float(Itemsquery['LotQuantity__sum'])/float(a["Quantity"]) )*100
                                # NoOfLot=T_MaterialIssue.objects.filter(id__in=y).values('NumberOfLot')                                
                                # NumberOFLots=a['NumberOfLot']- NoOfLot[0]['NumberOfLot']                           
                                # NO=int(NoOfLot[0]['NumberOfLot'])                               
                                # NoQty=float(a["Quantity"])                                   
                                # if NO >0:                              
                                #     RemaningQty=NoQty/NO
                                # else:
                                #     RemaningQty=NoQty                                
                        WorkOrderListData.append({
                            "id": a['id'],
                            "WorkOrderDate": a['WorkOrderDate'],
                            "WorkOrderNumber": a['WorkOrderNumber'],
                            "FullWorkOrderNumber": a['FullWorkOrderNumber'],
                            "Item": a['Item']['id'],
                            "ItemName": a['Item']['Name'],
                            "Unit": a['Unit']['id'],
                            "UnitName": a['Unit']['BaseUnitConversion'],
                            "Bom": a['Bom'],
                            "NumberOfLot": a['NumberOfLot'],
                            "RemainingLot":NumberOFLots,                            
                            "Quantity": a["Quantity"],
                            "RemaningQty":RemaningQty,
                            "Percentage":Percentage,
                            "Company": a['Company']['id'],
                            "CompanyName": a['Company']['Name'],
                            "EstimatedOutputQty": a['Quantity'],
                            "CreatedOn": a['CreatedOn'],
                            "CreatedBy": a['CreatedBy'],
                            "Status":a['Status'],
                        })
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': WorkOrderListData})
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Record Not Found', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})


class WorkOrderView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                        
                        MultipleWorkOrderData = JSONParser().parse(request)  
                        if not isinstance(MultipleWorkOrderData, list):
                            return JsonResponse({'StatusCode': 400, 'Status': False, 'Message': 'Expected a list of items', 'Data': []})                      
                        # CustomPrint(MultipleWorkOrderData)
                        WorkOrders=[]
                        for index,WorkOrderData in enumerate(MultipleWorkOrderData):
                            # CustomPrint(WorkOrderData)
                            Party = WorkOrderData['Party']
                            WorkOrderDate = WorkOrderData['WorkOrderDate']
                            #==================Max Work Order ==================
                            a = GetMaxNumber.GetWorkOrderNumber(Party, WorkOrderDate)
                            # return JsonResponse({'StatusCode': 200, 'Status': True,   'Data':[a] })
                            aa=index+a                            
                            WorkOrderData['WorkOrderNumber'] = aa
                            '''Get Order Prifix '''
                            b = GetPrifix.GetWorkOrderPrifix(Party)
                            WorkOrderData['FullWorkOrderNumber'] = b+""+str(aa)                
                            #=====================================================
                            WorkOrderData['Status']=0
                            WorkOrderData['RemainNumberOfLot']=WorkOrderData['NumberOfLot']
                            WorkOrderData['RemaninQuantity']=WorkOrderData['Quantity'] 
                            WorkOrders.append(WorkOrderData)
                            # CustomPrint(WorkOrders)
                        # return JsonResponse({'StatusCode': 200, 'Status': True,   'Data':[WorkOrders] })
                        WorkOrder_Serializer = WorkOrderSerializer(data=WorkOrders,many=True) 
                        if WorkOrder_Serializer.is_valid():                           
                            # work_order_instances.append(WorkOrder_Serializer)
                            WorkOrder_Serializer.save()
                            return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Work Order Save Successfully', 'Data': []})
                        else:
                            transaction.set_rollback(True)
                            return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': WorkOrder_Serializer.errors, 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})


class WorkOrderViewSecond(RetrieveAPIView):

    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request, id=0):
        try:
            with transaction.atomic():
                
                    Check = TC_MaterialIssueWorkOrders.objects.filter(WorkOrder_id=id)
                    if Check.exists():
                        return JsonResponse({'StatusCode': 226, 'Status': True, 'Message': 'Work Order used in Material Issue', 'Data': []})
                    Query = T_WorkOrder.objects.filter(id=id)
                    if Query.exists():
                        WorkOrder_serializer = WorkOrderSerializerSecond(
                            Query, many=True).data
                        # CustomPrint(WorkOrder_serializer)
                        WorkOrderData = list()
                        # return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': BOM_Serializer})
                        ActualBomqty = 0
                        for a in WorkOrder_serializer:
                            Item = a['Item']['id']
                            CustomPrint(Item)                            
                            obatchwisestockquery = O_BatchWiseLiveStock.objects.raw(
                                ''' SELECT O_BatchWiseLiveStock.id,O_BatchWiseLiveStock.Item_id,SUM(O_BatchWiseLiveStock.BaseUnitQuantity) AS actualStock FROM O_BatchWiseLiveStock WHERE O_BatchWiseLiveStock.Item_id = %s GROUP BY O_BatchWiseLiveStock.Item_id''', [Item])
                            # CustomPrint(obatchwisestockquery.query)
                            if not obatchwisestockquery:
                                StockQty = 0.0
                            else:
                                StockQtySerialize_data = StockQtyserializer(
                                    obatchwisestockquery, many=True).data
                                StockQty = StockQtySerialize_data[0]['actualStock']
                            CustomPrint(StockQty)
                            ActualBomqty = float(
                                a['Quantity']) / float(a['NumberOfLot'])
                            MaterialDetails = list()
                            for b in a['WorkOrderItems']:
                               
                                obatchwisestockquery1 = O_BatchWiseLiveStock.objects.raw(
                                ''' SELECT O_BatchWiseLiveStock.id,O_BatchWiseLiveStock.Item_id,SUM(O_BatchWiseLiveStock.BaseUnitQuantity) AS actualStock FROM O_BatchWiseLiveStock WHERE O_BatchWiseLiveStock.Item_id = %s GROUP BY O_BatchWiseLiveStock.Item_id''', [b['Item']['id']])                              
                                if not obatchwisestockquery1:
                                    StockQty1 = 0.0
                                else:
                                    StockQtySerialize_data = StockQtyserializer(
                                    obatchwisestockquery1, many=True).data
                                    StockQty1 = StockQtySerialize_data[0]['actualStock']
                                
                                MaterialDetails.append({
                                    "id": b['id'],
                                    "Item": b['Item']['id'],
                                    "ItemName": b['Item']['Name'],
                                    "Unit": b['Unit']['id'],
                                    "UnitName": b['Unit']['BaseUnitConversion'],
                                    "BomQuantity": b['BomQuantity'],
                                    "Quantity": b['Quantity'],
                                    "StockQuantity":StockQty1
                                })
                            
                            WorkOrderData.append({
                                "id": a['id'],
                                "WorkOrderDate": a['WorkOrderDate'],
                                "WorkOrderNumber": a['WorkOrderNumber'],
                                "FullWorkOrderNumber": a['FullWorkOrderNumber'],
                                "Item": a['Item']['id'],
                                "ItemName": a['Item']['Name'],
                                "Unit": a['Unit']['id'],
                                "UnitName": a['Unit']['BaseUnitConversion'],
                                "Bom": a['Bom'],
                                "Stock": StockQty,
                                "ActualBomqty": ActualBomqty,
                                "NumberOfLot": a['NumberOfLot'],
                                "Quantity": a["Quantity"],
                                "Company": a['Company']['id'],
                                "CompanyName": a['Company']['Name'],
                                "Party": a['Party']['id'],
                                "PartyName": a['Party']['Name'],
                                "EstimatedOutputQty": a['Quantity'],
                                "WorkOrderItems": MaterialDetails,
                                "Status":a['Status'],
                                "RemainNumberOfLot":a['RemainNumberOfLot'],
                                "RemaninQuantity":a['RemaninQuantity']                                
                                
                            })
                        return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': WorkOrderData})
        except T_WorkOrder.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Work Orders Not available', 'Data': []})

    @transaction.atomic()
    def put(self, request, id=0, Company=0):
        try:
            with transaction.atomic():
                WorkOrderData = JSONParser().parse(request)
                
                
                WorkOrderDataByID = T_WorkOrder.objects.get(id=id)
                
               
                WorkOrder_Serializer = WorkOrderSerializer(
                    WorkOrderDataByID, data=WorkOrderData[0])
                
                # print(WorkOrder_Serializer)
                if WorkOrder_Serializer.is_valid():
                    WorkOrder_Serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Work Order Updated Successfully', 'Data': []})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': WorkOrder_Serializer.errors, 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})

    @transaction.atomic()
    def delete(self, request, id=0, Company=0):
        try:
            with transaction.atomic():
                WorkOrderdata = T_WorkOrder.objects.get(id=id)
                WorkOrderdata.delete()
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Work Order Deleted Successfully', 'Data': []})
        except T_WorkOrder.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Work Order Not available', 'Data': []})
        except IntegrityError:
            return JsonResponse({'StatusCode': 226, 'Status': True, 'Message': 'Work Order used in another table', 'Data': []})


