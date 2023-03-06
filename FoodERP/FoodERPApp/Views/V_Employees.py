from django.http import JsonResponse
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, connection, transaction
from rest_framework.parsers import JSONParser
from ..Serializer.S_Employees import *
from ..models import *


class M_EmployeesFilterView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                Logindata = JSONParser().parse(request)
                UserID = Logindata['UserID']   
                RoleID=  Logindata['RoleID']  
                CompanyID=Logindata['CompanyID']  

                if (RoleID == 1):
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
                else:
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
where M_Employees.CreatedBy=%s
''',[UserID])
                if not query:
                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Employees Not available', 'Data': []})
                else:
                    M_Employees_Serializer = M_EmployeesSerializer02(
                        query, many=True).data
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': M_Employees_Serializer})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})   



class M_EmployeesView(CreateAPIView):

    permission_classes = (IsAuthenticated,)
    authentication__Class = JSONWebTokenAuthentication

    
    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                M_Employeesdata = JSONParser().parse(request)
                M_Employees_Serializer = M_EmployeesSerializer(
                    data=M_Employeesdata)
                if M_Employees_Serializer.is_valid():
                    M_Employees_Serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Employee Data Save Successfully', 'Data': []})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': M_Employees_Serializer.errors, 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})   


class M_EmployeesViewSecond(RetrieveAPIView):

    permission_classes = (IsAuthenticated,)
    authentication__Class = JSONWebTokenAuthentication

    def get(self, request, id=0):
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
JOIN M_Districts ON M_Districts.id=M_Employees.District_id where M_Employees.id= %s''', [id])
                if not query:
                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Employee Not available', 'Data': []})
                else:
                    M_Employees_Serializer = M_EmployeesSerializer02(
                        query, many=True).data
                    
                    GetAllData = list()

                    Employeeparties = MC_EmployeeParties.objects.raw('''SELECT Party_id as id, m_parties.Name FROM mc_employeeparties join m_parties on m_parties.id = mc_employeeparties.Party_id where Employee_id=%s''', ([id]))
                    EmployeepartiesData_Serializer = EmployeepartiesDataSerializer(Employeeparties, many=True).data
                    
                    EmployeeParties = list()
                    for a in EmployeepartiesData_Serializer:
                        EmployeeParties.append({
                            'id': a['id'],
                            'Name': a['Name']
                        })
                    
                    GetAllData.append({
                    'id':  M_Employees_Serializer[0]['id'],
                        'Name':  M_Employees_Serializer[0]['Name'],
                        'Address':  M_Employees_Serializer[0]['Address'],
                        'Mobile': M_Employees_Serializer[0]['Mobile'],
                        'email': M_Employees_Serializer[0]['email'],
                        'DOB' : M_Employees_Serializer[0]['DOB'],
                        'PAN' : M_Employees_Serializer[0]['PAN'],
                        'AadharNo':M_Employees_Serializer[0]['AadharNo'],
                        'working_hours' : M_Employees_Serializer[0]['working_hours'],
                        'CreatedBy':M_Employees_Serializer[0]['CreatedBy'],
                        'CreatedOn' :  M_Employees_Serializer[0]['CreatedOn'],
                        'UpdatedBy': M_Employees_Serializer[0]['UpdatedBy'],
                        'UpdatedOn':M_Employees_Serializer[0]['UpdatedOn'],
                        'CompanyName':M_Employees_Serializer[0]['CompanyName'],
                        'DesignationName':  M_Employees_Serializer[0]['DesignationName'],
                        'EmployeeTypeName' : M_Employees_Serializer[0]['EmployeeTypeName'],
                        'StateName' :  M_Employees_Serializer[0]['StateName'],
                        'DistrictName' :  M_Employees_Serializer[0]['DistrictName'],
                        'Company_id':  M_Employees_Serializer[0]['Company_id'],
                        'Designation_id':  M_Employees_Serializer[0]['Designation_id'] ,
                        'EmployeeType_id':  M_Employees_Serializer[0]['EmployeeType_id'],
                        'State_id': M_Employees_Serializer[0]['State_id'],
                        'District_id' :  M_Employees_Serializer[0]['District_id'],
                        'EmployeeParties' : EmployeeParties
                        })
 
                    return JsonResponse ( {"StatusCode": 200, "Status": True, "Message": " ", "Data": GetAllData[0]}  )   
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})   

    @transaction.atomic()
    def put(self, request, id=0):
        try:
            with transaction.atomic():
                M_Employeesdata = JSONParser().parse(request)
                M_EmployeesdataByID = M_Employees.objects.get(id=id)

                M_Employees_Serializer = M_EmployeesSerializer(
                    M_EmployeesdataByID, data=M_Employeesdata)
                if M_Employees_Serializer.is_valid():
                    M_Employees_Serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Employee Updated Successfully', 'Data': []})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': M_Employees_Serializer.errors, 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})

    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                M_Employeesdata = M_Employees.objects.get(id=id)
                M_Employeesdata.delete()
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Employee data Deleted Successfully', 'Data': []})
        except M_Employees.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Record Not available', 'Data': []})
        except IntegrityError:
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Employee used in another table', 'Data': []})
