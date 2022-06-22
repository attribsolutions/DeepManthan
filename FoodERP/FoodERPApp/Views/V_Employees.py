from django.http import JsonResponse
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import connection, transaction
from rest_framework.parsers import JSONParser
from ..Serializer.S_Employees import *
from ..models import *

class M_EmployeesView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication
    
    @transaction.atomic()
    def get(self, request ):
        try:
            with transaction.atomic():
                M_Employeesdata = M_Employees.objects.all()
                if M_Employeesdata.exists():
                    M_Employees_Serializer = M_EmployeesSerializer1(
                    M_Employeesdata, many=True)
                    return JsonResponse({'StatusCode': 200, 'Status': True,'Message': '','Data': M_Employees_Serializer.data })
                return JsonResponse({'StatusCode': 200, 'Status': True,'Message':  'Records Not available', 'Data': []})    
        except Exception as e:
            raise Exception(e)
            
            print(e)

    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                M_Employeesdata = JSONParser().parse(request)
                M_Employees_Serializer = M_EmployeesSerializer(data=M_Employeesdata)
                if M_Employees_Serializer.is_valid():
                    M_Employees_Serializer.save()
                   
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Employee Data Save Successfully','Data' :''})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': M_Employees_Serializer.errors,'Data': ''})
        except Exception as e:
            raise Exception(e)
            print(e)


class M_EmployeesViewSecond(RetrieveAPIView):
    
    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request, id=0):
        try:
            with transaction.atomic():
                M_Employeesdata = M_Employees.objects.filter(id=id)
                if M_Employeesdata.exists():
                    M_Employees_Serializer = M_EmployeesSerializer1(M_Employeesdata, many=True)
                    return JsonResponse({'StatusCode': 200, 'Status': True,'Message': '','Data': M_Employees_Serializer.data})
                return JsonResponse({'StatusCode': 200, 'Status': True,'Message':  'Records Not available', 'Data': ''})    
        except Exception as e:
            raise Exception(e)
            
            print(e)
        
    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                M_Employeesdata = M_Employees.objects.get(id=id)
                M_Employeesdata.delete()
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Employee data Deleted Successfully','Data' : ''})
        except Exception as e:
            raise Exception(e)
            print(e)

    @transaction.atomic()
    def put(self, request, id=0):
        try:
            with transaction.atomic():
                M_Employeesdata = JSONParser().parse(request)
                M_EmployeesdataByID = M_Employees.objects.get(id=id)
               
                M_Employees_Serializer = M_EmployeesSerializer(M_EmployeesdataByID, data=M_Employeesdata)
                if M_Employees_Serializer.is_valid():
                    M_Employees_Serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Employee Updated Successfully','Data':''})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': M_Employees_Serializer.errors,'Data' :''})
                
        except Exception as e:
            raise Exception(e)
            print(e)            
