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
    
    def get(self, request, id=0 ):
        try:
            with transaction.atomic():
                query = M_Employees.objects.raw('''SELECT m_employees.id,m_employees.Name,m_employees.Address,m_employees.Mobile,m_employees.email,m_employees.DOB,
m_employees.PAN,m_employees.AadharNo,m_employees.working_hours,m_employees.CreatedBy,m_employees.CreatedOn,
m_employees.UpdatedBy,m_employees.UpdatedOn,c_companies.Name CompanyName,m_designations.Name DesignationName,
m_employeetypes.Name EmployeeTypeName,m_states.Name StateName,m_employees.Companies_id,m_employees.Designation_id,m_employees.EmployeeType_id,m_employees.State_id 
FROM m_employees
JOIN c_companies ON c_companies.ID=m_employees.Companies_id
JOIN m_designations ON m_designations.id=m_employees.Designation_id
JOIN m_employeetypes ON m_employeetypes.id=m_employees.EmployeeType_id
JOIN m_states ON m_states.id=m_employees.State_id''')
                M_Employees_Serializer = M_EmployeesSerializer02(query, many=True).data
                
                return JsonResponse({'StatusCode': 200, 'Status': True,'Message': '','Data': M_Employees_Serializer})   
        except Exception as e:
            raise Exception(e)
            
            print(e)

    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                M_Employeesdata = JSONParser().parse(request)
                M_Employees_Serializer = M_EmployeesSerializer01(data=M_Employeesdata)
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

    def get(self, request, id=0 ):
        try:
            with transaction.atomic():
                query = M_Employees.objects.raw('''SELECT m_employees.id,m_employees.Name,m_employees.Address,m_employees.Mobile,m_employees.email,m_employees.DOB,
m_employees.PAN,m_employees.AadharNo,m_employees.working_hours,m_employees.CreatedBy,m_employees.CreatedOn,
m_employees.UpdatedBy,m_employees.UpdatedOn,c_companies.Name CompanyName,m_designations.Name DesignationName,
m_employeetypes.Name EmployeeTypeName,m_states.Name StateName,m_employees.Companies_id,m_employees.Designation_id,m_employees.EmployeeType_id,m_employees.State_id 
FROM m_employees
JOIN c_companies ON c_companies.ID=m_employees.Companies_id
JOIN m_designations ON m_designations.id=m_employees.Designation_id
JOIN m_employeetypes ON m_employeetypes.id=m_employees.EmployeeType_id
JOIN m_states ON m_states.id=m_employees.State_id where m_employees.id= %s''',[id])
                M_Employees_Serializer = M_EmployeesSerializer02(query, many=True).data
                return JsonResponse({'StatusCode': 200, 'Status': True,'Message': '','Data': M_Employees_Serializer})   
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
               
                M_Employees_Serializer = M_EmployeesSerializer01(M_EmployeesdataByID, data=M_Employeesdata)
                if M_Employees_Serializer.is_valid():
                    M_Employees_Serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Employee Updated Successfully','Data':''})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': M_Employees_Serializer.errors,'Data' :''})
                
        except Exception as e:
            raise Exception(e)
            print(e)            
