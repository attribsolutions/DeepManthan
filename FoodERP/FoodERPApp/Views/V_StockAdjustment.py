from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
# from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import transaction
from rest_framework.parsers import JSONParser
from django.db import connection

from ..Views.V_TransactionNumberfun import GetYear
from ..Serializer.S_Orders import Mc_ItemUnitSerializerThird
from ..Serializer.S_StockAdjustment import *
from ..Serializer.S_Parties import *
from ..Serializer.S_ItemSale import *
from ..models import *
from ..Views.V_CommFunction import *
from datetime import datetime


 
class ShowBatchesForItemView(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    @transaction.atomic()
    def get(self, request, id=0,Party=0):
        try:
            with transaction.atomic():
                query=O_BatchWiseLiveStock.objects.raw('''SELECT O_BatchWiseLiveStock.id,O_BatchWiseLiveStock.Item_id,M_Items.Name ItemName,
                                                       OriginalBaseUnitQuantity,BaseUnitQuantity,O_LiveBatches.BatchDate,O_LiveBatches.BatchCode,
                                                       O_LiveBatches.SystemBatchDate,O_LiveBatches.SystemBatchCode,O_LiveBatches.MRPValue,
                                                       O_LiveBatches.MRP_id MRPID,M_MRPMaster.MRP,O_LiveBatches.GST_id,
                                                       M_GSTHSNCode.GSTPercentage,M_Units.id UnitID,M_Units.Name UnitName,O_LiveBatches.Rate
                                                       FROM O_BatchWiseLiveStock
                                                       JOIN O_LiveBatches ON O_LiveBatches.id=O_BatchWiseLiveStock.LiveBatche_id
                                                       LEFT JOIN M_MRPMaster ON M_MRPMaster.id= O_LiveBatches.MRP_id 
                                                       JOIN M_GSTHSNCode ON M_GSTHSNCode.id=O_LiveBatches.GST_id  
                                                       JOIN M_Items ON M_Items.id =O_BatchWiseLiveStock.Item_id 
                                                       JOIN M_Units ON M_Units.id = M_Items.BaseUnitID_id
                                                       WHERE O_BatchWiseLiveStock.Item_id=%s AND O_BatchWiseLiveStock.Party_id=%s 
                                                       AND IsDamagePieces =0 order by id desc limit 50''',([id],[Party]))
               
                if query:
                    BatchCodelist = list()
                    Obatchwise_serializer = OBatchWiseLiveStockAdjustmentSerializer(query, many=True).data
                    for a in Obatchwise_serializer:
                        Unitquery = MC_ItemUnits.objects.filter(Item_id=a['Item_id'],IsDeleted=0)
                        if Unitquery.exists():
                            Unitdata = Mc_ItemUnitSerializerThird(Unitquery, many=True).data
                            ItemUnitDetails = list()
                            for c in Unitdata:
                                ItemUnitDetails.append({
                                "Unit": c['id'],
                                "BaseUnitQuantity": c['BaseUnitQuantity'],
                                "IsBase": c['IsBase'],
                                "UnitName": c['BaseUnitConversion'],
                            })
                        BatchCodelist.append({
                            'id':  a['id'],
                            'Item':  a['Item_id'],
                            'ItemName':  a['ItemName'],
                            'OriginalBaseUnitQuantity': a['OriginalBaseUnitQuantity'],
                            'BaseUnitQuantity':  a['BaseUnitQuantity'],
                            'BatchDate':  a['BatchDate'],
                            'BatchCode':  a['BatchCode'],
                            'SystemBatchDate':  a['SystemBatchDate'],
                            'SystemBatchCode':  a['SystemBatchCode'],
                            'MRPValue':  a['MRPValue'],
                            'MRPID':  a['MRPID'],
                            'MRP':  a['MRP'],
                            'GSTID':  a['GST_id'],
                            'GSTPercentage':  a['GSTPercentage'],
                            'UnitID':  a['UnitID'],
                            'UnitName':  a['UnitName'],
                            'Rate': a['Rate'],
                            'UnitOptions' : ItemUnitDetails
                        })
                    log_entry = create_transaction_logNew(request,0, 0,'',272,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': BatchCodelist})
                log_entry = create_transaction_logNew(request,0, 0,'Stock Not available',272,0)
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Stock Not available ', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request,0, 0,'GETBatchesForItemInStockAdjustment:'+str(Exception),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})


class GetStockCountForPartyView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    
    @transaction.atomic()
    def post(self, request, id=0):
        try:
            with transaction.atomic():
                StockData = JSONParser().parse(request)
                FromDate = StockData['FromDate']
                PartyID = StockData['PartyID']

                Stockquery=''' select GetStockEffectiveTransactionCountFromDateForPartyID(%s, %s)'''

                with connection.cursor() as cursor:
                    # Execute the raw query and fetch the results
                    cursor.execute(Stockquery, [FromDate, PartyID])
                    StockResult = cursor.fetchone()[0]
                log_entry = create_transaction_logNew(request,StockData, 0,'',358,0)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': StockResult})

        except Exception as e:
            log_entry = create_transaction_logNew(request,0, 0,'StockData:'+str((e)),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})
        
        
class CheckStockEntryForFYFirstTransactionView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
   
    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                StockData = JSONParser().parse(request)
                FromDate = StockData['FromDate']
                PartyID = StockData['PartyID']
                query= M_Settings.objects.filter(id=41).values('DefaultValue') 
                IsActive = query[0]['DefaultValue']                                    
                
                if(IsActive == '1'):
                    Return_year= GetYear(FromDate)  
                                         
                    fs,fe=Return_year 
                    year_fs = datetime.strptime(fs, '%Y-%m-%d').year
                    year_fe= datetime.strptime(fe, '%Y-%m-%d').year
                    
                    concatenated_year = str(year_fs) + '-' + str(year_fe)   
                                        
                    query1= M_FinancialYearFirstTransactionLog.objects.filter(Party=PartyID,FinancialYear=concatenated_year).count()                                                
                    
                    if (query1==0):
                        with connection.cursor() as cursor:
                            cursor.execute("SELECT CheckStockEntryForFinancialYearFirstTransaction(%s, %s, %s, %s)", [FromDate, PartyID,concatenated_year,year_fs])
                            result = cursor.fetchone()[0]
                                
                            if result == 1: 
                                Message = ""
                                Result = True
                                StatusCode = 200
                            else: 
                                Result = False 
                                Message = f"Please enter the stock for all products to enable transactions in the financial year {concatenated_year}."
                                StatusCode = 400
                            log_entry = create_transaction_logNew(request,StockData, PartyID,f'Date: {FromDate}',359,0)
                            return JsonResponse({'StatusCode': StatusCode, 'Status': True, 'Message': Message, 'Data': Result})
                    else: 
                        log_entry = create_transaction_logNew(request,StockData, PartyID, f'Date: {FromDate}',359,0)
                        return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': True})
                else:
                    log_entry = create_transaction_logNew(request,StockData, PartyID, f'Date: {FromDate}',359,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': True})  
        except Exception as e:
            log_entry = create_transaction_logNew(request,0, 0,'FinancialYearFirstTransaction:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': False})

 
class CheckStockEntryDateAndNotAllowedBackdatedTransactionView(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    @transaction.atomic()
    def post(self, request):
        TransactionData = JSONParser().parse(request)
        try:
            TransactionDate = TransactionData['TransactionDate']
            PartyID = TransactionData['PartyID']
            
            BackDateTransactionQuery='''SELECT CheckStockEntryDateAndNotAllowedBackdatedTransaction(%s, %s)'''
            
            with connection.cursor() as cursor:
                cursor.execute(BackDateTransactionQuery, [TransactionDate, PartyID])
                result = cursor.fetchone()[0]
                
            if result: 
                log_entry = create_transaction_logNew(request,TransactionData, PartyID,f'Transactions Allowed for Party: {PartyID} Date: {TransactionDate}',360,0)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Transactions Allowed', 'Data': bool(result)})
            else:  
                log_entry = create_transaction_logNew(request,TransactionData, PartyID,f'Backdated transactions not allowed for Party: {PartyID} Date: {TransactionDate}',360,0)
                return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': 'Backdated transactions not allowed', 'Data': bool(result)})
        except Exception as e:
            log_entry = create_transaction_logNew(request,0, 0,'TransactionData:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': str(e), 'Data': []})