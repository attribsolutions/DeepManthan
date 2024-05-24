from datetime import timedelta
from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
# from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import transaction
from rest_framework.parsers import JSONParser
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
                    # CustomPrint(a)
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
                    
                    # CustomPrint(query3)
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
                    
                    "ItemExpiryDate":date.today()+ timedelta(days = query2[0]['Days']),
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
                # CustomPrint(StockEntrydata['O_LiveBatchesList'])
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
                Employee = StockReportdata['Employee']
                Cluster = StockReportdata['Cluster']
                SubCluster = StockReportdata['SubCluster']
                Group = StockReportdata['Group']
                SubGroup = StockReportdata['SubGroup']
                IsRateWise=StockReportdata['IsRateWise']
                today = date.today()                 
                if Party == "":
                    
                    PartyID=0;
                    if Employee > 0:
                        EmpPartys=MC_EmployeeParties.objects.raw('''select EmployeeParties(%s) id''',[Employee])
                        for row in EmpPartys:
                            p=row.id
                        PartyIDs = p.split(",")
                    where_clause = ""
                    p1 = (today,PartyIDs)
                    if Cluster:
                        where_clause += " AND M_Cluster.id = %s"
                        p1 += (Cluster,)
                      
                    if SubCluster:
                        where_clause += " AND M_SubCluster.id = %s "
                        p1 += (SubCluster,)
            
                    if Group:
                        where_clause += " AND M_Group.id = %s"
                        p1 += (Group,)
                        
                    if SubGroup:
                        where_clause += " AND MC_SubGroup.id = %s "
                        p1 += (SubGroup,)
                        
                    
                    Stockquery=(f'''SELECT A.id DistributorID,A.name DistributorName,ifnull(M_GroupType.Name,'') GroupTypeName,
ifnull(M_Group.Name,'') GroupName,ifnull(MC_SubGroup.Name,'') SubGroupName, M_Items.id,M_Items.Name,O_BatchWiseLiveStock.Party_id,
sum(O_BatchWiseLiveStock.BaseUnitQuantity)Qty ,
ifnull(sum(case when IsDamagePieces=0 then O_BatchWiseLiveStock.BaseUnitQuantity end),0)SaleableStock,
ifnull(sum(case when IsDamagePieces=1 then O_BatchWiseLiveStock.BaseUnitQuantity end),0)UnSaleableStock,
O_LiveBatches.MRPValue ,
0 BatchCode,0 SystemBatchCode,round(GSTHsnCodeMaster(M_Items.id,%s,2),2)GSTPercentage,0 Rate, M_Cluster.Name AS Cluster, M_SubCluster.Name AS SubCluster
                
                FROM M_Items 
join MC_PartyItems on M_Items.id=MC_PartyItems.Item_id and MC_PartyItems.Party_id in %s
left JOIN MC_ItemGroupDetails ON MC_ItemGroupDetails.Item_id = M_Items.id 
left JOIN M_GroupType ON M_GroupType.id = MC_ItemGroupDetails.GroupType_id
left JOIN M_Group ON M_Group.id  = MC_ItemGroupDetails.Group_id 
left JOIN MC_SubGroup ON MC_SubGroup.id  = MC_ItemGroupDetails.SubGroup_id
join O_BatchWiseLiveStock on M_Items.id=O_BatchWiseLiveStock.Item_id and O_BatchWiseLiveStock.Party_id= MC_PartyItems.Party_id
JOIN O_LiveBatches ON O_LiveBatches.id=O_BatchWiseLiveStock.LiveBatche_id
join M_Parties A on A.id =MC_PartyItems.Party_id
LEFT JOIN M_PartyDetails on  A.id=M_PartyDetails.Party_id AND M_PartyDetails.Group_id is null
LEFT JOIN M_Cluster On M_PartyDetails.Cluster_id=M_Cluster.id 
LEFT JOIN M_SubCluster on M_PartyDetails.SubCluster_id=M_SubCluster.Id
WHERE O_BatchWiseLiveStock.BaseUnitQuantity >0 {where_clause}
group by A.id, M_GroupType.id,
M_Group.id,MC_SubGroup.id, M_Items.id , GSTPercentage,MRPValue
order by A.id ,M_Group.id, MC_SubGroup.id ,M_Items.id''')
                    
                    Itemquery = MC_PartyItems.objects.raw(Stockquery, p1)
                    
                else : 
                    PartyID=Party;
                    PartyIDs= Party  

                    where_clause = ""
                    Condition=""
                    # p2 = (today, Unit, [PartyIDs]) 
                    if IsRateWise:
                        Condition += "ifnull(Round(GetTodaysDateRate(M_Items.id, curdate(),MC_PartyItems.Party_id,0,2),2),0)Rate"
                        p2 = (today, [PartyIDs])                         
                        
                    else:     
                        Condition += "RateCalculationFunction1(0, M_Items.id, MC_PartyItems.Party_id, %s, 0, 0, O_LiveBatches.MRPValue, 0)Rate"                  
                        p2 = (today, Unit, [PartyIDs]) 
                        
                    if Cluster:
                        where_clause += " AND M_Cluster.id = %s "
                        p2 += (Cluster,)
                    
                    if SubCluster:
                        where_clause += " AND M_SubCluster.id = %s "
                        p2 += (SubCluster,)
                    
                    if Group:
                        where_clause += " AND M_Group.id = %s"
                        p2 += (Group,)
                    
                    if SubGroup:
                        where_clause += " AND MC_SubGroup.id = %s "
                        p2 += (SubGroup,)
                    
                    Stockquery=(f'''SELECT A.id DistributorID,A.name DistributorName,ifnull(M_GroupType.Name,'') GroupTypeName,
    ifnull(M_Group.Name,'') GroupName,ifnull(MC_SubGroup.Name,'') SubGroupName, M_Items.id,M_Items.Name,O_BatchWiseLiveStock.Party_id,
    O_BatchWiseLiveStock.BaseUnitQuantity Qty ,M_Items.BaseUnitID_id,
    ifnull((case when IsDamagePieces=0 then O_BatchWiseLiveStock.BaseUnitQuantity end),0)SaleableStock,
    ifnull((case when IsDamagePieces=1 then O_BatchWiseLiveStock.BaseUnitQuantity end),0)UnSaleableStock,
    O_LiveBatches.MRPValue ,
    O_LiveBatches.BatchCode,O_LiveBatches.SystemBatchCode,round(GSTHsnCodeMaster(M_Items.id,%s,2),2)GSTPercentage,
    {Condition},  M_Cluster.Name AS Cluster, M_SubCluster.Name AS SubCluster
    FROM M_Items 
    join MC_PartyItems on M_Items.id=MC_PartyItems.Item_id and MC_PartyItems.Party_id in %s
    left JOIN MC_ItemGroupDetails ON MC_ItemGroupDetails.Item_id = M_Items.id 
    left JOIN M_GroupType ON M_GroupType.id = MC_ItemGroupDetails.GroupType_id
    left JOIN M_Group ON M_Group.id  = MC_ItemGroupDetails.Group_id 
    left JOIN MC_SubGroup ON MC_SubGroup.id  = MC_ItemGroupDetails.SubGroup_id
    join O_BatchWiseLiveStock on M_Items.id=O_BatchWiseLiveStock.Item_id and O_BatchWiseLiveStock.Party_id= MC_PartyItems.Party_id
    JOIN O_LiveBatches ON O_LiveBatches.id=O_BatchWiseLiveStock.LiveBatche_id
    join M_Parties A on A.id =MC_PartyItems.Party_id
    LEFT JOIN M_PartyDetails on  A.id=M_PartyDetails.Party_id AND M_PartyDetails.Group_id is null
    LEFT JOIN M_Cluster On M_PartyDetails.Cluster_id=M_Cluster.id 
    LEFT JOIN M_SubCluster on M_PartyDetails.SubCluster_id=M_SubCluster.Id
    WHERE O_BatchWiseLiveStock.BaseUnitQuantity >0 {where_clause}
    order by M_Group.id, MC_SubGroup.id ,M_Items.id,A.id''')
                       
                    Itemquery = MC_PartyItems.objects.raw(Stockquery, p2)
                    CustomPrint(Itemquery)
                if not Itemquery:
                    log_entry = create_transaction_logNew(request, StockReportdata, Party, "BatchWiseLiveStock Not available",88,0) 
                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':  'Items Not available', 'Data': []})
                else:
                    ItemList = list()
                    for row in Itemquery:
                        if int(Unit)==0:
                            Unit=row.BaseUnitID_id   
                        if int(Unit) == 1:
                            SaleableStockActualQty=UnitwiseQuantityConversion(row.id,row.SaleableStock,0,0,0,1,0).ConvertintoSelectedUnit()
                            UnSaleableStockActualQty=UnitwiseQuantityConversion(row.id,row.UnSaleableStock,0,0,0,1,0).ConvertintoSelectedUnit()
                            StockUnit = 'No'
                        if int(Unit) == 2:
                            SaleableStockActualQty=UnitwiseQuantityConversion(row.id,row.SaleableStock,0,0,0,2,0).ConvertintoSelectedUnit()
                            UnSaleableStockActualQty=UnitwiseQuantityConversion(row.id,row.UnSaleableStock,0,0,0,2,0).ConvertintoSelectedUnit()
                            StockUnit = 'Kg'
                        
                        if int(Unit) == 4:
                            SaleableStockActualQty=UnitwiseQuantityConversion(row.id,row.SaleableStock,0,0,0,4,0).ConvertintoSelectedUnit()
                            UnSaleableStockActualQty=UnitwiseQuantityConversion(row.id,row.UnSaleableStock,0,0,0,4,0).ConvertintoSelectedUnit()
                            StockUnit = 'Box'
                        
                       
                        SaleableStockValue = round((float(SaleableStockActualQty) * float(row.Rate)),2)
                        SaleableStockTaxValue =round((float(SaleableStockValue)*(float(row.GSTPercentage)/100)),2)
                        UnSaleableStockValue = round((float(UnSaleableStockActualQty) * float(row.Rate)),2)
                        UnSaleableStockTaxValue =round((float(UnSaleableStockValue)*(float(row.GSTPercentage)/100)),2)
                        
                        ItemList.append({
                            "DistributorCode" : row.DistributorID,
                            "DistributorName" : row.DistributorName,
                            "GroupTypeName": row.GroupTypeName,
                            "GroupName": row.GroupName, 
                            "SubGroupName": row.SubGroupName,
                            "Item": row.id,
                            "ItemName": row.Name,
                            "BatchCode" : row.BatchCode ,
                            "SystemBatchCode" : row.SystemBatchCode ,
                            "MRP":row.MRPValue,
                            "Rate":row.Rate,
                            "PurchaseRate" : round(row.Rate,2),
                            "SaleableStock":round(SaleableStockActualQty,3),
                            "UnSaleableStock":round(UnSaleableStockActualQty,3),
                            "SaleableStockValue" : SaleableStockValue,
                            "SaleableStockTaxValue" :SaleableStockTaxValue,
                            "UnSaleableStockValue" : UnSaleableStockValue,
                            "UnSaleableStockTaxValue" : UnSaleableStockTaxValue,
                            "TotalStockValue" : SaleableStockValue+UnSaleableStockValue,
                            "TaxValue" : SaleableStockTaxValue+UnSaleableStockTaxValue,
                            "Stockvaluewithtax" : SaleableStockValue+SaleableStockTaxValue+UnSaleableStockValue+UnSaleableStockTaxValue,
                            "Unit":StockUnit,
                            "GST" : row.GSTPercentage,
                            "Cluster" : row.Cluster,
                            "SubCluster": row.SubCluster
                        })
                        
                    
                    log_entry = create_transaction_logNew(request, StockReportdata, PartyID , 'From:'+FromDate+','+'To:'+ToDate,88,0,FromDate,ToDate,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True,  'Message':'', 'Data': ItemList})     
        except Exception as e:
            log_entry = create_transaction_logNew(request, 0, 0,'PartyLiveStock:'+str(Exception(e)),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})      



class DeleteDuplicateStockEntryPageView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request):
        try:
            with transaction.atomic():
                
                query=T_Stock.objects.raw('''select 1 as id, StockDate,Item_id,Party_id,max(id) maxid, count(*) cnt from T_Stock where StockDate>='20240331' and IsStockAdjustment=0  
group by StockDate,Item_id,Party_id having count(*) > 1
order by StockDate,Party_id,Item_id ''')
                
                for a in query:
                    CustomPrint(a.Party_id,)
                    CustomPrint(a.Item_id)
                    CustomPrint(a.maxid)
                    query2=T_Stock.objects.filter(StockDate='2024-03-31',  Item_id=a.Item_id,Party_id=a.Party_id,
).exclude(id=a.maxid).update(IsDeleted=1)
                   
            return JsonResponse({'StatusCode': 200, 'Status': True,  'Message': 'Delete Duplicate Stock Entry Successfully', 'Data': []})
        except Exception as e:
            
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})
        

# class FranchiseItemView(CreateAPIView):
#     permission_classes = (IsAuthenticated,)
    
#     @transaction.atomic()
#     def post(self, request):
#         Logindata = JSONParser().parse(request)
#         try:
#             with transaction.atomic():
#                 UserID = Logindata['UserID']
#                 RoleID = Logindata['RoleID']
#                 CompanyID = Logindata['CompanyID']
#                 PartyID = Logindata['PartyID']
#                 CompanyGroupID = Logindata['CompanyGroup']
#                 IsSCMCompany = Logindata['IsSCMCompany']

#                 FranchiseItemsList = []
                
#                 if IsSCMCompany == 1:
#                     Itemquery = MC_PartyItems.objects.raw('''SELECT distinct M_Items.id,M_Items.Name,ifnull(MC_PartyItems.Party_id,0) Party_id,ifnull(M_Parties.Name,'') PartyName,ifnull(M_GroupType.Name,'') GroupTypeName,ifnull(M_Group.Name,'') GroupName,ifnull(MC_SubGroup.Name,'') SubGroupName,M_ItemMappingMaster.MapItem FROM M_Items JOIN M_ChannelWiseItems ON M_ChannelWiseItems.Item_id=M_Items.id  LEFT JOIN MC_PartyItems ON MC_PartyItems.Item_id=M_ChannelWiseItems.Item_id AND MC_PartyItems.Party_id=%s LEFT JOIN M_Parties ON M_Parties.id=MC_PartyItems.Party_id LEFT JOIN MC_ItemGroupDetails ON MC_ItemGroupDetails.Item_id = M_Items.id LEFT JOIN M_GroupType ON M_GroupType.id = MC_ItemGroupDetails.GroupType_id LEFT JOIN M_Group ON M_Group.id  = MC_ItemGroupDetails.Group_id LEFT JOIN MC_SubGroup ON MC_SubGroup.id  = MC_ItemGroupDetails.SubGroup_id left join M_ItemMappingMaster on M_Items.id=M_ItemMappingMaster.Item_id and M_ItemMappingMaster.Party_id=%s WHERE IsSCM=1 AND M_Items.Company_id IN (select id from C_Companies where CompanyGroup_id=%s) AND M_ChannelWiseItems.PartyType_id IN (SELECT distinct M_Parties.PartyType_id FROM MC_PartySubParty WHERE (MC_PartySubParty.Party_id=%s))  order by M_Group.id, MC_SubGroup.id ''', ([PartyID], [PartyID], [CompanyGroupID], [PartyID]))
#                     print(Itemquery.query)
#                 else:
#                     Itemquery = MC_PartyItems.objects.raw('''SELECT distinct M_Items.id,M_Items.Name,ifnull(MC_PartyItems.Party_id,0) Party_id,ifnull(M_Parties.Name,'') PartyName,ifnull(M_GroupType.Name,'') GroupTypeName,ifnull(M_Group.Name,'') GroupName,ifnull(MC_SubGroup.Name,'') SubGroupName,M_ItemMappingMaster.MapItem FROM M_Items JOIN M_ChannelWiseItems ON M_ChannelWiseItems.Item_id=M_Items.id  LEFT JOIN MC_PartyItems ON MC_PartyItems.Item_id=M_ChannelWiseItems.Item_id AND MC_PartyItems.Party_id=%s LEFT JOIN M_Parties ON M_Parties.id=MC_PartyItems.Party_id LEFT JOIN MC_ItemGroupDetails ON MC_ItemGroupDetails.Item_id = M_Items.id LEFT JOIN M_GroupType ON M_GroupType.id = MC_ItemGroupDetails.GroupType_id LEFT JOIN M_Group ON M_Group.id  = MC_ItemGroupDetails.Group_id LEFT JOIN MC_SubGroup ON MC_SubGroup.id  = MC_ItemGroupDetails.SubGroup_id left join M_ItemMappingMaster on M_Items.id=M_ItemMappingMaster.Item_id and M_ItemMappingMaster.Party_id=%s WHERE  M_Items.Company_id IN (select id from C_Companies where CompanyGroup_id=%s) AND M_ChannelWiseItems.PartyType_id IN (SELECT distinct M_Parties.PartyType_id FROM MC_PartySubParty WHERE (MC_PartySubParty.Party_id=%s )) AND MC_PartyItems.Party_id IS NOT NULL order by M_Group.id, MC_SubGroup.id ''', ([PartyID], [PartyID], [CompanyGroupID], [PartyID]))
#                     print("ppppp")
#                     print(Itemquery)
#                 if not Itemquery:
#                     log_entry = create_transaction_logNew(request, Logindata, 0, 'Items Not available', 181, 0)
#                     return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Items Not available', 'Data': []})
#                 else:
#                     Items_Serializer = MC_PartyItemSerializerSingleGet(Itemquery, many=True).data
#                     for a in Items_Serializer:
                        # query1 = M_Items.objects.raw('''select id ,name ,
                        #                         round(GetTodaysDateMRP(%s,curdate(),2,0,0),2)MRPValue,                                                
                        #                         round(GetTodaysDateRate(%s,curdate(),0,0,2),2)RateValue,
                        #                         round(GSTHsnCodeMaster(%s,curdate(),2),2)GSTPercentage,
                        #                         GetTodaysDateMRP(%s,curdate(),1,0,0)MRPID,
                        #                         GSTHsnCodeMaster(%s,curdate(),1)GSTID,
                        #                         GetTodaysDateRate(%s,curdate(),0,0,1)RateID
                        #                         from M_Items where id =%s''', [a['id'], a['id'], a['id'], a['id'], a['id'], a['id'], a['id']])
#                         for b in query1:
#                             ItemMRPDetails = [{
#                                 "MRP": b.MRPID,
#                                 "MRPValue": b.MRPValue,
#                             }]
#                             ItemRateDetails = [{
#                                 "Rate": b.RateID,
#                                 "RateValue": b.RateValue,
#                             }]
#                             ItemGSTDetails = [{
#                                 "GST": b.GSTID,
#                                 "GSTPercentage": b.GSTPercentage,
#                             }]
#                             Unitquery = MC_ItemUnits.objects.filter(Item_id=b.id, IsDeleted=0)
#                             if Unitquery.exists():
#                                 Unitdata = Mc_ItemUnitSerializerThird(Unitquery, many=True).data
#                                 ItemUnitDetails = []
#                                 for c in Unitdata:
#                                     ItemUnitDetails.append({
#                                         "Unit": c['id'],
#                                         "BaseUnitQuantity": c['BaseUnitQuantity'],
#                                         "IsBase": c['IsBase'],
#                                         "UnitName": c['BaseUnitConversion'],
#                                     })
#                             else:
#                                 ItemUnitDetails = []

#                             FranchiseItemsList.append({
#                                 "Item": a['id'],
#                                 "ItemName": a['Name'],
#                                 "ItemUnitDetails": ItemUnitDetails,
#                                 "ItemMRPDetails": ItemMRPDetails,
#                                 "ItemGSTDetails": ItemGSTDetails,
#                                 "ItemRateDetails": ItemRateDetails
#                             })

#                 log_entry = create_transaction_logNew(request, Logindata, PartyID, '', 382, 0)
#                 return JsonResponse({'StatusCode': 200,'Status': True,'Message': '','Data':FranchiseItemsList})
#         except Exception as e:
#             log_entry = create_transaction_logNew(request, Logindata, 0, 'FetchSingleGETItem:' + str(e), 33, 0)
#             return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': str(e), 'Data': []})



class StockEntryItemsView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    
    @transaction.atomic()
    def post(self, request):
        Logindata = JSONParser().parse(request)
        try:
            with transaction.atomic():
                UserID = Logindata['UserID']
                RoleID = Logindata['RoleID']
                CompanyID = Logindata['CompanyID']
                PartyID = Logindata['PartyID']
                CompanyGroupID = Logindata['CompanyGroup']
                IsSCMCompany = Logindata['IsSCMCompany']
                
                Itemquery = MC_PartyItems.objects.raw('''SELECT M_Items.id, M_Items.Name AS ItemName,
                                                            ROUND(GetTodaysDateMRP(M_Items.id, CURDATE(), 2, 0, 0), 2) AS MRPValue,
                                                            ROUND(GetTodaysDateRate(M_Items.id, CURDATE(), 0, 0, 2), 2) AS RateValue,
                                                            ROUND(GSTHsnCodeMaster(M_Items.id, CURDATE(), 2), 2) AS GSTPercentage,
                                                            GetTodaysDateMRP(M_Items.id, CURDATE(), 1, 0, 0) AS MRPID,
                                                            GSTHsnCodeMaster(M_Items.id, CURDATE(), 1) AS GSTID,
                                                            GetTodaysDateRate(M_Items.id, CURDATE(), 0, 0, 1) AS RateID
                                                            FROM M_Items 
                                                            JOIN MC_PartyItems  ON MC_PartyItems.Item_id = M_Items.id
                                                            WHERE MC_PartyItems.Party_id = %s''', ([PartyID]))
                print(Itemquery)
                if not Itemquery:
                    log_entry = create_transaction_logNew(request, Logindata, 0, 'Items Not available', 181, 0)
                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Items Not available', 'Data': []})
                
                FranchiseItemsList = [{
                    "Item": item.id,
                    "ItemName": item.ItemName,
                    "ItemUnitDetails": [{
                        "Unit": unit.id,
                        "BaseUnitQuantity": unit.BaseUnitQuantity,
                        "IsBase": unit.IsBase,
                        "UnitName": unit.BaseUnitConversion,
                    } for unit in MC_ItemUnits.objects.filter(Item_id=item.id, IsDeleted=0)],
                    "ItemMRPDetails": [{
                        "MRP": item.MRPID,
                        "MRPValue": item.MRPValue,
                    }],
                    "ItemGSTDetails": [{
                        "GST": item.GSTID,
                        "GSTPercentage": item.GSTPercentage,
                    }],
                    "ItemRateDetails": [{
                        "Rate": item.RateID,
                        "RateValue": item.RateValue,
                    }]
                } for item in Itemquery]
                
                log_entry = create_transaction_logNew(request, Logindata, PartyID, '', 382, 0)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': FranchiseItemsList})

        except Exception as e:
            log_entry = create_transaction_logNew(request, Logindata, 0, 'FetchSingleGETItem:' + str(e), 33, 0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': str(e), 'Data': []})
