from django.http import JsonResponse
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import connection, transaction
from rest_framework.parsers import JSONParser

from ..Serializer.S_States import *

from ..models import *

class S_StateView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request,id=0):
        try:
            with transaction.atomic():
                State_data = M_States.objects.all()
                if State_data.exists():
                    State_serializer =  StateSerializer(State_data, many=True)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': State_serializer.data})
                return JsonResponse({'StatusCode': 200, 'Status': True,'Message':  'Records Not available', 'Data': []})    
        except Exception as e:
            raise JsonResponse({'StatusCode': 200, 'Status': True, 'Message':  Exception(e), 'Data': []})
         

    @transaction.atomic()
    def post(self, request, id=0):
        try:
            with transaction.atomic():
                State_data = JSONParser().parse(request)
                State_serializer = StateSerializer(data=State_data)
                if State_serializer.is_valid():
                    State_serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'State Save Successfully', 'Data': []})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':  State_serializer.errors, 'Data': []})
        except Exception as e:
            raise JsonResponse({'StatusCode': 200, 'Status': True, 'Message':  Exception(e), 'Data': []})
            print(e)        

class S_StateViewSecond(RetrieveAPIView):

    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request, id=0):
        try:
            with transaction.atomic():
                State_data = M_States.objects.get(id=id)
                State_serializer = StateSerializer(State_data)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':'', 'Data': State_serializer.data})
        except M_States.DoesNotExist:
            return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':  'Record Not available', 'Data': []})
            

    @transaction.atomic()
    def put(self, request, id=0):
        try:
            with transaction.atomic():
                State_data = JSONParser().parse(request)
                StatedataByID = M_States.objects.get(id=id)
                State_serializer = StateSerializer(StatedataByID, data=State_data)
                if State_serializer.is_valid():
                    State_serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'State Updated Successfully', 'Data' : []})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': State_serializer.errors, 'Data' : []})
        except Exception as e:
            raise JsonResponse({'StatusCode': 200, 'Status': True, 'Message':  Exception(e), 'Data': []})

    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                State_data = M_States.objects.get(id=id)
                State_data.delete()
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'State Deleted Successfully','Data':[]})
        except Exception as e:
            raise JsonResponse({'StatusCode': 200, 'Status': True, 'Message':  Exception(e), 'Data': []})             