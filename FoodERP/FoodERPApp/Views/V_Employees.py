from django.http import JsonResponse
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, connection, transaction
from rest_framework.parsers import JSONParser
from ..Serializer.S_Employees import *
from ..models import *

class M_EmployeesView(CreateAPIView):

    permission_classes = (IsAuthenticated,)
    authentication__Class = JSONWebTokenAuthentication
    
    def get(self, request, id=0 ):
        try:
            with transaction.atomic():
                query = M_Employees.objects.raw('''SELECT M_Employees.id,M_Employees.Name,M_Employees.Address,M_Employees.Mobile,M_Employees.email,M_Employees.DOB,
M_Employees.PAN,M_Employees.AadharNo,M_Employees.working_hours,M_Employees.CreatedBy,M_Employees.CreatedOn,
M_Employees.UpdatedBy,M_Employees.UpdatedOn,C_Companies.Name CompanyName,M_Designations.Name DesignationName,
M_EmployeeTypes.Name EmployeeTypeName,M_States.Name StateName,M_Districts.Name DistrictName,M_Employees.Company_id,M_Employees.Designation_id,M_Employees.EmployeeType_id,M_Employees.State_id,M_Employees.District_id 
FROM M_Employees
JOIN C_Companies ON C_Companies.id=M_Employees.Company_id
JOIN M_Designations ON M_Designations.id=M_Employees.Designation_id
JOIN M_EmployeeTypes ON M_EmployeeTypes.id=M_Employees.EmployeeType_id
JOIN M_States ON M_States.id=M_Employees.State_id
JOIN M_Districts ON M_Districts.id=M_Employees.District_id
''')
                if not query:
                    return JsonResponse({'StatusCode': 204, 'Status': True,'Message': 'Employees Not available','Data': []})
                else:    
                    M_Employees_Serializer = M_EmployeesSerializer02(query, many=True).data
                    return JsonResponse({'StatusCode': 200, 'Status': True,'Message': '','Data': M_Employees_Serializer})   
        except Exception as e:
           return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})
            
         
    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                M_Employeesdata = JSONParser().parse(request)
                M_Employees_Serializer = M_EmployeesSerializer(data=M_Employeesdata)
                if M_Employees_Serializer.is_valid():
                    M_Employees_Serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Employee Data Save Successfully','Data' :[]})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': M_Employees_Serializer.errors,'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})


class M_EmployeesViewSecond(RetrieveAPIView):
    
    permission_classes = (IsAuthenticated,)
    authentication__Class = JSONWebTokenAuthentication

    def get(self, request, id=0 ):
        try:
            with transaction.atomic():
                query = M_Employees.objects.raw('''SELECT M_Employees.id,M_Employees.Name,M_Employees.Address,M_Employees.Mobile,M_Employees.email,M_Employees.DOB,
M_Employees.PAN,M_Employees.AadharNo,M_Employees.working_hours,M_Employees.CreatedBy,M_Employees.CreatedOn,
M_Employees.UpdatedBy,M_Employees.UpdatedOn,C_Companies.Name CompanyName,M_Designations.Name DesignationName,
M_EmployeeTypes.Name EmployeeTypeName,M_States.Name StateName,M_Districts.Name DistrictName,M_Employees.Company_id,M_Employees.Designation_id,M_Employees.EmployeeType_id,M_Employees.State_id,M_Employees.District_id 
FROM M_Employees
JOIN C_Companies ON C_Companies.id=M_Employees.Company_id
JOIN M_Designations ON M_Designations.id=M_Employees.Designation_id
JOIN M_EmployeeTypes ON M_EmployeeTypes.id=M_Employees.EmployeeType_id
JOIN M_States ON M_States.id=M_Employees.State_id
JOIN M_Districts ON M_Districts.id=M_Employees.District_id where M_Employees.id= %s''',[id])
                if not query:
                    return JsonResponse({'StatusCode': 204, 'Status': True,'Message': 'Employee Not available', 'Data': []})
                else:    
                    M_Employees_Serializer = M_EmployeesSerializer02(query, many=True).data
                    return JsonResponse({'StatusCode': 200, 'Status': True,'Message': '','Data': M_Employees_Serializer[0]})   
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})

    @transaction.atomic()
    def put(self, request, id=0):
        try:
            with transaction.atomic():
                M_Employeesdata = JSONParser().parse(request)
                M_EmployeesdataByID = M_Employees.objects.get(id=id)
               
                M_Employees_Serializer = M_EmployeesSerializer(M_EmployeesdataByID, data=M_Employeesdata)
                if M_Employees_Serializer.is_valid():
                    M_Employees_Serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Employee Updated Successfully','Data':[]})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': M_Employees_Serializer.errors,'Data' :[]})    
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})            

    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                M_Employeesdata = M_Employees.objects.get(id=id)
                M_Employeesdata.delete()
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Employee data Deleted Successfully','Data' :[]})
        except M_Employees.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Record Not available', 'Data': []})
        except IntegrityError:   
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Employee used in another table', 'Data': []})