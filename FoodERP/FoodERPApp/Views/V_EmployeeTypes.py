from django.http import JsonResponse
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
# from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError,transaction
from rest_framework.parsers import JSONParser
from ..Serializer.S_EmployeeTypes import  *
from ..models import *


class M_EmployeeTypeView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request, id=0):
        try:
            with transaction.atomic():
                M_EmployeeTypedata = JSONParser().parse(request)
                M_EmployeeType_serializer = M_EmployeeTypeSerializer(data=M_EmployeeTypedata)
                if M_EmployeeType_serializer.is_valid():
                    M_EmployeeType_serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Employee Type Save Successfully', 'Data':[]})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message':  M_EmployeeType_serializer.errors,  'Data':[]})
        except Exception :
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  'Exception Found', 'Data': []})
                   
class M_EmployeeTypeFilterView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication 
    
    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                EmployeeType_data = JSONParser().parse(request)
                Company = EmployeeType_data['CompanyID']
                query = M_EmployeeTypes.objects.filter(Company=Company)
                
                if query:
                    EmpType_serializer = M_EmployeeTypeSerializer(query,many=True).data
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': EmpType_serializer})
                return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'Employee Type Not available', 'Data': []})    
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  e, 'Data': []})                  


class M_EmployeeTypeViewSecond(RetrieveAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request, id=0):
        try:
            with transaction.atomic():
                EmployeeType_data = M_EmployeeTypes.objects.get(id=id)
                EmployeeType_Serializer = M_EmployeeTypeSerializer(EmployeeType_data)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':'', 'Data': EmployeeType_Serializer.data})
        except M_EmployeeTypes.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'Employee Type Not available', 'Data': []})

    @transaction.atomic()
    def put(self, request, id=0):
        try:
            with transaction.atomic():
                EmployeeType_data = JSONParser().parse(request)
                EmployeeType_dataByID = M_EmployeeTypes.objects.get(id=id)
                EmployeeType_Serializer = M_EmployeeTypeSerializer(EmployeeType_dataByID, data=EmployeeType_data)
                if EmployeeType_Serializer.is_valid():
                    EmployeeType_Serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'EmployeeType Updated Successfully', 'Data' : []})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': EmployeeType_Serializer.errors, 'Data' : []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})   

    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                EmployeeType_data = M_EmployeeTypes.objects.get(id=id)
                EmployeeType_data.delete()
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'EmployeeType Deleted Successfully', 'Data':[]})
        except M_EmployeeTypes.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'EmployeeType Not available', 'Data': []}) 
        except IntegrityError:   
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'EmployeeType used in another table', 'Data': []})   