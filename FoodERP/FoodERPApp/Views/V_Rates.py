from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
# from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, transaction
from rest_framework.parsers import JSONParser

from ..Serializer.S_Rates import *
from ..Serializer.S_Mrps import *
from ..Serializer.S_Items import *
from ..Serializer.S_Parties import *
from .V_CommFunction import *
from ..models import *
from datetime import datetime


class M_RatesView(CreateAPIView):
        
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication
    
    @transaction.atomic()
    def get(self, request):
        try:
            with transaction.atomic():
                Ratedata = M_RateMaster.objects.raw('''SELECT M_RateMaster.id,M_RateMaster.EffectiveDate,M_Parties.Name PartyName,
                M_PriceList.Name PriceListName,GROUP_CONCAT(CONCAT(M_Items.Name, ' ','=', M_RateMaster.Rate)) AS RateItemList,M_RateMaster.Company_id,
                M_RateMaster.CreatedBy,M_RateMaster.CreatedOn,M_RateMaster.CommonID,C_Companies.Name CompanyName
                FROM M_RateMaster 
                JOIN M_Items ON M_Items.Id=M_RateMaster.Item_Id
                left join C_Companies on C_Companies.id = M_RateMaster.Company_id
                left JOIN M_Parties ON M_Parties.id=M_RateMaster.Party_id
                left JOIN M_PriceList ON M_PriceList.id=M_RateMaster.PriceList_id
                where M_RateMaster.CommonID >0 AND M_RateMaster.IsDeleted=0   group by EffectiveDate,CommonID 
                Order BY EffectiveDate Desc''')
                
                if not Ratedata:
                    log_entry = create_transaction_logNew(request, 0, 0, "Rate Not available",371,0)
                    return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'Rate Not available', 'Data': []})
                else:
                    Ratedata_Serializer = M_RatesSerializerSecond(Ratedata, many=True).data
                    log_entry = create_transaction_logNew(request, Ratedata_Serializer, 0,'',371,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': Ratedata_Serializer})
        except Exception as e:
            log_entry = create_transaction_logNew(request,0, 0,'SingleGET Rate:'+str(Exception(e)),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})
    
    @transaction.atomic()
    def post(self, request):
        try:
            
            with transaction.atomic():
                M_Ratesdata = JSONParser().parse(request)
                
                # MCUnitID = M_Ratesdata[0]['UnitID']                
                # query = MC_ItemUnits.objects.filter(id=MCUnitID).values('UnitID')                              
                # UnitID=query[0]['UnitID']
                # M_Ratesdata[0]['UnitID']=UnitID                
                a=MaxValueMaster(M_RateMaster,'CommonID')
                jsondata=a.GetMaxValue() 
                # CustomPrint(jsondata)
                additionaldata= list()                
                for b in M_Ratesdata:                    
                    
                    b.update({'CommonID': jsondata})                   
                    additionaldata.append(b) 
                    # CustomPrint(b)
                    ItemId=b['Item']
                    EffectiveDate=b['EffectiveDate']
                    PriceListID = b['PriceList']
                    PartyID = b['Party']                   
                    # CustomPrint(ItemId)
                    Ratedata = M_RateMaster.objects.filter(Item_id=ItemId,EffectiveDate=EffectiveDate,PriceList_id=PriceListID,Party_id=PartyID).update(IsDeleted=1)    
                     
                M_Rates_Serializer = M_RatesSerializer(data=additionaldata,many=True)
                if M_Rates_Serializer.is_valid():
                    Rate = M_Rates_Serializer.save()
                    LastInsertID = Rate[0].id
                    
                    log_entry = create_transaction_logNew(request, M_Ratesdata,0,'TransactionID:'+str(LastInsertID),370,LastInsertID)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Rate Save Successfully', 'TransactionID':LastInsertID,'ItemID':M_Ratesdata[0]['Item'],'Data' :[]})
                else:
                    log_entry = create_transaction_logNew(request, M_Ratesdata, 0,'MRPSave:'+str(M_Rates_Serializer.errors),34,0)
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': M_Rates_Serializer.errors,'Data' :[]})
        except Exception as e:
            log_entry = create_transaction_logNew(request, 0, 0,'MRPSave:'+str(Exception(e)),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})

  
           
class GETRateDetails(CreateAPIView): 
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication
    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                EffectiveDate = request.data['EffectiveDate'] 
                PriceListID = request.data['PriceList']
                PartyID = request.data['Party']
                CompanyID = request.data['CompanyID']            
                
                MRates=M_RateMaster.objects.raw(f'''SELECT 1 id ,
			M_Items.id AS ItemID,
            GetTodaysDateRate(M_Items.id, '{EffectiveDate}','{PartyID}','{PriceListID}',1) AS Rateid,
			GetTodaysDateRate(M_Items.id, '{EffectiveDate}','{PartyID}','{PriceListID}',2) AS MRates,
            GetTodaysDateRate(M_Items.id, '{EffectiveDate}','{PartyID}','{PriceListID}',3) AS EffectiveDate,
            GetTodaysDateRate(M_Items.id, '{EffectiveDate}','{PartyID}','{PriceListID}',4) AS Unit,            
			M_Items.Name ItemName ,M_Units.Name UnitName,BaseUnitID_id,MC_ItemUnits.id UnitID
            FROM M_Items 
            JOIN M_Units ON M_Units.id=M_Items.BaseUnitID_id
            JOIN MC_ItemUnits on MC_ItemUnits.Item_id =M_Items.id
            where M_Items.Company_id={CompanyID} and isActive=1 and IsBase=1 ''')  
                           
                if not MRates:
                    
                    log_entry = create_transaction_logNew(request, EffectiveDate, 0, "Items Not available",367,0)
                    return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'Items Not available', 'Data': []})
                else:
                    
                    current_date = datetime.now().date()                      
                    ItemList = []  
                              
                    if MRates: 
                        
                        for a in MRates:
                            ItemList.append({
                            "id":a.Rateid,
                            "ItemID":a.ItemID,
                            "ItemName": a.ItemName,
                            "CurrentRate":a.MRates,
                            "EffectiveDate":a.EffectiveDate,                            
                            "UnitName" : a.UnitName,
                            "BaseUnitID" : a.BaseUnitID_id,
                            "Rate": "",
                            "UnitID":a.UnitID
                           
                        })
                            
                       
                    log_entry = create_transaction_logNew(request,ItemList, 0,'',367,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data':ItemList })
        except Exception as e:
            log_entry = create_transaction_logNew(request,ItemList, 0,'GetRatemethod:'+str(Exception(e)),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})

''' Rate Master List Delete Api Depend on ID '''
class M_RatesViewSecond(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                
                Ratedata = M_RateMaster.objects.filter(id=id).update(IsDeleted=1)
                
                # MRPdata.delete()
                log_entry = create_transaction_logNew(request, {'RateID':id}, 0, 'RateID:'+str(id),368,0)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Rate Deleted Successfully','DeleteID':id,'Data':[]})
        except M_RateMaster.DoesNotExist:
            log_entry = create_transaction_logNew(request,0, 0, "Rate Not available",368,0)
            transaction.set_rollback(True)
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Rate Not available', 'Data': []})
        except IntegrityError:
            log_entry = create_transaction_logNew(request,0, 0, "Rate used in another table",8,0)
            transaction.set_rollback(True)   
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Rate used in another table', 'Data': []}) 


''' Rate Master List Delete Api Depend on CommonID '''
class M_RatesViewThird(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def delete(self, request, id=0):
        Query = M_RateMaster.objects.filter(CommonID=id)
        # return JsonResponse({'StatusCode': 200, 'Status': True,'Data':str(Query.query)})
        Rate_Serializer = M_RatesSerializer(Query, many=True).data
        # return JsonResponse({'StatusCode': 200, 'Status': True,'Data':MRP_Serializer})
        for a in Rate_Serializer:
            deletedID = a['id'] 
            # CustomPrint(deletedID)
            try:
                with transaction.atomic():
                    Ratedata = M_RateMaster.objects.filter(id=deletedID).update(IsDeleted=1)
            except M_RateMaster.DoesNotExist:
                log_entry = create_transaction_logNew(request, 0, 0, "Rate Not available",369,0)
                transaction.set_rollback(True)
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Rate Not available', 'Data': []})    
            except IntegrityError:
                log_entry = create_transaction_logNew(request, 0, 0, "Rate used in another table",8,0)
                transaction.set_rollback(True)   
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Rate used in another table', 'Data': []}) 
        log_entry = create_transaction_logNew(request, {'RateID':id}, 0,'RateID:'+str(id),369,0)
        return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Rate Deleted Successfully','DeleteID':id,'Data':[]})
        
class BatchDetailsAdjustmentView(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    @transaction.atomic()
    def post(self, request):
        AdjustmentData = JSONParser().parse(request)
        updated_items = []

        try:
            with transaction.atomic():
                Party = AdjustmentData['PartyID']
                TypeID = AdjustmentData.get('TypeID')

                if not TypeID:
                    return JsonResponse({'StatusCode': 400, 'Status': False, 'Message': 'TypeID is required.', 'Data': []})

                Type = M_GeneralMaster.objects.filter(id=TypeID, IsActive=1).first()

                if not Type:
                    return JsonResponse({'StatusCode': 400, 'Status': False, 'Message': f'Invalid TypeID: {TypeID}', 'Data': []})

                for item in AdjustmentData['StockItems']:
                    BatchCode = item['BatchCode']
                    Rate = item.get('Rate')
                    GST = item.get('GST')
                    MRPValue = item.get('MRPValue')   

                    BatchDetails = O_LiveBatches.objects.filter(BatchCode=BatchCode).first()

                    if BatchDetails:
                        updated = False

                        if Type.Name == 'Rate':
                            if Rate is not None:
                                BatchDetails.Rate = Rate
                                updated = True
                            else:
                                return JsonResponse({'StatusCode': 400, 'Status': False, 'Message': f'Missing Rate for BatchCode: {BatchCode}', 'Data': []})

                        elif Type.Name == 'GST':
                            GSTInstance = M_GSTHSNCode.objects.filter(id=GST, IsDeleted=0).first()
                            if GSTInstance:
                                BatchDetails.GST_id = GSTInstance
                                updated = True
                            else:
                                return JsonResponse({'StatusCode': 400, 'Status': False, 'Message': f'Invalid GST ID: {GST} for BatchCode: {BatchCode}', 'Data': []})
                            
                        elif Type.Name == 'MRP':
                            if MRPValue is not None:
                                BatchDetails.MRPValue = MRPValue
                                updated = True
                            else:
                                return JsonResponse({'StatusCode': 400, 'Status': False, 'Message': f'Missing MRP for BatchCode: {BatchCode}', 'Data': []})

                        if updated:
                            BatchDetails.save()
                            updated_items.append(BatchCode)

                if updated_items:
                    log_entry = create_transaction_logNew(request, AdjustmentData, Party, 'Data Updated Successfully', 455, 0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Data Updated Successfully', 'Data': updated_items})
                else:
                    log_entry = create_transaction_logNew(request, 0, 0, "No records updated", 455, 0)
                    return JsonResponse({'StatusCode': 400, 'Status': False, 'Message': 'No records updated', 'Data': []})

        except Exception as e:
            log_entry = create_transaction_logNew(request, AdjustmentData, 0, 'DataAdjustment: ' + str(e), 33, 0)
            return JsonResponse({'StatusCode': 400, 'Status': False, 'Message': str(e), 'Data': []})


