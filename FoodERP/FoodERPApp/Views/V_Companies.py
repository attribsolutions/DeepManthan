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
                Companies_Serializer = C_CompanySerializer2(
                    Companiesdata, many=True)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': Companies_Serializer.data})

        except Exception as e:
            raise Exception(e)
            print(e)

    @transaction.atomic()
    def post(self, request, id=0):
        try:
            with transaction.atomic():
                Companiesdata = JSONParser().parse(request)
                Companies_Serializer = C_CompanySerializer(data=Companiesdata)
                if Companies_Serializer.is_valid():
                    Companies_Serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Company Save Successfully'})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':  C_CompanySerializer2.errors})
        except Exception as e:
            raise JsonResponse({'StatusCode': 200, 'Status': True, 'Message':  Exception(e)})
            print(e)


class C_CompaniesViewSecond(CreateAPIView):

    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request, id=0):
        try:
            with transaction.atomic():
                Companiesdata = C_Companies.objects.get(ID=id)
                Companies_Serializer = C_CompanySerializer2(Companiesdata)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': Companies_Serializer.data})
        except Exception as e:
            raise Exception(e)
            print(e)

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
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Company Updated Successfully'})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': Companies_Serializer.errors})
        except Exception as e:
            raise Exception(e)
            print(e)

    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                Companiesdata = C_Companies.objects.get(ID=id)
                Companiesdata.delete()
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Company Deleted Successfully'})
        except Exception as e:
            raise Exception(e)
            print(e)



class C_CompanyGroupsView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request):
        try:
            with transaction.atomic():
                Companiesdata = C_CompanyGroups.objects.all()
                Companies_Serializer = C_CompanyGroupsSerializer(
                    Companiesdata, many=True)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': Companies_Serializer.data})
        except Exception as e:
            raise Exception(e)
            print(e)

    @transaction.atomic()
    def post(self, request, id=0):
        try:
            with transaction.atomic():
                Companiesdata = JSONParser().parse(request)
                Companies_Serializer = C_CompanyGroupsSerializer(
                    data=Companiesdata)
                if Companies_Serializer.is_valid():
                    Companies_Serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Company Group Save Successfully'})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': Companies_Serializer.errors})
        except Exception as e:
            raise Exception(e)
            print(e)


class C_CompanyGroupsViewSecond(CreateAPIView):

    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request, id=0):
        try:
            with transaction.atomic():
                Companiesdata = C_CompanyGroups.objects.filter(ID=id)
                Companies_Serializer = C_CompanyGroupsSerializer(
                    Companiesdata)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': Companies_Serializer.data})
        except Exception as e:
            raise Exception(e)
            print(e)

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
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Company Group Updated Successfully'})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': CompaniesGropus_Serializer.errors})
        except Exception as e:
            raise Exception(e)
            print(e)

    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                CompaniesGropusdata = C_CompanyGroups.objects.get(ID=id)
                CompaniesGropusdata.delete()
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Company Group  Deleted Successfully'})
        except Exception as e:
            raise Exception(e)
            print(e)            