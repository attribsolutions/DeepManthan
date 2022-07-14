from django.http import JsonResponse
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, connection, transaction
from rest_framework.parsers import JSONParser

from ..Serializer.S_Roles import M_RolesSerializer

from ..models import *



class M_RolesView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request):
        try:
            with transaction.atomic():
                M_Roles_data = M_Roles.objects.all()
                if M_Roles_data.exists():
                    M_Roles_serializer = M_RolesSerializer(M_Roles_data, many=True)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': M_Roles_serializer.data})
                return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'Role Not available', 'Data': []})
        except Exception as e:
            raise JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})

    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                M_Rolesdata = JSONParser().parse(request)
                M_Roles_Serializer = M_RolesSerializer(data=M_Rolesdata)
            if M_Roles_Serializer.is_valid():
                M_Roles_Serializer.save()
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Role Save Successfully', 'Data' :[]})
            else:
                transaction.set_rollback(True)
                return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': M_Roles_Serializer.errors, 'Data' : []})
        except Exception as e:
            raise JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})


class M_RolesViewSecond(CreateAPIView):

    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request, id=0):
        try:
            with transaction.atomic():
                M_Rolesdata = M_Roles.objects.get(id=id)
                M_Roles_Serializer = M_RolesSerializer(M_Rolesdata)
                return JsonResponse({'StatusCode': 200, 'Status': True,'Message': '', 'Data': M_Roles_Serializer.data})
        except Exception as e:
            raise JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})

    @transaction.atomic()
    def put(self, request, id=0):
        try:
            with transaction.atomic():
                M_Rolesdata = JSONParser().parse(request)
                M_RolesdataByID = M_Roles.objects.get(id=id)
                M_Roles_Serializer = M_RolesSerializer(
                    M_RolesdataByID, data=M_Rolesdata)
                if M_Roles_Serializer.is_valid():
                    M_Roles_Serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Role Updated Successfully','Data' :[]})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': M_Roles_Serializer.errors, 'Data' :[]})
        except Exception as e:
            raise JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})

    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                M_Rolesdata = M_Roles.objects.get(id=id)
                M_Rolesdata.delete()
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Role Deleted Successfully','Data':[]})
        except M_Roles.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Role Not available', 'Data': []})
        except IntegrityError:   
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Role used in another table', 'Data': []})