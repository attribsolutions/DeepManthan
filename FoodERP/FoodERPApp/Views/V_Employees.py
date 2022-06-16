from django.http import JsonResponse
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import connection, transaction
from rest_framework.parsers import JSONParser

from  ..Serializer.S_Employees import *
from ..models import *

 
class M_EmployessView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication
    
    @transaction.atomic()
    def get(self, request ):
        try:
            with transaction.atomic():
                M_Employessdata = M_Employess.objects.all()
                if M_Employessdata.exists():
                    M_Employess_Serializer = M_EmployessSerializer(
                    M_Employessdata, many=True)
                    return JsonResponse({'StatusCode': 200, 'Status': True,'Message': '','Data': M_Employess_Serializer.data})
                return JsonResponse({'StatusCode': 200, 'Status': True,'Message':  'Records Not available', 'Data': []})    
        except Exception as e:
            raise Exception(e)
            print(e)

    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                M_Employessdata = JSONParser().parse(request)
                M_Employess_Serializer = M_EmployessSerializer(data=M_Employessdata)
                if M_Employess_Serializer.is_valid():
                    M_Employess_Serializer.save()
                   
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Data Save Successfully','Data' :''})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': M_Employess_Serializer.errors,'Data': ''})
        except Exception as e:
            raise Exception(e)
            print(e)     


class M_EmployessViewSecond(CreateAPIView):

    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request, id=0):
        try:
            with transaction.atomic():
                M_Employessdata = M_Employess.objects.get(ID=id)
                M_Employess_Serializer = M_EmployessSerializer(M_Employessdata)
                return JsonResponse({'StatusCode': 200, 'Status': True,'Message': '', 'Data': M_Employess_Serializer.data})
        except Exception as e:
            raise Exception(e)


    @transaction.atomic()
    def put(self, request, id=0):
        try:
            with transaction.atomic():
                M_Employessdata = JSONParser().parse(request)
                M_EmployessdataByID = M_Employess.objects.get(ID=id)
                M_Employess_Serializer = M_EmployessSerializer(
                    M_EmployessdataByID, data=M_Employessdata)
                if M_Employess_Serializer.is_valid():
                    M_Employess_Serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Employee Updated Successfully','Data' : ''})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': M_Employess_Serializer.errors,'Data' : ''})
        except Exception as e:
            raise Exception(e)

    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                M_Employessdata = M_Employess.objects.get(ID=id)
                M_Employessdata.delete()
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Employee Deleted Successfully','Data':''})
        except Exception as e:
            raise Exception(e)
 