from django.http import JsonResponse
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import connection, transaction
from rest_framework.parsers import JSONParser

from ..Serializer.S_ItemsGroup import *

from ..models import *



class ItemsGroupView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request):
        try:
            with transaction.atomic():
                ItemsGroup_data = M_ItemsGroup.objects.all()
                ItemsGroup_serializer = ItemsGroupSerializer(ItemsGroup_data, many=True)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': ItemsGroup_serializer.data})
        except Exception as e:
            raise Exception(e)
            print(e)

    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                ItemsGroup_data = JSONParser().parse(request)
                ItemsGroup_serializer = ItemsGroupSerializer(data=ItemsGroup_data)
            if ItemsGroup_serializer.is_valid():
                ItemsGroup_serializer.save()
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Roles Save Successfully','Data' :''})
            else:
                transaction.set_rollback(True)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': ItemsGroup_serializer.errors,'Data' : ''})
        except Exception as e:
            raise Exception(e)
    

class ItemsGroupViewSecond(CreateAPIView):

    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request, id=0):
        try:
            with transaction.atomic():
                ItemsGroup_data = M_Roles.objects.get(ID=id)
                ItemsGroup_serializer = ItemsGroupSerializer(ItemsGroup_data)
                return JsonResponse({'StatusCode': 200, 'Status': True,'Message': '', 'Data': ItemsGroup_serializer.data})
        except Exception as e:
            raise Exception(e)

    # @transaction.atomic()
    # def put(self, request, id=0):
    #     try:
    #         with transaction.atomic():
    #             M_Rolesdata = JSONParser().parse(request)
    #             M_RolesdataByID = M_Roles.objects.get(ID=id)
    #             M_Roles_Serializer = M_RolesSerializer(
    #                 M_RolesdataByID, data=M_Rolesdata)
    #             if M_Roles_Serializer.is_valid():
    #                 M_Roles_Serializer.save()
    #                 return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Roles Updated Successfully','Data' : ''})
    #             else:
    #                 transaction.set_rollback(True)
    #                 return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': M_Roles_Serializer.errors,'Data' : ''})
    #     except Exception as e:
    #         raise Exception(e)

    # @transaction.atomic()
    # def delete(self, request, id=0):
    #     try:
    #         with transaction.atomic():
    #             M_Rolesdata = M_Roles.objects.get(ID=id)
    #             M_Rolesdata.delete()
    #             return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Roles Deleted Successfully','Data':''})
    #     except Exception as e:
    #         raise Exception(e)
