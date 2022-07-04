from django.http import JsonResponse
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, connection, transaction
from rest_framework.parsers import JSONParser

from ..Serializer.S_Companies import *

from ..models import C_Companies


class C_CompaniesView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request):
        try:
            with transaction.atomic():
                Companiesdata = C_Companies.objects.all()
                if Companiesdata.exists():
                    Companies_Serializer = C_CompanySerializer1(Companiesdata, many=True)
                    return JsonResponse({'StatusCode': 200, 'Status': True,'Message': '','Data': Companies_Serializer.data})
                return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'Companies Not Available', 'Data': []})    
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})


    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                Companiesdata = JSONParser().parse(request)
                Companies_Serializer = C_CompanySerializer2(data=Companiesdata)
                if Companies_Serializer.is_valid():
                    Companies_Serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Company Save Successfully', 'Data':[]})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message':  Companies_Serializer.errors, 'Data':[]})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})
            


class C_CompaniesViewSecond(CreateAPIView):

    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication
    
    def get(self, request, id=0 ):
        try:
            with transaction.atomic():
                query = C_Companies.objects.raw('''SELECT c_companies.id,c_companies.Name,c_companies.Address,c_companies.GSTIN,c_companies.PhoneNo,c_companies.GSTIN,c_companies.CompanyAbbreviation,c_companies.EmailID,c_companies.CreatedBy,c_companies.CreatedOn,c_companies.UpdatedBy,c_companies.UpdatedOn,c_companies.CompanyGroup_id,c_companygroups.Name CompanyGroupName FROM erpdatabase.c_companies
JOIN c_companygroups ON c_companygroups.id=c_companies.CompanyGroup_id
WHERE c_companies.id = %s''',[id])
                if not query:
                    return JsonResponse({'StatusCode': 204, 'Status': True,'Message': 'Employee Not available', 'Data': []})
                else:    
                    Companies_Serializer = C_CompanySerializer3(query, many=True).data
                    return JsonResponse({'StatusCode': 200, 'Status': True,'Message': '','Data': Companies_Serializer[0]})   
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})
            

    @transaction.atomic()
    def put(self, request, id=0):
        try:
            with transaction.atomic():
                Companiesdata = JSONParser().parse(request)
                CompaniesdataByID = C_Companies.objects.get(id=id)
                Companies_Serializer = C_CompanySerializer2(
                    CompaniesdataByID, data=Companiesdata)
                if Companies_Serializer.is_valid():
                    Companies_Serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Company Updated Successfully', 'Data':[]})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': Companies_Serializer.errors, 'Data':[]})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})
        

    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                Companiesdata = C_Companies.objects.get(id=id)
                Companiesdata.delete()
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Company Deleted Successfully', 'Data':[]})
        except C_Companies.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Company Not available', 'Data': []})
           



class C_CompanyGroupsView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request):
        try:
            with transaction.atomic():
                CompaniesGroupsdata = C_CompanyGroups.objects.all()
                if CompaniesGroupsdata.exists():
                    CompaniesGroups_Serializer = C_CompanyGroupsSerializer(CompaniesGroupsdata, many=True)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':'', 'Data': CompaniesGroups_Serializer.data})
                return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'Company Groups Not available', 'Data': []})        
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})
            

    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                Companiesdata = JSONParser().parse(request)
                Companies_Serializer = C_CompanyGroupsSerializer(
                    data=Companiesdata)
                if Companies_Serializer.is_valid():
                    Companies_Serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Company Group Save Successfully', 'Data':[]})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': Companies_Serializer.errors, 'Data':[]})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})
           


class C_CompanyGroupsViewSecond(CreateAPIView):

    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request, id=0):
        try:
            with transaction.atomic():
                CompaniesGroupsdata = C_CompanyGroups.objects.get(id=id)
                CompaniesGroupsdata_Serializer = C_CompanyGroupsSerializer(CompaniesGroupsdata)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':'', 'Data': CompaniesGroupsdata_Serializer.data})
        except C_CompanyGroups.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Company Group Not available', 'Data': []})
            

    @transaction.atomic()
    def put(self, request, id=0):
        try:
            with transaction.atomic():
                CompaniesGropusdata = JSONParser().parse(request)
                CompaniesGropusdataByID = C_CompanyGroups.objects.get(id=id)
                CompaniesGropus_Serializer = C_CompanyGroupsSerializer(
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
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'ID used in another tbale', 'Data': []})  