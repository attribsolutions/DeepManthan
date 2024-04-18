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
                Ratedata = M_RateMaster.objects.raw('''SELECT M_RateMaster.id,M_RateMaster.EffectiveDate,M_RateMaster.Company_id,
                M_RateMaster.CreatedBy,M_RateMaster.CreatedOn,M_RateMaster.CommonID,C_Companies.Name CompanyName
                FROM M_RateMaster 
                left join C_Companies on C_Companies.id = M_RateMaster.Company_id
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
                
                a=MaxValueMaster(M_RateMaster,'CommonID')
                jsondata=a.GetMaxValue() 
                additionaldata= list()                
                for b in M_Ratesdata:                    
                    b.update({'CommonID': jsondata})                   
                    additionaldata.append(b)                
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
                CompanyID = request.data['CompanyID']            
                MRates=M_RateMaster.objects.raw(f'''SELECT 1  id,ifnull(MAX(M_RateMaster.id),0) AS RateMasterID,
                                                    M_Items.id AS ItemID,
                                                    GetTodaysDateRate(M_Items.id, '{EffectiveDate}',2) AS MRates,
                                                    MAX(M_Items.Name) AS Name 
                                                    FROM M_Items LEFT JOIN  M_RateMaster ON M_RateMaster.Item_id = M_Items.id 
                                                    JOIN  MC_PartyItems ON MC_PartyItems.Item_id=M_Items.id   where M_Items.Company_id={CompanyID}                                                                                              
                                                    GROUP BY  M_Items.id''')  
                print(MRates.query)
                           
                if not MRates:
                    
                    log_entry = create_transaction_logNew(request, EffectiveDate, 0, "Items Not available",367,0)
                    return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'Items Not available', 'Data': []})
                else:
                    
                    current_date = datetime.now().date()                      
                    ItemList = []  
                              
                    if MRates: 
                        
                        for a in MRates:
                            ItemList.append({
                            "id":a.RateMasterID,
                            "Item":a.ItemID,
                            "Name": a.Name,
                            "CurrentRate":a.MRates,
                            "CurrentDate":current_date,
                            "Rate": ""
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
            # print(deletedID)
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
           
            
                
           