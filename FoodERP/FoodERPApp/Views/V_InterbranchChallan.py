from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
# from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import transaction
from rest_framework.parsers import JSONParser
from ..Serializer.S_Demands import *
from ..Views.V_TransactionNumberfun import GetMaxNumber, GetPrifix
from ..Serializer.S_InterbranchChallan import *
from ..Serializer.S_Orders import *

from ..models import  *


class DemandDetailsForIBChallan(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    def post(self, request, id=0):
        try:
            with transaction.atomic():
               
                Orderdata = JSONParser().parse(request)
                FromDate = Orderdata['FromDate']
                Party = Orderdata['Party']
                Customer = Orderdata['Customer']
                POOrderIDs = Orderdata['OrderIDs']
                Order_list = POOrderIDs.split(",")
                OrderItemDetails = list()
                Orderdata = list()
               
                if POOrderIDs != '':
                    # OrderQuery=T_Demands.objects.raw("SELECT T_Demands.Supplier_id id,m_parties.Name SupplierName,sum(T_Demands.DemandAmount) OrderAmount ,T_Demands.Customer_id CustomerID FROM T_Demands join m_parties on m_parties.id=T_Demands.Supplier_id where T_Demands.id IN %s group by T_Demands.Supplier_id;",[Order_list])
                    # OrderSerializedata = OrderSerializerForGrn(OrderQuery,many=True).data
                    OrderItemQuery=TC_DemandItems.objects.filter(Demand__in=Order_list,IsDeleted=0).order_by('Item')
                    OrderItemSerializedata=TC_DemandItemsSerializerSecond(OrderItemQuery,many=True).data
                else:
                    query = T_Demands.objects.filter(DemandDate=FromDate,Supplier=Party,Customer=Customer)
                    Serializedata = OrderserializerforIBChallan(query,many=True).data
                    Order_list = list()
                    for x in Serializedata:
                        Order_list.append(x['id'])
                        
                    OrderQuery=T_Demands.objects.raw("SELECT T_Demands.Supplier_id id,M_Parties.Name SupplierName,sum(T_Demands.DemandAmount) OrderAmount ,T_Demands.Customer_id CustomerID FROM T_Demands join M_Parties on M_Parties.id=T_Demands.Supplier_id where T_Demands.id IN %s group by T_Demands.Supplier_id;",[Order_list])
                    OrderSerializedata = OrderSerializerForGrn(OrderQuery,many=True)
                    OrderItemQuery=TC_DemandItems.objects.filter(Demand__in=Order_list,IsDeleted=0).order_by('Item')
                    OrderItemSerializedata=TC_DemandItemsSerializerSecond(OrderItemQuery,many=True).data
                       
                # return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': OrderItemSerializedata})
                for b in OrderItemSerializedata:
                    
                    Item= b['Item']['id']
                    obatchwisestockquery= O_BatchWiseLiveStock.objects.filter(Item_id=Item,Party_id=Party,BaseUnitQuantity__gt=0)
                   
                    if obatchwisestockquery == "":
                        StockQtySerialize_data =[]
                    else:
                        StockQtySerialize_data = StockQtyserializerForIBChallan(obatchwisestockquery, many=True).data
                        stockDatalist = list()
                        for d in StockQtySerialize_data:
                            stockDatalist.append({
                                "id": d['id'],
                                "Item":d['Item']['id'],
                                "BatchDate":d['LiveBatche']['BatchDate'],
                                "BatchCode":d['LiveBatche']['BatchCode'],
                                "SystemBatchDate":d['LiveBatche']['SystemBatchDate'],
                                "SystemBatchCode":d['LiveBatche']['SystemBatchCode'],
                                "LiveBatche" : d['LiveBatche']['id'],
                                "LiveBatcheMRPID" : d['LiveBatche']['MRP']['id'],
                                "LiveBatcheGSTID" : d['LiveBatche']['GST']['id'],
                                "Rate":d['LiveBatche']['Rate'],
                                "MRP" : d['LiveBatche']['MRP']['MRP'],
                                "GST" : d['LiveBatche']['GST']['GSTPercentage'],
                                "UnitName":d['Unit']['BaseUnitConversion'], 
                                "BaseUnitQuantity":d['BaseUnitQuantity']   
                                })
                    query = MC_ItemUnits.objects.filter(Item_id=Item,IsDeleted=0)
                    # print(query.query)
                    if query.exists():
                        Unitdata = Mc_ItemUnitSerializerThird(query, many=True).data
                        UnitDetails = list()
                        for c in Unitdata:
                           
                            UnitDetails.append({
                            "Unit": c['id'],
                            "UnitName": c['BaseUnitConversion'],
                            "ConversionUnit": c['BaseUnitQuantity'],
                            "Unitlabel": c['UnitID']['Name']
                        })
                        # return JsonResponse({'StatusCode': 200, 'Status': True, 'Data':Unitdata})
                        
                    OrderItemDetails.append({
                         
                        "id": b['id'],
                        "Item": b['Item']['id'],
                        "ItemName": b['Item']['Name'],
                        "Quantity": b['Quantity'],
                        "MRP": b['MRP']['id'],
                        "MRPValue": b['MRP']['MRP'],
                        "Rate": b['Rate'],
                        "Unit": b['Unit']['id'],
                        "UnitName": b['Unit']['BaseUnitConversion'],
                        "ConversionUnit": b['Unit']['BaseUnitQuantity'],
                        "BaseUnitQuantity": b['BaseUnitQuantity'],
                        "GST": b['GST']['id'],
                        "HSNCode": b['GST']['HSNCode'],
                        "GSTPercentage": b['GST']['GSTPercentage'],
                        "Margin": b['Margin']['id'],
                        "MarginValue": b['Margin']['Margin'],
                        "BasicAmount": b['BasicAmount'],
                        "GSTAmount": b['GSTAmount'],
                        "CGST": b['CGST'],
                        "SGST": b['SGST'],
                        "IGST": b['IGST'],
                        "CGSTPercentage": b['CGSTPercentage'],
                        "SGSTPercentage": b['SGSTPercentage'],
                        "IGSTPercentage": b['IGSTPercentage'],
                        "Amount": b['Amount'],
                        "UnitDetails":UnitDetails,
                        "StockDetails":stockDatalist
                    })
                Orderdata.append({
                    "OrderIDs":Order_list,
                    "OrderItemDetails":OrderItemDetails
                   })         
            return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': Orderdata[0]})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})
        

class InterBranchChallanListFilterView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request, id=0):
        try:
            with transaction.atomic():
                IBChallandata = JSONParser().parse(request)
                FromDate = IBChallandata['FromDate']
                ToDate = IBChallandata['ToDate']
                Customer = IBChallandata['Customer']
                Party = IBChallandata['Party']
                IBType = IBChallandata['IBType']
                if (IBType == "IBInvoice" ): # InterBranch Sales Order 
                    if(Customer == ''):
                       query = T_InterbranchChallan.objects.filter(IBChallanDate__range=[FromDate, ToDate], Party=Party)
                    else:
                        query = T_InterbranchChallan.objects.filter(IBChallanDate__range=[FromDate, ToDate], Customer_id=Customer, Party=Party)  
                elif(IBType == "IBGRN"):
                    if(Customer == ''): # InterBranch Purchase Order
                        query = T_InterbranchChallan.objects.filter(IBChallanDate__range=[FromDate, ToDate], Customer_id=Party)
                    else:
                        query = T_InterbranchChallan.objects.filter(IBChallanDate__range=[FromDate, ToDate], Customer_id=Party, Party=Customer)
                else:
                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Record Not Found', 'Data': []})
                  
                   
                # return JsonResponse({'query': str(Orderdata.query)})
                if query:
                    IBChallan_serializer = IBChallanSerializerSecond(query, many=True).data
                    # return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':'','Data': Order_serializer})
                    IBChallanListData = list()
                    for a in IBChallan_serializer:
                        IBChallanListData.append({
                            "id": a['id'],
                            "InvoiceDate": a['IBChallanDate'],
                            "FullInvoiceNumber": a['FullIBChallanNumber'],
                            "CustomerID": a['Customer']['id'],
                            "Customer": a['Customer']['Name'],
                            "PartyID": a['Party']['id'],
                            "Party": a['Party']['Name'],
                            "GrandTotal": a['GrandTotal'],
                            "RoundOffAmount": a['RoundOffAmount'], 
                            "CreatedOn": a['CreatedOn']  
                        })
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': IBChallanListData})
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Record Not Found', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})


class InterBranchChallanView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication
    
    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                IBChallandata = JSONParser().parse(request)
                Party = IBChallandata['Party']
                IBChallanDate = IBChallandata['IBChallanDate']
                # ==========================Get Max IBChallan Number=====================================================
                a = GetMaxNumber.GetIBChallanNumber(Party,IBChallanDate)
                IBChallandata['IBChallanNumber'] = a
                b = GetPrifix.GetIBChallanPrifix(Party)
                IBChallandata['FullIBChallanNumber'] = str(b)+""+str(a)
                #================================================================================================== 
                IBChallanItems = IBChallandata['IBChallanItems']
                
                O_BatchWiseLiveStockList=list()
                for IBChallanItem in IBChallanItems:
                    O_BatchWiseLiveStockList.append({
                        "Quantity" : IBChallanItem['BatchID'],
                        "Item" : IBChallanItem['Item'],
                        "BaseUnitQuantity" : IBChallanItem['Quantity']
                    })
                        
                IBChallandata.update({"obatchwiseStock":O_BatchWiseLiveStockList}) 
                
                IBChallan_serializer = IBChallanSerializer(data=IBChallandata)
                if IBChallan_serializer.is_valid():
                    IBChallan_serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True,  'Message': 'InterBranch Challan Save Successfully', 'Data':[]})
                return JsonResponse({'StatusCode': 406, 'Status': True,  'Message': IBChallan_serializer.errors, 'Data':[]})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})
    
class InterBranchChallanViewSecond(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                IBChallandata=T_InterbranchChallan.objects.all().filter(id=id)
                IBChallandataserializer=IBChallanSerializerForDelete(IBChallandata,many=True).data
                # return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'IBChallan Delete Successfully', 'Data':IBChallandataserializer})

                O_BatchWiseLiveStockList=dict()
                
                for a in IBChallandataserializer[0]['IBChallanItems']:
                    BaseUnitQuantity11=UnitwiseQuantityConversion(a['Item'],a['Quantity'],a['Unit'],0,0,0,0).GetBaseUnitQuantity()
                    
                    # O_BatchWiseLiveStockList.update({
                    # "Item": a['Item'],
                    # "Quantity": a['Quantity'],
                    # "Unit": a['Unit'],
                    # "BaseUnitQuantity": BaseUnitQuantity,
                    # "OriginalBaseUnitQuantity": BaseUnitQuantity,
                    # "Party": IBChallandataserializer[0]['Party'],
                    # "LiveBatche" : a['LiveBatch'],
                    # "CreatedBy":1,
                    # })

                selectQuery=O_BatchWiseLiveStock.objects.filter(LiveBatche=a['LiveBatch']).values('BaseUnitQuantity')

                UpdateQuery=O_BatchWiseLiveStock.objects.filter(LiveBatche=a['LiveBatch']).update(BaseUnitQuantity = int(selectQuery[0]['BaseUnitQuantity'] )+int(BaseUnitQuantity11))
                    
                # BatchItemdataserializer=obatchwiseStockSerializerfordelete(data=O_BatchWiseLiveStockList)
                
                # if BatchItemdataserializer.is_valid():
                #    BatchItemdataserializer.save()
                  
                IBChallandata = T_InterbranchChallan.objects.get(id=id)
                IBChallandata.delete()
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'IBChallan Delete Successfully', 'Data':[]})
                # else:
                #     transaction.set_rollback(True)
                #     return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': BatchItemdataserializer.errors, 'Data': []})

        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})   
                               