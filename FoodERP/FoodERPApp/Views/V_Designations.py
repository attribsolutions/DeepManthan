from django.http import JsonResponse
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import connection, transaction
from rest_framework.parsers import JSONParser

from ..Serializer.S_Designations import M_DesignationsSerializer

from ..models import *

class M_DesignationsView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request):
        try:
            with transaction.atomic():
                M_Designations_data = M_Designations.objects.all()
                M_Designations_serializer = M_DesignationsSerializer(M_Designations_data, many=True)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': M_Designations_serializer.data})
        except Exception as e:
            raise Exception(e)
            print(e)

    @transaction.atomic()
    def post(self, request, id=0):
        try:
            with transaction.atomic():
                Designationsdata = JSONParser().parse(request)
                Designationsdata_Serializer = M_DesignationsSerializer(data=Designationsdata)
                if Designationsdata_Serializer.is_valid():
                    Designationsdata_Serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Designation Save Successfully'})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':  Designationsdata_Serializer.errors})
        except Exception as e:
            raise JsonResponse({'StatusCode': 200, 'Status': True, 'Message':  Exception(e)})
            print(e)        

class M_DesignationsViewSecond(RetrieveAPIView):
    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request, id=0):
        try:
            with transaction.atomic():
                M_Designations_data = M_Designations.objects.get(id=id)
                M_Designations_Serializer = M_DesignationsSerializer(M_Designations_data)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': M_Designations_Serializer.data})
        except Exception as e:
            raise Exception(e)
            print(e)

    @transaction.atomic()
    def put(self, request, id=0):
        try:
            with transaction.atomic():
                Designationsdata = JSONParser().parse(request)
                DesignationsdataByID = M_Designations.objects.get(ID=id)
                Designations_Serializer = M_DesignationsSerializer(
                    DesignationsdataByID, data=Designationsdata)
                if Designations_Serializer.is_valid():
                    Designations_Serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Designation Updated Successfully'})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': Designations_Serializer.errors})
        except Exception as e:
            raise Exception(e)
            print(e)

    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                Designationsdata = M_Designations.objects.get(ID=id)
                Designationsdata.delete()
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Designation Deleted Successfully'})
        except Exception as e:
            raise Exception(e)
            print(e)