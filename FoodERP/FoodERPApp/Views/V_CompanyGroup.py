from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
# from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, transaction
from rest_framework.parsers import JSONParser


from ..Serializer.S_CompanyGroup import *

from ..models import *


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
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':'', 'Data': CompaniesGroups_Serializer.data})
                return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'Company Groups Not available', 'Data': []})        
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})   
            

    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                Companiesdata = JSONParser().parse(request)
                Companies_Serializer = C_CompanyGroupSerializer(
                    data=Companiesdata)
                if Companies_Serializer.is_valid():
                    Companies_Serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Company Group Save Successfully', 'Data':[]})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': Companies_Serializer.errors, 'Data':[]})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})   
           


class C_CompanyGroupViewSecond(CreateAPIView):

    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request, id=0):
        try:
            with transaction.atomic():
                CompaniesGroupsdata = C_CompanyGroups.objects.get(id=id)
                CompaniesGroupsdata_Serializer = C_CompanyGroupSerializer(CompaniesGroupsdata)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':'', 'Data': CompaniesGroupsdata_Serializer.data})
        except C_CompanyGroups.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Company Group Not available', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]}) 

    @transaction.atomic()
    def put(self, request, id=0):
        try:
            with transaction.atomic():
                CompaniesGropusdata = JSONParser().parse(request)
                CompaniesGropusdataByID = C_CompanyGroups.objects.get(id=id)
                CompaniesGropus_Serializer = C_CompanyGroupSerializer(
                    CompaniesGropusdataByID, data=CompaniesGropusdata)
                if CompaniesGropus_Serializer.is_valid():
                    CompaniesGropus_Serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Company Group Updated Successfully', 'Data':[]})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': CompaniesGropus_Serializer.errors, 'Data':[]})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})
           

    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                CompaniesGropusdata = C_CompanyGroups.objects.get(id=id)
                CompaniesGropusdata.delete()
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Company Group  Deleted Successfully', 'Data':[]})
        except C_CompanyGroups.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Company Group Not available', 'Data': []})
        except IntegrityError:   
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Company Group used in another table', 'Data': []})  