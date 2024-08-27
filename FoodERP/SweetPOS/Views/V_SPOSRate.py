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
                GroupTypeid = 5 
                
                # ---- Order By Sequence  
                joinsforgroupsubgroup = f'''
                    LEFT JOIN FoodERP.MC_ItemGroupDetails ON MC_ItemGroupDetails.Item_id = B.id AND MC_ItemGroupDetails.GroupType_id = {GroupTypeid}
                    LEFT JOIN FoodERP.M_Group ON M_Group.id = MC_ItemGroupDetails.Group_id 
                    LEFT JOIN FoodERP.MC_SubGroup ON MC_SubGroup.id = MC_ItemGroupDetails.SubGroup_id
                '''   
                orderby = f'''
                    ORDER BY M_Group.Sequence, MC_SubGroup.Sequence,MC_ItemGroupDetails.ItemSequence
                '''   
                
                q0 = f'''SELECT A.id, A.Item_id ItemID,  B.Name ItemName, C.Rate, C.IsChangeRateToDefault,round(FoodERP.GetTodaysDateMRP(B.id,%s,2,0,0),0) PrimaryRate,M_Group.Name as GroupName,MC_SubGroup.Name as SubGroupName
                                                    FROM FoodERP.M_ChannelWiseItems A 
                                                    join FoodERP.M_Items B on A.Item_id = B.id
                                                    {joinsforgroupsubgroup}
                                                    left join SweetPOS.M_SPOSRateMaster C on C.ItemID = B.id and C.IsDeleted=0 and C.EffectiveFrom <= %s and C.POSRateType = %s 
                                                    where A.PartyType_id=19 
                                                    {orderby}
                                                    '''
                                                                         
                params = [today, EffectiveFrom, POSRateType]
                
                q1 = M_SPOSRateMaster.objects.raw(q0,params)
                RateList = list()
                for a in q1:
                    RateList.append({
                        "ItemID": a.ItemID,
                        "ItemName":a.ItemName,
                        "Rate": a.Rate,
                        "IsChangeRateToDefault": a.IsChangeRateToDefault,
                        "PrimaryRate": a.PrimaryRate,
                        "GroupName":a.GroupName,
                        "SubGroupName":a.SubGroupName
                    })
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data' :RateList})
            return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': 'Rate not available', 'Data' : []})
        except Exception as e:
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
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Rate Save Successfully', 'Data': []})
                return JsonResponse({'StatusCode': 406, 'Status': False, 'Message': 'Data not available', 'Data': Rate_serializer.errors})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': False, 'Message': str(e), 'Data': []})