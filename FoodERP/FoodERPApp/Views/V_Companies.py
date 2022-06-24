from django.http import JsonResponse
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import connection, transaction
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
                    Companies_Serializer = C_CompanySerializer2(Companiesdata, many=True)
                    return JsonResponse({'StatusCode': 200, 'Status': True,'Message': '','Data': Companies_Serializer.data})
                return JsonResponse({'StatusCode': 200, 'Status': True,'Message':  'Companies Not Available', 'Data': []})    
        except Exception as e:
            raise JsonResponse({'StatusCode': 200, 'Status': True, 'Message':  Exception(e), 'Data':[]})


    @transaction.atomic()
    def post(self, request, id=0):
        try:
            with transaction.atomic():
                Companiesdata = JSONParser().parse(request)
                Companies_Serializer = C_CompanySerializer(data=Companiesdata)
                if Companies_Serializer.is_valid():
                    Companies_Serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Company Save Successfully', 'Data':[]})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':  C_CompanySerializer2.errors, 'Data':[]})
        except Exception as e:
            raise JsonResponse({'StatusCode': 200, 'Status': True, 'Message':  Exception(e), 'Data':[]})
            


class C_CompaniesViewSecond(CreateAPIView):

    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request, id=0):
        try:
            with transaction.atomic():
                Companiesdata = C_Companies.objects.get(ID=id)
                if Companiesdata.exists():
                    Companies_Serializer = C_CompanySerializer2(Companiesdata)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':'', 'Data': Companies_Serializer.data})
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':'Company Not Available', 'Data':[]})    
        except Exception as e:
            raise JsonResponse({'StatusCode': 200, 'Status': True, 'Message':  Exception(e), 'Data':[]})
            

    @transaction.atomic()
    def put(self, request, id=0):
        try:
            with transaction.atomic():
                Companiesdata = JSONParser().parse(request)
                CompaniesdataByID = C_Companies.objects.get(ID=id)
                Companies_Serializer = C_CompanySerializer(
                    CompaniesdataByID, data=Companiesdata)
                if Companies_Serializer.is_valid():
                    Companies_Serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Company Updated Successfully', 'Data':[]})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': Companies_Serializer.errors, 'Data':[]})
        except Exception as e:
            raise JsonResponse({'StatusCode': 200, 'Status': True, 'Message':  Exception(e), 'Data':[]})
        

    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                Companiesdata = C_Companies.objects.get(ID=id)
                Companiesdata.delete()
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Company Deleted Successfully', 'Data':[]})
        except Exception as e:
            raise JsonResponse({'StatusCode': 200, 'Status': True, 'Message':  Exception(e), 'Data':[]})
           



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
                return JsonResponse({'StatusCode': 200, 'Status': True,'Message':  'Company Groups Not available', 'Data': []})        
        except Exception as e:
            raise JsonResponse({'StatusCode': 200, 'Status': True, 'Message':  Exception(e), 'Data':[]})
            

    @transaction.atomic()
    def post(self, request, id=0):
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
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': Companies_Serializer.errors, 'Data':[]})
        except Exception as e:
            raise JsonResponse({'StatusCode': 200, 'Status': True, 'Message':  Exception(e), 'Data':[]})
           


class C_CompanyGroupsViewSecond(CreateAPIView):

    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request, id=0):
        try:
            with transaction.atomic():
                Companiesdata = C_CompanyGroups.objects.filter(ID=id)
                if Companiesdata.exists():
                    Companies_Serializer = C_CompanyGroupsSerializer(Companiesdata)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':'', 'Data': Companies_Serializer.data})
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':'Company Not Available', 'Data': []})    
        except Exception as e:
            raise JsonResponse({'StatusCode': 200, 'Status': True, 'Message':  Exception(e), 'Data':[]})
            

    @transaction.atomic()
    def put(self, request, id=0):
        try:
            with transaction.atomic():
                CompaniesGropusdata = JSONParser().parse(request)
                CompaniesGropusdataByID = C_CompanyGroups.objects.get(ID=id)
                CompaniesGropus_Serializer = C_CompanyGroupsSerializer(
                    CompaniesGropusdataByID, data=CompaniesGropusdata)
                if CompaniesGropus_Serializer.is_valid():
                    CompaniesGropus_Serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Company Group Updated Successfully', 'Data':[]})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': CompaniesGropus_Serializer.errors, 'Data':[]})
        except Exception as e:
            raise JsonResponse({'StatusCode': 200, 'Status': True, 'Message':  Exception(e), 'Data':[]})
           

    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                CompaniesGropusdata = C_CompanyGroups.objects.get(ID=id)
                CompaniesGropusdata.delete()
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Company Group  Deleted Successfully', 'Data':[]})
        except Exception as e:
            raise JsonResponse({'StatusCode': 200, 'Status': True, 'Message':  Exception(e), 'Data':[]})
                       