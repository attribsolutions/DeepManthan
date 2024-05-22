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
from SweetPOS.Serializer.S_SPOSstock import SPOSstockSerializer
from django.db.models import *
from FoodERPApp.Views.V_TransactionNumberfun import SystemBatchCodeGeneration
from datetime import date

class FranchiseStockView(CreateAPIView):
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
                  
                    log_entry = create_transaction_logNew(request, FranchiseStockdata, FranchiseStockdata['PartyID'],'',381,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Stock Save Successfully', 'Data': []})
                else:
                    log_entry = create_transaction_logNew(request, FranchiseStockdata, 0,'FranchiseStockEntrySave:'+str(Stock_serializer.errors),34,0)
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': Stock_serializer.errors, 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, FranchiseStockdata, 0,'FranchiseStockEntrySave:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':Exception(e), 'Data': []})
