from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
# from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, transaction
from rest_framework.parsers import JSONParser
from ..Serializer.S_CompanyGroup import *
from ..models import *
from ..Views.V_CommFunction import *


class C_CompanyGroupView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request):
        try:
            with transaction.atomic():
                CompaniesGroupsdata = C_CompanyGroups.objects.all()
                if CompaniesGroupsdata.exists():
                    CompaniesGroups_Serializer = C_CompanyGroupSerializerSecond(CompaniesGroupsdata, many=True)
                    log_entry = create_transaction_logNew(request, CompaniesGroups_Serializer,0,'',313,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':'', 'Data': CompaniesGroups_Serializer.data})
                log_entry = create_transaction_logNew(request,0,0,'Companies Groups Data Does Not Exist',313,0)
                return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'Company Groups Not available', 'Data': []})        
        except Exception as e:
            log_entry = create_transaction_logNew(request, 0, 0,'CompaniesGroups:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data':[]})   
            

    @transaction.atomic()
    def post(self, request):
        Companiesdata = JSONParser().parse(request)
        try:
            with transaction.atomic():
                Companies_Serializer = C_CompanyGroupSerializer(
                    data=Companiesdata)
                if Companies_Serializer.is_valid():
                    Companies_Serializer.save()
                    log_entry = create_transaction_logNew(request, Companiesdata,0,'',314,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Company Group Save Successfully', 'Data':[]})
                else:
                    log_entry = create_transaction_logNew(request, Companiesdata,0,'CompanyGroupSave:'+str(Companies_Serializer.errors),34,0)
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': Companies_Serializer.errors, 'Data':[]})
        except Exception as e:
            log_entry = create_transaction_logNew(request, Companiesdata, 0,'CompanyGroupSave:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data':[]})   
           


class C_CompanyGroupViewSecond(CreateAPIView):

    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request, id=0):
        try:
            with transaction.atomic():
                CompaniesGroupsdata = C_CompanyGroups.objects.get(id=id)
                CompaniesGroupsdata_Serializer = C_CompanyGroupSerializer(CompaniesGroupsdata)
                log_entry = create_transaction_logNew(request, CompaniesGroupsdata_Serializer,0,'',315,0)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':'', 'Data': CompaniesGroupsdata_Serializer.data})
        except C_CompanyGroups.DoesNotExist:
            log_entry = create_transaction_logNew(request,0,0,'CompanyGroup Data Does Not Exist',315,0)
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Company Group Not available', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, 0, 0,'CompanyGroup:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data':[]}) 

    @transaction.atomic()
    def put(self, request, id=0):
        CompaniesGropusdata = JSONParser().parse(request)
        try:
            with transaction.atomic():
                CompaniesGropusdataByID = C_CompanyGroups.objects.get(id=id)
                CompaniesGropus_Serializer = C_CompanyGroupSerializer(
                    CompaniesGropusdataByID, data=CompaniesGropusdata)
                if CompaniesGropus_Serializer.is_valid():
                    CompaniesGropus_Serializer.save()
                    log_entry = create_transaction_logNew(request, CompaniesGropusdata,0,'',316,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Company Group Updated Successfully', 'Data':[]})
                else:
                    log_entry = create_transaction_logNew(request, CompaniesGropusdata,0,'CompanyGroupUpdate:'+ str(CompaniesGropus_Serializer.errors),34,0)
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': CompaniesGropus_Serializer.errors, 'Data':[]})
        except Exception as e:
            log_entry = create_transaction_logNew(request, CompaniesGropusdata,0,'CompanyGroupUpdate:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data':[]})
           

    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                CompaniesGropusdata = C_CompanyGroups.objects.get(id=id)
                CompaniesGropusdata.delete()
                log_entry = create_transaction_logNew(request, {'CompanyID':id},0,'',317,0)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Company Group  Deleted Successfully', 'Data':[]})
        except C_CompanyGroups.DoesNotExist:
            log_entry = create_transaction_logNew(request, {'CompanyID':id},0,'',317,0)
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Company Group Not available', 'Data': []})
        except IntegrityError:   
            log_entry = create_transaction_logNew(request, {'CompanyID':id},0,'',8,0)
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Company Group used in another table', 'Data': []})  