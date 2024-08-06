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
                query = M_SPOSRateMaster.objects.all()
                if query:
                    Rate_serializer = RateSerializer(query, many=True).data
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data' :Rate_serializer})
                return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': 'Rate not available', 'Data' : []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':Exception(e), 'Data':[]})
        
class RateSaveView(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    @transaction.atomic()
    def post(self,request):
        try:
            with transaction.atomic():
                Rate_data = JSONParser().parse(request)
                M_SPOSRateMaster.objects.filter(ItemID=Rate_data['ItemID']).delete()
                Rate_serializer = RateSerializer(data=Rate_data)
                if Rate_serializer.is_valid():
                    Rate_serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Rate Save Successfully', 'Data':[]})
                return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': 'Rate not available', 'Data' : []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':Exception(e), 'Data':[]})    



