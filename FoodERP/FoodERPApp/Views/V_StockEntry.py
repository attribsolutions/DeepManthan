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
                Mode =  StockEntrydata['Mode']
                IsStockAdjustment=StockEntrydata['IsStockAdjustment']
                IsAllStockZero = StockEntrydata['IsAllStockZero']
              
                O_BatchWiseLiveStockList=list()
                O_LiveBatchesList=list()
                T_StockEntryList = list()
                for a in StockEntrydata['StockItems']:
                    # print(a)
                    query2=MC_ItemShelfLife.objects.filter(Item_id=a['Item'],IsDeleted=0).values('Days')
                    BatchCode = SystemBatchCodeGeneration.GetGrnBatchCode(a['Item'], Party,0)
                    UnitwiseQuantityConversionobject=UnitwiseQuantityConversion(a['Item'],a['Quantity'],a['Unit'],0,0,0,0)
                    BaseUnitQuantity=UnitwiseQuantityConversionobject.GetBaseUnitQuantity()
                    Item=a['Item']
                    if Mode == 1:
                        query3 = O_BatchWiseLiveStock.objects.filter(Item_id=Item,Party_id=Party).aggregate(total=Sum('BaseUnitQuantity'))
                    else:
                        query3 = O_BatchWiseLiveStock.objects.filter(Item_id=Item,Party_id=Party,id=a['BatchCodeID']).aggregate(total=Sum('BaseUnitQuantity'))
                  
                    if query3['total']:
                        totalstock=float(query3['total'])
                    else:
                        totalstock=0    
                    
                    # print(query3)
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
                    "BatchCode" : a['BatchCode'],
                    "BatchCodeID" : a['BatchCodeID'],
                    "IsSaleable" : 1,
                    "Difference" : round(BaseUnitQuantity,3)-totalstock,
                    "IsStockAdjustment" : IsStockAdjustment
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
                    "Mode" :Mode,
                    "OriginalBatchBaseUnitQuantity" : round(BaseUnitQuantity,3),
                    "O_BatchWiseLiveStockList" :O_BatchWiseLiveStockList, 
                    "T_StockEntryList" :T_StockEntryList                   
                    
                    })
                    
                    O_BatchWiseLiveStockList=list()
                    T_StockEntryList=list()
                
                StockEntrydata.update({"O_LiveBatchesList":O_LiveBatchesList})
                
                if(Mode == 1):   # Stock Entry case update 0 to all stock for given party
                    if IsAllStockZero == True:
                        OBatchWiseLiveStock=O_BatchWiseLiveStock.objects.filter(Party=Party).update(BaseUnitQuantity=0)
                    else:
                        
                        for b in StockEntrydata['StockItems']:
                            OBatchWiseLiveStock=O_BatchWiseLiveStock.objects.filter(Party=Party,Item=b['Item']).update(BaseUnitQuantity=0)      
                # print(StockEntrydata['O_LiveBatchesList'])
                for aa in StockEntrydata['O_LiveBatchesList']:
               
                    if(Mode == 1):
                        StockEntry_OLiveBatchesSerializer = PartyStockEntryOLiveBatchesSerializer(data=aa)
                    else:
                        StockEntry_OLiveBatchesSerializer = PartyStockAdjustmentOLiveBatchesSerializer(data=aa)
                    
                    
                    if StockEntry_OLiveBatchesSerializer.is_valid():
                        StockEntry_OLiveBatchesSerializer.save()
                        
                        pass
                    else:
                        log_entry = create_transaction_logNew(request, StockEntrydata, 0,'PartyStockEntrySave:'+str(StockEntry_OLiveBatchesSerializer.errors),34,0)
                        transaction.set_rollback(True)
                        return JsonResponse({'StatusCode': 406, 'Status': True,  'Message': StockEntry_OLiveBatchesSerializer.errors, 'Data': []})
                log_entry = create_transaction_logNew(request, StockEntrydata, Party,'',87,0)
                return JsonResponse({'StatusCode': 200, 'Status': True,  'Message': 'Party Stock Entry Save Successfully', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, 0, 0,'PartyStockEntrySave:'+str(Exception(e)),33,0)
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
                IsDamagePieces=StockReportdata['IsDamagePieces']

                
                Itemquery= MC_PartyItems.objects.raw('''SELECT ifnull(M_GroupType.Name,'') GroupTypeName,
ifnull(M_Group.Name,'') GroupName,ifnull(MC_SubGroup.Name,'') SubGroupName, M_Items.id,M_Items.Name,O_BatchWiseLiveStock.Party_id,O_BatchWiseLiveStock.BaseUnitQuantity Qty ,O_LiveBatches.MRPValue ,
O_LiveBatches.BatchCode,O_LiveBatches.SystemBatchCode
FROM M_Items 
join MC_PartyItems on M_Items.id=MC_PartyItems.Item_id
left JOIN MC_ItemGroupDetails ON MC_ItemGroupDetails.Item_id = M_Items.id 
left JOIN M_GroupType ON M_GroupType.id = MC_ItemGroupDetails.GroupType_id
left JOIN M_Group ON M_Group.id  = MC_ItemGroupDetails.Group_id 
left JOIN MC_SubGroup ON MC_SubGroup.id  = MC_ItemGroupDetails.SubGroup_id
join O_BatchWiseLiveStock on M_Items.id=O_BatchWiseLiveStock.Item_id and O_BatchWiseLiveStock.Party_id=%s
JOIN O_LiveBatches ON O_LiveBatches.id=O_BatchWiseLiveStock.LiveBatche_id
where MC_PartyItems.Party_id=%s and O_BatchWiseLiveStock.BaseUnitQuantity >0 and O_BatchWiseLiveStock.IsDamagePieces=%s order by M_Group.id, MC_SubGroup.id ,M_Items.id ''',([Party],[Party],[IsDamagePieces]))
                # print(str(Itemquery.query))
                if not Itemquery:
                    log_entry = create_transaction_logNew(request, StockReportdata, Party, "BatchWiseLiveStock Not available",88,0)
                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':  'Items Not available', 'Data': []})
                else:
                    ItemList = list()
                    for row in Itemquery:
                        Stock = row.Qty
                        
                        if int(Unit) == 1:
                            ActualQty=UnitwiseQuantityConversion(row.id,Stock,0,0,0,1,0).ConvertintoSelectedUnit()
                            StockUnit = 'No'
                        if int(Unit) == 2:
                            ActualQty=UnitwiseQuantityConversion(row.id,Stock,0,0,0,2,0).ConvertintoSelectedUnit()
                            StockUnit = 'Kg'
                        
                        if int(Unit) == 4:
                            ActualQty=UnitwiseQuantityConversion(row.id,Stock,0,0,0,4,0).ConvertintoSelectedUnit()
                            StockUnit = 'Box'
                            
                        ItemList.append({
                            "Item": row.id,
                            "ItemName": row.Name,
                            "GroupTypeName": row.GroupTypeName,
                            "GroupName": row.GroupName, 
                            "SubGroupName": row.SubGroupName,
                            "ActualQty":round(ActualQty,3),
                            "BatchCode" : row.BatchCode ,
                            "SystemBatchCode" : row.SystemBatchCode ,
                            "Unit":StockUnit,
                            "MRP":row.MRPValue
                        })
                    
                    log_entry = create_transaction_logNew(request, StockReportdata, Party, 'From:'+FromDate+','+'To:'+ToDate,88,0,FromDate,ToDate,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True,  'Message':'', 'Data': ItemList})     
        except Exception as e:
            log_entry = create_transaction_logNew(request, 0, 0,'PartyLiveStock:'+str(Exception(e)),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})      



