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

class RateListView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self,request):
        try:
            with transaction.atomic():

                query = M_SPOSRateMaster.objects.raw('''SELECT A.id, A.Item_id ItemID,  B.Name ItemName, C.Rate
                                                    FROM FoodERP.M_ChannelWiseItems A 
                                                    join FoodERP.M_Items B on A.Item_id = B.id
                                                    left join SweetPOS.M_SPOSRateMaster C on C.ItemID = B.id and C.IsDeleted=0
                                                    where PartyType_id=19 ''')
                RateList = list()
                for a in query:
                    RateList.append({
                        "ItemID": a.ItemID,
                        "ItemName":a.ItemName,
                        "Rate": a.Rate,
                    })
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data' :RateList})
            return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': 'Rate not available', 'Data' : []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':Exception(e), 'Data':[]})
        
