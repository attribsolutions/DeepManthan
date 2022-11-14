from django.http import JsonResponse
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, connection, transaction
from rest_framework.parsers import JSONParser

from ..Serializer.S_DeliveryChallans import *

from ..models import  *


class T_DeliveryChallanView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request,id=0):
        try:
            with transaction.atomic():
                query = T_DeliveryChallans.objects.all()
                if not query:
                    return JsonResponse({'StatusCode': 200, 'Status': True,'Message':  'Records Not available', 'Data': []})
                else:
                    DeliveryChallan_serializer = T_DeliveryChallanSerializer(query, many=True).data
                    return JsonResponse({'StatusCode': 200, 'Status': 'true', 'Data': DeliveryChallan_serializer})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})

    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                DeliveryChallandata = JSONParser().parse(request)
                DeliveryChallandata_serializer = T_DeliveryChallanSerializer(data=DeliveryChallandata)
                if DeliveryChallandata_serializer.is_valid():
                    DeliveryChallandata_serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': 'true',  'Message': 'Delivery Challan Save Successfully', 'Data':[]})
                return JsonResponse({'StatusCode': 200, 'Status': 'true',  'Message': DeliveryChallandata_serializer.errors, 'Data':[]})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})

class T_DeliveryChallanViewSecond(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request,id=0):
        try:
            with transaction.atomic():
                DeliveryChallandata = T_DeliveryChallans.objects.get(id=id)
                DeliveryChallan_serializer = T_DeliveryChallanSerializer(DeliveryChallandata)
                return JsonResponse({'StatusCode': 200, 'Status': 'true', 'Data': DeliveryChallan_serializer.data})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})
   

    @transaction.atomic()
    def put(self, request, id=0):
        try:
            with transaction.atomic():
                DeliveryChallandata = JSONParser().parse(request)
                DeliveryChallanByID = T_DeliveryChallans.objects.get(id=id)
                DeliveryChallan_Serializer = T_DeliveryChallanSerializer(DeliveryChallanByID, data=DeliveryChallandata)
                if DeliveryChallan_Serializer.is_valid():
                    DeliveryChallan_Serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Delivery Challan Updated Successfully','Data':{}})
                return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': DeliveryChallan_Serializer.errors ,'Data':[]})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})
   
    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                DeliveryChallan_Data = T_DeliveryChallans.objects.get(id=id)
                DeliveryChallan_Data.delete()
                return JsonResponse({'StatusCode': 200, 'Status': 'true', 'Message': 'Delivery Challan Deleted Successfully', 'Data':[]})
        except T_DeliveryChallans.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Record Not available', 'Data': []})
        except IntegrityError:   
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Delivery Challan used in another tbale', 'Data': []})    


