from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from rest_framework.parsers import JSONParser
from rest_framework.authentication import BasicAuthentication
from django.contrib.auth import authenticate
from FoodERPApp.models import *
from ..models import *
from SweetPOS.Serializer.S_POSRate import *
from FoodERPApp.Views.V_CommFunction import *

class RateListView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self,request):
        Rate_Data = JSONParser().parse(request)
        try:
            with transaction.atomic():
                EffectiveFrom = Rate_Data['EffectiveFrom']
                POSRateType = Rate_Data['POSRateType'] 
                
                today = date.today()

                ItemsGroupJoinsandOrderby = Get_Items_ByGroupandPartytype(0,5).split('!')   
                
                q0 =  M_ChannelWiseItems.objects.raw(f'''SELECT A.id, A.Item_id ItemID,  M_Items.Name ItemName, C.Rate, C.IsChangeRateToDefault,Round(GetTodaysDateMRP(M_Items.id,%s,2,0,0,0),2)PrimaryRate,Groupss.Name as GroupName,subgroup.Name as SubGroupName
                                                    FROM FoodERP.M_ChannelWiseItems A 
                                                    join FoodERP.M_Items  on A.Item_id = M_Items.id
                                                    {ItemsGroupJoinsandOrderby[1]}
                                                    left join SweetPOS.M_SPOSRateMaster C on C.ItemID = M_Items.id and C.IsDeleted=0 and C.EffectiveFrom <= %s and C.POSRateType = %s 
                                                    where A.PartyType_id in (select id from M_PartyType where IsFranchises=1)
                                                    {ItemsGroupJoinsandOrderby[2]}
                                                    ''', [today, EffectiveFrom, POSRateType])
               
                RateList = list()
                for a in q0:
                    RateList.append({
                        "ItemID": a.ItemID,
                        "ItemName":a.ItemName,
                        "Rate": a.Rate,
                        "IsChangeRateToDefault": a.IsChangeRateToDefault,
                        "PrimaryRate": a.PrimaryRate,
                        "GroupName":a.GroupName,
                        "SubGroupName":a.SubGroupName
                    })
                log_entry = create_transaction_logNew(request, Rate_Data, 0, 'RateDetails', 420, 0)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data' :RateList})
            log_entry = create_transaction_logNew(request, 0, 0, 'Rate not available', 420, 0)
            return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': 'Rate not available', 'Data' : []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, 0, 0, 'RateData:' + str(e), 33, 0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':str(e), 'Data':[]})
        
class RateSaveView(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    @transaction.atomic()
    def post(self, request):
        Rate_data = JSONParser().parse(request)
        try:
            with transaction.atomic():

                item_ids = [item['ItemID'] for item in Rate_data]

                M_SPOSRateMaster.objects.filter(ItemID__in=item_ids, POSRateType=Rate_data[0]['POSRateType']).update(IsDeleted=1)

                Rate_serializer = RateSerializer(data=Rate_data, many=True)
                if Rate_serializer.is_valid():
                    Rate_serializer.save()
                    log_entry = create_transaction_logNew(request, Rate_data, 0, 'SaveRate', 421, 0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Rate Save Successfully', 'Data': []})
                log_entry = create_transaction_logNew(request, 0, 0, 'Data not available', 421, 0)
                return JsonResponse({'StatusCode': 406, 'Status': False, 'Message': 'Data not available', 'Data': Rate_serializer.errors})
        except Exception as e:
            log_entry = create_transaction_logNew(request, 0, 0, 'RateData:' + str(e), 33, 0)
            return JsonResponse({'StatusCode': 400, 'Status': False, 'Message': str(e), 'Data': []})