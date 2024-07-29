from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from rest_framework.parsers import JSONParser
from rest_framework.authentication import BasicAuthentication
from FoodERPApp.Views.V_CommFunction import UnitwiseQuantityConversion, create_transaction_logNew
from FoodERPApp.models import *
from FoodERPApp.Serializer.S_PartyItems import *
from FoodERPApp.Serializer.S_Orders import *
from ..models import  *
from SweetPOS.Serializer.S_SPOSstock import SPOSstockSerializer, SPOSStockReportSerializer
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

                T_StockEntryList = list()
                Stock_serializer = SPOSstockSerializer(data=FranchiseStockdata, many=True)

                for a in FranchiseStockdata['StockItems']:
                    BatchCode = SystemBatchCodeGeneration.GetGrnBatchCode(a['Item'], Party,0)
                    UnitwiseQuantityConversionobject=UnitwiseQuantityConversion(a['Item'],a['Quantity'],a['Unit'],0,0,0,0)
                    BaseUnitQuantity=UnitwiseQuantityConversionobject.GetBaseUnitQuantity()
                    Item=a['Item']
                    if Mode == 2:
                        query3 = T_SPOSStock.objects.filter(Party=Party).aggregate(total=Sum('BaseUnitQuantity'))
                    else:
                        query3 = T_SPOSStock.objects.filter(Party=Party,id=a['BatchCodeID']).aggregate(total=Sum('BaseUnitQuantity'))

                    if query3['total']:
                        totalstock=float(query3['total'])
                    else:
                        totalstock=0

                    a['BatchCode'] = BatchCode
                    a['StockDate'] = date.today()
                    a['BaseUnitQuantity'] = round(BaseUnitQuantity,3)

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
                Stock_serializer = SPOSstockSerializer(data=T_StockEntryList, many=True)
                
                if Stock_serializer.is_valid():
                    Stock_serializer.save()
                  
                    log_entry = create_transaction_logNew(request, FranchiseStockdata, FranchiseStockdata['PartyID'],'Franchise Items Save Successfully',87,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Stock Save Successfully', 'Data': []})
                else:
                    log_entry = create_transaction_logNew(request, FranchiseStockdata, 0,'FranchiseStockEntrySave:'+str(Stock_serializer.errors),34,0)
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': Stock_serializer.errors, 'Data': []})
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
                UnitName = M_Units.objects.filter(id=Unit).values("Name")
                unitname = UnitName[0]['Name']
                StockreportQuery = O_SPOSDateWiseLiveStock.objects.raw('''
                SELECT 1 as id,A.Item_id,A.Unit,
                FoodERP.UnitwiseQuantityConversion(A.Item_id,ifnull(OpeningBalance,0),0,A.Unit,0,%s,0)OpeningBalance,
                FoodERP.UnitwiseQuantityConversion(A.Item_id,GRNInward,0,A.Unit,0,%s,0)GRNInward,
                FoodERP.UnitwiseQuantityConversion(A.Item_id,Sale,0,A.Unit,0,%s,0)Sale,
                FoodERP.UnitwiseQuantityConversion(A.Item_id,ClosingBalance,0,A.Unit,0,%s,0)ClosingBalance,
                FoodERP.UnitwiseQuantityConversion(A.Item_id,ActualStock,0,A.Unit,0,%s,0)ActualStock,
                A.ItemName,
                D.QuantityInBaseUnit,
                FoodERP.UnitwiseQuantityConversion(A.Item_id,PurchaseReturn,0,A.Unit,0,%s,0)PurchaseReturn,
                FoodERP.UnitwiseQuantityConversion(A.Item_id,SalesReturn,0,A.Unit,0,%s,0)SalesReturn,
                FoodERP.UnitwiseQuantityConversion(A.Item_id,StockAdjustment,0,A.Unit,0,%s,0)StockAdjustment
                ,GroupTypeName,GroupName,SubGroupName,%s UnitName
                FROM

                        ( SELECT M_Items.id Item_id, M_Items.Name ItemName ,Unit,M_Units.Name UnitName ,SUM(GRN) GRNInward, SUM(Sale) Sale, SUM(PurchaseReturn)PurchaseReturn,SUM(SalesReturn)SalesReturn,SUM(StockAdjustment)StockAdjustment,
                    ifnull(M_GroupType.Name,'') GroupTypeName,ifnull(M_Group.Name,'') GroupName,ifnull(MC_SubGroup.Name,'') SubGroupName
                        FROM O_SPOSDateWiseLiveStock

                JOIN FoodERP.M_Items ON M_Items.id=O_SPOSDateWiseLiveStock.Item
                join FoodERP.M_Units on M_Units.id= O_SPOSDateWiseLiveStock.Unit
                left join FoodERP.MC_ItemGroupDetails on MC_ItemGroupDetails.Item_id=M_Items.id
                left JOIN FoodERP.M_GroupType ON M_GroupType.id = MC_ItemGroupDetails.GroupType_id
                left JOIN FoodERP.M_Group ON M_Group.id  = MC_ItemGroupDetails.Group_id
                left JOIN FoodERP.MC_SubGroup ON MC_SubGroup.id  = MC_ItemGroupDetails.SubGroup_id
                 WHERE M_GroupType.id = 5 AND StockDate BETWEEN %s AND %s AND Party=%s GROUP BY Item,M_GroupType.id,M_Group.id,MC_SubGroup.id) A

                left JOIN (SELECT O_SPOSDateWiseLiveStock.Item, OpeningBalance FROM O_SPOSDateWiseLiveStock WHERE O_SPOSDateWiseLiveStock.StockDate = %s AND O_SPOSDateWiseLiveStock.Party=%s) B
                ON A.Item_id = B.Item

                left JOIN (SELECT Item, ClosingBalance, ActualStock FROM O_SPOSDateWiseLiveStock WHERE StockDate = %s AND Party=%s) C 
                ON A.Item_id = C.Item

                LEFT JOIN (SELECT Item, SUM(BaseunitQuantity) QuantityInBaseUnit
                FROM T_SPOSStock
                WHERE Party =%s AND StockDate BETWEEN %s AND %s
                GROUP BY Item) D
                ON A.Item_id = D.Item ''', ([Unit], [Unit], [Unit], [Unit], [Unit], [Unit], [Unit], [Unit], [unitname], [FromDate], [ToDate], [Party], [FromDate], [Party], [ToDate], [Party], [Party], [FromDate], [ToDate]))
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
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': str(e), 'Data': []})
