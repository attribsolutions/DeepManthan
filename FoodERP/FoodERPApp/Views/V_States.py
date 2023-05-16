from django.http import JsonResponse
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
# from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import transaction
from ..Serializer.S_States import *
from ..models import *

class M_StateView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication


class M_StateView(RetrieveAPIView):

    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request,id=0):
        try:
            with transaction.atomic():
                State_data = M_States.objects.all()
                if State_data.exists():
                    State_serializer =  StateSerializer(State_data, many=True)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': State_serializer.data})
                return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'Records Not available', 'Data': []})    
        except Exception:
            raise JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  'Exception Found', 'Data': []})
        
class M_DistrictView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request,id=0):
        try:
            with transaction.atomic():
                Districts_data = M_Districts.objects.filter(State=id)
                if Districts_data.exists():
                    District_serializer =  DistrictsSerializer(Districts_data, many=True)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': District_serializer.data})
                return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'Districts Not available', 'Data': []})    
        except Exception:
            raise JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  'Exception Found', 'Data': []})
                          