from django.http import JsonResponse
from datetime import timedelta
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from rest_framework.parsers import JSONParser
from rest_framework.authentication import BasicAuthentication
from FoodERPApp.Views.V_CommFunction import *
from FoodERPApp.models import *
from FoodERPApp.Serializer.S_PartyItems import *
from FoodERPApp.Serializer.S_Orders import *
from ..models import  *
from SweetPOS.Serializer.S_SPOSstock import *
from django.db.models import *
from FoodERPApp.Views.V_TransactionNumberfun import SystemBatchCodeGeneration
from datetime import date
from FoodERPApp.models import * 

class StockView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    
    @transaction.atomic()
    def post(self, request):
        FranchiseStockdata = JSONParser().parse(request)
        try:
            with transaction.atomic():
                Party = FranchiseStockdata['PartyID']
                CreatedBy = FranchiseStockdata['CreatedBy']
                StockDate = FranchiseStockdata['Date']
                Mode =  FranchiseStockdata['Mode']
                IsStockAdjustment=FranchiseStockdata['IsStockAdjustment']
                IsAllStockZero = FranchiseStockdata['IsAllStockZero']

                T_SPOS_StockEntryList = list()
              
                for a in FranchiseStockdata['StockItems']:
                    BatchCode = SystemBatchCodeGeneration.GetGrnBatchCode(a['Item'], Party,0)
                    
                    query3 = None
                    query4 = None
                    
                    if Mode == 2: #Mode 2 is for stock adjustment
                        UnitwiseQuantityConversionobject = UnitwiseQuantityConversion( a['Item'], a['Quantity'], a['Unit'], 0, 0, 0, 0 )
                    else:
                        UnitwiseQuantityConversionobject = UnitwiseQuantityConversion( a['Item'], a['Quantity'], 0, a['Unit'], 0, 0, 0)

                    BaseUnitQuantity=UnitwiseQuantityConversionobject.GetBaseUnitQuantity()
                 
                    Item=a['Item']
                    if Mode == 2:
                        query3 = O_SPOSDateWiseLiveStock.objects.filter(Party=Party,Item=Item,StockDate=date.today()).values('ClosingBalance')
                    else:
                        query4 = T_SPOSStock.objects.filter(Party=Party,id=a['BatchCodeID'],).aggregate(total=Sum('BaseUnitQuantity'))
                        
                    if query3 and query3.exists():
                        totalstock = float(query3[0]['ClosingBalance'])
                    elif query4 and query4['total']:
                        totalstock = float(query4['total'])
                    else:
                        totalstock = 0

                    a['BatchCode'] = BatchCode
                    a['StockDate'] = date.today()
                    a['BaseUnitQuantity'] = round(BaseUnitQuantity,3)

                    T_SPOS_StockEntryList.append({
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
                    
                StockEntrySerializer = SPOSstockSerializer(data=T_SPOS_StockEntryList, many=True)
               
                       
                if StockEntrySerializer.is_valid():
                    StockEntrySerializer.save()
                    
                    if Mode == 2:
                        log_entry = create_transaction_logNew(request, FranchiseStockdata, Party, 'FranchiseStock Adjustment Save Successfully', 87, 0)
                        return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'FranchiseStock Adjustment Save Successfully', 'Data': []})
                    else:
                        log_entry = create_transaction_logNew(request, FranchiseStockdata, Party, 'FranchiseItems Stock Save Successfully', 87, 0)
                        return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'FranchiseItems Stock Save Successfully', 'Data': []})
                else:
                    log_entry = create_transaction_logNew(request, FranchiseStockdata, 0,'FranchiseStockEntrySave:'+str(StockEntrySerializer.errors),34,0)
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': StockEntrySerializer.errors, 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, FranchiseStockdata, 0,'FranchiseStockEntrySave:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':str(e), 'Data': []})



class SPOSStockReportView(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, id=0):
        Orderdata = JSONParser().parse(request)
        try:
            with transaction.atomic():
                FromDate = Orderdata['FromDate']
                ToDate = Orderdata['ToDate']
                Unit = Orderdata['Unit']
                Party = Orderdata['Party']
                PartyNameQ = M_Parties.objects.filter(id=Party).values("Name")
                CustomPrint(PartyNameQ)
                if(Unit!=0):
                    UnitName = M_Units.objects.filter(id=Unit).values("Name")
                    unitname = UnitName[0]['Name']                    
                else:
                    unitname='UnitName'      
                # print('aaaaa')
                if(Unit==0):
                    unitcondi='A.Unit'
                else:
                    unitcondi=Unit  
                CustomPrint(Unit)  
                StockreportQuery = O_SPOSDateWiseLiveStock.objects.raw(f'''
                SELECT 1 as id,A.Item_id,A.Unit,
                FoodERP.UnitwiseQuantityConversion(A.Item_id,ifnull(OpeningBalance,0),0,A.Unit,0,{unitcondi},0)OpeningBalance,
                FoodERP.UnitwiseQuantityConversion(A.Item_id,GRNInward,0,A.Unit,0,{unitcondi},0)GRNInward,
                FoodERP.UnitwiseQuantityConversion(A.Item_id,Sale,0,A.Unit,0,{unitcondi},0)Sale,
                FoodERP.UnitwiseQuantityConversion(A.Item_id,ClosingBalance,0,A.Unit,0,{unitcondi},0)ClosingBalance,
                FoodERP.UnitwiseQuantityConversion(A.Item_id,ActualStock,0,A.Unit,0,{unitcondi},0)ActualStock,
                A.ItemName,
                D.QuantityInBaseUnit,
                FoodERP.UnitwiseQuantityConversion(A.Item_id,PurchaseReturn,0,A.Unit,0,{unitcondi},0)PurchaseReturn,
                FoodERP.UnitwiseQuantityConversion(A.Item_id,SalesReturn,0,A.Unit,0,{unitcondi},0)SalesReturn,
                FoodERP.UnitwiseQuantityConversion(A.Item_id,StockAdjustment,0,A.Unit,0,{unitcondi},0)StockAdjustment
                ,GroupTypeName,GroupName,SubGroupName,'{unitname}' UnitName
                FROM

                        ( SELECT M_Items.id Item_id, M_Items.Name ItemName ,Unit,M_Units.Name UnitName ,SUM(GRN) GRNInward, SUM(Sale) Sale, SUM(PurchaseReturn)PurchaseReturn,SUM(SalesReturn)SalesReturn,SUM(StockAdjustment)StockAdjustment,
                    ifnull(M_GroupType.Name,'') GroupTypeName,ifnull(M_Group.Name,'') GroupName,ifnull(MC_SubGroup.Name,'') SubGroupName
                        FROM O_SPOSDateWiseLiveStock

                JOIN FoodERP.M_Items ON M_Items.id=O_SPOSDateWiseLiveStock.Item
                join FoodERP.M_Units on M_Units.id= O_SPOSDateWiseLiveStock.Unit
                left join FoodERP.MC_ItemGroupDetails on MC_ItemGroupDetails.Item_id=M_Items.id and MC_ItemGroupDetails.GroupType_id = 5
                left JOIN FoodERP.M_GroupType ON M_GroupType.id = MC_ItemGroupDetails.GroupType_id 
                left JOIN FoodERP.M_Group ON M_Group.id  = MC_ItemGroupDetails.Group_id
                left JOIN FoodERP.MC_SubGroup ON MC_SubGroup.id  = MC_ItemGroupDetails.SubGroup_id
                 WHERE StockDate BETWEEN %s AND %s AND Party=%s GROUP BY Item,Unit,M_GroupType.id,M_Group.id,MC_SubGroup.id) A

                left JOIN (SELECT O_SPOSDateWiseLiveStock.Item, OpeningBalance FROM O_SPOSDateWiseLiveStock WHERE O_SPOSDateWiseLiveStock.StockDate = %s AND O_SPOSDateWiseLiveStock.Party=%s) B
                ON A.Item_id = B.Item

                left JOIN (SELECT Item, ClosingBalance, ActualStock FROM O_SPOSDateWiseLiveStock WHERE StockDate = %s AND Party=%s) C 
                ON A.Item_id = C.Item

                LEFT JOIN (SELECT Item, SUM(BaseunitQuantity) QuantityInBaseUnit
                FROM T_SPOSStock
                WHERE Party =%s AND StockDate BETWEEN %s AND %s
                GROUP BY Item) D
                ON A.Item_id = D.Item ''', ( [FromDate], [ToDate], [Party], [FromDate], [Party], [ToDate], [Party], [Party], [FromDate], [ToDate]))
                CustomPrint(StockreportQuery)
                serializer = SPOSStockReportSerializer(StockreportQuery, many=True).data                
                StockData = list()
                StockData.append({
                    "FromDate": FromDate,
                    "ToDate": ToDate,
                    "PartyName": PartyNameQ[0]["Name"],
                    "StockDetails": serializer})

                if StockreportQuery:
                    log_entry = create_transaction_logNew(request, Orderdata, Party, 'From:'+str(FromDate)+','+'To:'+str(ToDate), 210, 0, FromDate, ToDate, 0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': StockData})
                else:
                    log_entry = create_transaction_logNew(request, Orderdata, Party, 'Recort Not Found', 210, 0)
                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Record Not Found', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request,Orderdata, 0, 'StockReport:'+str(e), 33, 0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': Exception(e), 'Data': []})
        
        
        
        
 
class SPOSStockAdjustmentView(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    @transaction.atomic()
    def get(self, request, id=0,Party=0):
        try:
            with transaction.atomic():
                query=O_SPOSDateWiseLiveStock.objects.raw(''' SELECT 1 as id, M_Items.id Item, M_Items.Name AS ItemName, D.StockDate,
                                                            FORMAT(IFNULL(D.ClosingBalance, 0), 15) AS Quantity,
                                                            M_Units.id AS UnitID, M_Units.Name AS UnitName,M_Group.Name AS GroupName,MC_SubGroup.Name AS SubGroupName,
                                                            (SELECT MRP FROM SweetPOS.T_SPOSStock 
                                                                WHERE StockDate = (SELECT MAX(StockDate) FROM SweetPOS.T_SPOSStock WHERE Item = %s AND Party = %s)
                                                                AND Item = %s AND Party = %s ORDER BY id DESC LIMIT 1) AS MRP,
                                                            (SELECT BatchCode FROM SweetPOS.T_SPOSStock 
                                                                WHERE StockDate = (SELECT MAX(StockDate) FROM SweetPOS.T_SPOSStock WHERE Item = %s AND Party = %s)
                                                                AND Item = %s AND Party = %s ORDER BY id DESC LIMIT 1) AS BatchCode,
                                                            (SELECT MRPValue FROM SweetPOS.T_SPOSStock 
                                                                WHERE StockDate = (SELECT MAX(StockDate) FROM SweetPOS.T_SPOSStock WHERE Item = %s AND Party = %s)
                                                                AND Item = %s AND Party = %s ORDER BY id DESC LIMIT 1) AS MRPValue
                                                            FROM  FoodERP.M_Items
                                                            left JOIN SweetPOS.O_SPOSDateWiseLiveStock D ON M_Items.id = D.Item and D.Party = %s and D.StockDate = CURRENT_DATE
                                                            left JOIN FoodERP.M_Units ON M_Units.id = M_Items.BaseUnitID_id
                                                            LEFT JOIN FoodERP.MC_ItemGroupDetails ON MC_ItemGroupDetails.Item_id = M_Items.id AND MC_ItemGroupDetails.GroupType_id = 5
                                                            LEFT JOIN FoodERP.M_GroupType ON M_GroupType.id = MC_ItemGroupDetails.GroupType_id
                                                            LEFT JOIN FoodERP.M_Group ON M_Group.id = MC_ItemGroupDetails.Group_id
                                                            LEFT JOIN FoodERP.MC_SubGroup ON MC_SubGroup.id = MC_ItemGroupDetails.SubGroup_id
                                                            WHERE  M_Items.id = %s
                                                            ORDER BY FoodERP.M_Group.Sequence, FoodERP.MC_SubGroup.Sequence, FoodERP.MC_ItemGroupDetails.ItemSequence''',([id],[Party],[id],[Party],[id],[Party],[id],[Party],[id],[Party],[id],[Party],[Party],[id]))                                   
                if query:
                    BatchCodelist = list()
                    for a in query:
                        Unitquery = MC_ItemUnits.objects.raw('''SELECT MC_ItemUnits.id, M_Units.Name AS UnitName, MC_ItemUnits.BaseUnitQuantity, MC_ItemUnits.IsBase
                                                            FROM MC_ItemUnits 
                                                            JOIN M_Units ON MC_ItemUnits.UnitID_id = M_Units.id
                                                            WHERE MC_ItemUnits.Item_id = %s AND MC_ItemUnits.IsDeleted = 0''',([id]))
                        if Unitquery:
                            ItemUnitDetails = list()
                            for c in Unitquery:
                                ItemUnitDetails.append({
                                "Unit": c.id,
                                "BaseUnitQuantity": c.BaseUnitQuantity,
                                "IsBase": c.IsBase,
                                "UnitName": c.BaseUnitConversion,    
                            })
                        BatchCodelist.append({
                            'id':  a.id,
                            'Item':  a.Item,
                            'ItemName':  a.ItemName,
                            'GroupName': a.GroupName,
                            'SubGroupName' : a.SubGroupName,
                            'OriginalBaseUnitQuantity': a.Quantity,
                            'BaseUnitQuantity': a.Quantity,
                            'BatchDate': a.StockDate,
                            'BatchCode':  a.BatchCode,
                            'MRP':  a.MRPValue,
                            'SystemBatchDate':  a.StockDate,
                            'SystemBatchCode':  a.BatchCode,
                            'MRPValue': a.MRPValue,
                            'MRPID': a.MRP,
                            'GSTID':  "",
                            'GSTPercentage':  "",
                            'UnitID':  a.UnitID,
                            'UnitName':  a.UnitName,
                            'UnitOptions' : ItemUnitDetails
                        })
                    log_entry = create_transaction_logNew(request,0, Party,BatchCodelist,407,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': BatchCodelist})
                else:
                    log_entry = create_transaction_logNew(request, 0, Party, 'Item Not Available', 407, 0)
                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Item Not Available', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request,0, 0,'GETStockAdjustment:'+str(),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})


class StockOutReportView(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    @transaction.atomic()
    def post(self, request):
        StockData = JSONParser().parse(request)
        try:
            with transaction.atomic():
                FromDate = StockData['FromDate']
                ToDate = StockData['ToDate']
                Party = StockData['Party']

                StockOutReportQuery = T_SPOSStockOut.objects.raw('''SELECT A.id, A.StockDate , A.Item ItemID, B.Name, M_Group.Name "Group", MC_SubGroup.Name SubGroup, A.Party, M_Parties.Name PartyName, A.CreatedBy, A.CreatedOn StockoutTime
                            FROM SweetPOS.T_SPOSStockOut A 
                            JOIN FoodERP.M_Items B ON B.id = A.Item
                            JOIN FoodERP.M_Parties ON M_Parties.id = A.Party
                            LEFT JOIN FoodERP.MC_ItemGroupDetails ON MC_ItemGroupDetails.Item_id=B.id AND MC_ItemGroupDetails.GroupType_id = 5
                            LEFT JOIN FoodERP.M_Group ON M_Group.id  = MC_ItemGroupDetails.Group_id
                            LEFT JOIN FoodERP.MC_SubGroup ON MC_SubGroup.id  = MC_ItemGroupDetails.SubGroup_id
                            WHERE A.StockDate BETWEEN %s AND %s AND A.Party=%s''',[FromDate,ToDate,Party])
                
                StockOutDataList = list()

                for a in StockOutReportQuery:
                    StockOutDataList.append({
                        "id": a.id,
                        "ItemID": a.ItemID,
                        "ItemName": a.Name,
                        "Group": a.Group,
                        "SubGroup": a.SubGroup,
                        "Party": a.Party,
                        "PartyName": a.PartyName,
                        "CreatedBy": a.CreatedBy,
                        "StockoutTime": a.StockoutTime

                    })
                log_entry = create_transaction_logNew(request, StockData, StockData['Party'], '', 419, 0)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': StockOutDataList})
        except Exception as e:
            log_entry = create_transaction_logNew(request, StockData, 0, 'SPOS StockOut Report:'+str(e), 33, 0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})
               
