import datetime
from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
# from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, transaction
from rest_framework.parsers import JSONParser
from ..Views.V_TransactionNumberfun import GetMaxNumber, GetPrifix
from ..Serializer.S_GRNs import *
from ..Serializer.S_Orders import *
from ..Serializer.S_Challan import *
from ..Serializer.S_Invoices import *
from ..Serializer.S_Bom import *
from ..Serializer.S_StockEntry import *
from ..Serializer.S_PartyItems import *
from ..models import *
from django.db.models import *


class StockEntryPageView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                StockEntrydata = JSONParser().parse(request)
                Party = StockEntrydata['PartyID']
                CreatedBy = StockEntrydata['CreatedBy']
                StockDate = StockEntrydata['Date']
              
                O_BatchWiseLiveStockList=list()
                O_LiveBatchesList=list()
                T_StockEntryList = list()
                for a in StockEntrydata['StockItems']:
                  
                    query2=MC_ItemShelfLife.objects.filter(Item_id=a['Item'],IsDeleted=0).values('Days')
                    BatchCode = SystemBatchCodeGeneration.GetGrnBatchCode(a['Item'], Party,0)
                    UnitwiseQuantityConversionobject=UnitwiseQuantityConversion(a['Item'],a['Quantity'],a['Unit'],0,0,0,0)
                    BaseUnitQuantity=UnitwiseQuantityConversionobject.GetBaseUnitQuantity()
                    
                    a['SystemBatchCode'] = BatchCode
                    a['SystemBatchDate'] = date.today()
                    a['BaseUnitQuantity'] = round(BaseUnitQuantity,3)
                    
                    O_BatchWiseLiveStockList.append({
                    "Item": a['Item'],
                    "Quantity": a['Quantity'],
                    "Unit": a['Unit'],
                    "BaseUnitQuantity": round(BaseUnitQuantity,3),
                    "OriginalBaseUnitQuantity": round(BaseUnitQuantity,3),
                    "Party": Party,
                    "CreatedBy":CreatedBy,
                    
                    })
                    
                    T_StockEntryList.append({
                    "StockDate":StockDate,    
                    "Item": a['Item'],
                    "Quantity": a['Quantity'],
                    "Unit": a['Unit'],
                    "BaseUnitQuantity": round(BaseUnitQuantity,3),
                    "MRPValue" :a["MRPValue"],
                    "MRP": a['MRP'],
                    "Party": Party,
                    "CreatedBy":CreatedBy,
                    })
                    
                    O_LiveBatchesList.append({
                    
                    "ItemExpiryDate":date.today()+ datetime.timedelta(days = query2[0]['Days']),
                    "MRP": a['MRP'],
                    "GST": a['GST'],
                    "MRPValue" :a["MRPValue"],
                    "GSTPercentage" : a['GSTPercentage'],
                    "SystemBatchDate": a['SystemBatchDate'],
                    "SystemBatchCode": a['SystemBatchCode'],
                    "BatchDate": a['BatchDate'],
                    "BatchCode": a['BatchCode'],
                    "OriginalBatchBaseUnitQuantity" : round(BaseUnitQuantity,3),
                    "O_BatchWiseLiveStockList" :O_BatchWiseLiveStockList, 
                    "T_StockEntryList" :T_StockEntryList                   
                    
                    })
                    
                    O_BatchWiseLiveStockList=list()
                    T_StockEntryList=list()
                
                StockEntrydata.update({"O_LiveBatchesList":O_LiveBatchesList})
                
                for aa in StockEntrydata['O_LiveBatchesList']:
                
                    StockEntry_OLiveBatchesSerializer = PartyStockEntryOLiveBatchesSerializer(data=aa)
                    if StockEntry_OLiveBatchesSerializer.is_valid():
                        StockEntry_OLiveBatchesSerializer.save()
                    else:
                        transaction.set_rollback(True)
                        return JsonResponse({'StatusCode': 406, 'Status': True,  'Message': StockEntry_OLiveBatchesSerializer.errors, 'Data': []})
                return JsonResponse({'StatusCode': 200, 'Status': True,  'Message': 'Party Stock Entry Save Successfully', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})
        
        
        
class ShowOBatchWiseLiveStockView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                StockReportdata = JSONParser().parse(request)
                FromDate = StockReportdata['FromDate']
                ToDate = StockReportdata['ToDate']
                Party = StockReportdata['PartyID']
                Unit = StockReportdata['Unit']
                
                Itemquery= MC_PartyItems.objects.raw('''SELECT M_Items.id,M_Items.Name,ifnull(MC_PartyItems.Party_id,0) Party_id,ifnull(M_Parties.Name,'') PartyName,ifnull(M_GroupType.Name,'') GroupTypeName,ifnull(M_Group.Name,'') GroupName,ifnull(MC_SubGroup.Name,'') SubGroupName from M_Items JOIN MC_PartyItems ON MC_PartyItems.item_id=M_Items.id left JOIN M_Parties ON M_Parties.id=MC_PartyItems.Party_id left JOIN MC_ItemGroupDetails ON MC_ItemGroupDetails.Item_id = M_Items.id left JOIN M_GroupType ON M_GroupType.id = MC_ItemGroupDetails.GroupType_id left JOIN M_Group ON M_Group.id  = MC_ItemGroupDetails.Group_id left JOIN MC_SubGroup ON MC_SubGroup.id  = MC_ItemGroupDetails.SubGroup_id where MC_PartyItems.Party_id=%s  order by M_Group.id, MC_SubGroup.id''',([Party]))
                # print(str(Itemquery.query))
                if not Itemquery:
                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':  'Items Not available', 'Data': []})
                else:
                    Items_Serializer = MC_PartyItemSerializerSingleGet(
                        Itemquery, many=True).data
                    ItemList = list()
                    for a in Items_Serializer:
                        ActualQty='00.00'
                        stockquery = O_BatchWiseLiveStock.objects.filter(Item=a['id'], Party=Party).aggregate(Qty=Sum('BaseUnitQuantity'))
                   
                        if stockquery['Qty'] is None:
                            Stock = 0.0
                        else:
                            Stock = stockquery['Qty']
                        
                        if int(Unit) == 1:
                            ActualQty=UnitwiseQuantityConversion(a['id'],Stock,0,0,0,1,0).ConvertintoSelectedUnit()
                            StockUnit = 'No'
                        if int(Unit) == 2:
                            ActualQty=UnitwiseQuantityConversion(a['id'],Stock,0,0,0,2,0).ConvertintoSelectedUnit()
                            StockUnit = 'Kg'
                           
                        if int(Unit) == 4:
                            ActualQty=UnitwiseQuantityConversion(a['id'],Stock,0,0,0,4,0).ConvertintoSelectedUnit()
                            StockUnit = 'Box'
                           
                            
                        ItemList.append({
                            "Item": a['id'],
                            "ItemName": a['Name'],
                            "GroupTypeName": a['GroupTypeName'],
                            "GroupName": a['GroupName'], 
                            "SubGroupName": a['SubGroupName'],
                            "ActualQty":round(ActualQty,3),
                            "Unit":StockUnit 
                        })
                    return JsonResponse({'StatusCode': 200, 'Status': True,  'Message':'', 'Data': ItemList})     
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})      



