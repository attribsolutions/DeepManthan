from django.http import JsonResponse
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
# from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError,transaction
from rest_framework.parsers import JSONParser
from ..Serializer.S_EmployeeTypes import  *
from ..models import *
from .V_CommFunction import *

class M_EmployeeTypeView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request, id=0):
        M_EmployeeTypedata = JSONParser().parse(request)
        try:
            with transaction.atomic():
                M_EmployeeType_serializer = M_EmployeeTypeSerializer(data=M_EmployeeTypedata)
                if M_EmployeeType_serializer.is_valid():
                    EmployeeType = M_EmployeeType_serializer.save()
                    LastInsertID = EmployeeType.id
                    log_entry = create_transaction_logNew(request, M_EmployeeTypedata, 0,'TransactionID:'+str(LastInsertID),232,LastInsertID)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Employee Type Save Successfully','TransactionID':LastInsertID, 'Data':[]})
                else:
                    log_entry = create_transaction_logNew(request, M_EmployeeTypedata, 0,'EmployeeTypeSave:'+str(M_EmployeeType_serializer.errors),34,0)
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message':  M_EmployeeType_serializer.errors,  'Data':[]})
        except Exception :
            log_entry = create_transaction_logNew(request, M_EmployeeTypedata, 0,'EmployeeTypeSave:'+'Exception Found',33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  'Exception Found', 'Data': []})
                   
class M_EmployeeTypeFilterView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication 
    
    @transaction.atomic()
    def post(self, request):
        EmployeeType_data = JSONParser().parse(request)
        try:
            with transaction.atomic():
                Company = EmployeeType_data['CompanyID']
                query = M_EmployeeTypes.objects.filter(Company=Company)
                
                if query:
                    EmpType_serializer = M_EmployeeTypeSerializer(query,many=True).data
                    log_entry = create_transaction_logNew(request, EmployeeType_data, 0,'',233,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': EmpType_serializer})
                log_entry = create_transaction_logNew(request, EmployeeType_data, 0,'EmployeeType Not available',233,0)
                return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'Employee Type Not available', 'Data': []})    
        except Exception as e:
            log_entry = create_transaction_logNew(request, EmployeeType_data, 0,'EmployeeTypeList'+str(e),33,0)
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
                log_entry = create_transaction_logNew(request, 0, 0,'EmployeeID:'+str(id),234,id)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':'', 'Data': EmployeeType_Serializer.data})
        except M_EmployeeTypes.DoesNotExist:
            log_entry = create_transaction_logNew(request, 0, 0,'Employee Type Not available',234,0)
            return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'Employee Type Not available', 'Data': []})

    @transaction.atomic()
    def put(self, request, id=0):
        EmployeeType_data = JSONParser().parse(request)
        try:
            with transaction.atomic():
                EmployeeType_dataByID = M_EmployeeTypes.objects.get(id=id)
                EmployeeType_Serializer = M_EmployeeTypeSerializer(EmployeeType_dataByID, data=EmployeeType_data)
                if EmployeeType_Serializer.is_valid():
                    EmployeeType = EmployeeType_Serializer.save()
                    LastInsertID = EmployeeType.id
                    log_entry = create_transaction_logNew(request, EmployeeType_data, 0,'TransactionID:'+str(LastInsertID),235,LastInsertID)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'EmployeeType Updated Successfully', 'Data' : []})
                else:
                    log_entry = create_transaction_logNew(request, EmployeeType_data, 0,'EmployeeTypeEdit:'+str(EmployeeType_Serializer.errors),34,0)
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': EmployeeType_Serializer.errors, 'Data' : []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, EmployeeType_data, 0,'EmployeeTypeEdit:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})   

    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                EmployeeType_data = M_EmployeeTypes.objects.get(id=id)
                EmployeeType_data.delete()
                log_entry = create_transaction_logNew(request, 0, 0,'EmployeeID:'+str(id),236,id)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'EmployeeType Deleted Successfully', 'Data':[]})
        except M_EmployeeTypes.DoesNotExist:
            log_entry = create_transaction_logNew(request, 0, 0,'EmployeeType Not available',236,0)
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'EmployeeType Not available', 'Data': []}) 
        except IntegrityError:   
            log_entry = create_transaction_logNew(request, 0, 0,'EmployeeTypeDelete:'+'EmployeeType used in another table',8,0)
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'EmployeeType used in another table', 'Data': []})   