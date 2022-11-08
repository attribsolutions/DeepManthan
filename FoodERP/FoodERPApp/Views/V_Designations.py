from django.http import JsonResponse
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, connection, transaction
from rest_framework.parsers import JSONParser

from ..Serializer.S_Designations import *

from ..models import *

class M_DesignationsView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request):
        try:
            with transaction.atomic():
                M_Designations_data = M_Designations.objects.all()
                if M_Designations_data.exists():
                    M_Designations_serializer = M_DesignationsSerializer(M_Designations_data, many=True)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': M_Designations_serializer.data})
                return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'Designation Not available', 'Data': []})    
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})   
            

    @transaction.atomic()
    def post(self, request, id=0):
        try:
            with transaction.atomic():
                Designationsdata = JSONParser().parse(request)
                Designationsdata_Serializer = M_DesignationsSerializer(data=Designationsdata)
                if Designationsdata_Serializer.is_valid():
                    Designationsdata_Serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Designation Save Successfully', 'Data':[]})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message':  Designationsdata_Serializer.errors, 'Data':[]})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})   
                    

class M_DesignationsViewSecond(RetrieveAPIView):
    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request, id=0):
        try:
            with transaction.atomic():
                Designations_data = M_Designations.objects.get(id=id)
                Designations_Serializer = M_DesignationsSerializer(Designations_data)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':'', 'Data':Designations_Serializer.data})     
        except M_Designations.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Designation Not available', 'Data': []})
            
    @transaction.atomic()
    def put(self, request, id=0):
        try:
            with transaction.atomic():
                Designationsdata = JSONParser().parse(request)
                DesignationsdataByID = M_Designations.objects.get(id=id)
                Designations_Serializer = M_DesignationsSerializer(DesignationsdataByID, data=Designationsdata)
                if Designations_Serializer.is_valid():
                    Designations_Serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Designation Updated Successfully', 'Data': []})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': Designations_Serializer.errors, 'Data':[]})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})   

    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                Designations_data = M_Designations.objects.get(id=id)
                Designations_data.delete()
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Designation Deleted Successfully','Data':[]})
        except M_Designations.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Record Not available', 'Data': []})
        except IntegrityError:   
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Company used in another table', 'Data': []})   