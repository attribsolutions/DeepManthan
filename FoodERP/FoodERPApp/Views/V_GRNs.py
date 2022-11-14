from django.http import JsonResponse
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, connection, transaction
from rest_framework.parsers import JSONParser

from ..Serializer.S_GRNs import *

from ..models import  *


class T_GRNView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request,id=0):
        try:
            with transaction.atomic():
                query = T_GRNs.objects.all()
                if not query:
                    return JsonResponse({'StatusCode': 200, 'Status': True,'Message':  'Records Not available', 'Data': []})
                else:
                    GRN_serializer = T_GRNSerializer(query, many=True).data
                    return JsonResponse({'StatusCode': 200, 'Status': 'true', 'Data': GRN_serializer})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})

    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                GRNdata = JSONParser().parse(request)
                GRN_serializer = T_GRNSerializer(data=GRNdata)
                if GRN_serializer.is_valid():
                    GRN_serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': 'true',  'Message': 'GRN Save Successfully', 'Data':[]})
                return JsonResponse({'StatusCode': 200, 'Status': 'true',  'Message': GRN_serializer.errors, 'Data':[]})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})

class T_GRNViewSecond(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request,id=0):
        try:
            with transaction.atomic():
                GRNdata = T_GRNs.objects.get(id=id)
                GRN_serializer = T_GRNSerializer(GRNdata)
                return JsonResponse({'StatusCode': 200, 'Status': 'true', 'Data': GRN_serializer.data})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})
   

    @transaction.atomic()
    def put(self, request, id=0):
        try:
            with transaction.atomic():
                Invoiceupdatedata = JSONParser().parse(request)
                InvoiceupdateByID = T_GRNs.objects.get(id=id)
                Invoiceupdate_Serializer = T_GRNSerializer(InvoiceupdateByID, data=Invoiceupdatedata)
                if Invoiceupdate_Serializer.is_valid():
                    Invoiceupdate_Serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Invoice Updated Successfully','Data':{}})
                return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': Invoiceupdate_Serializer.errors ,'Data':[]})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})
   
    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                GRN_Data = T_GRNs.objects.get(id=id)
                GRN_Data.delete()
                return JsonResponse({'StatusCode': 200, 'Status': 'true', 'Message': 'GRN Deleted Successfully', 'Data':[]})
        except T_GRNs.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Record Not available', 'Data': []})
        except IntegrityError:   
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'T_GRN used in another tbale', 'Data': []})    


