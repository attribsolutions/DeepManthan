from django.http import JsonResponse
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, connection, transaction
from rest_framework.parsers import JSONParser
from ..Serializer.S_ProductCategoryTypes import M_ProductCategoryTypeSerializer
from ..models import *


class M_ProductCategoryTypeView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request):
        try:
            with transaction.atomic():
                M_ProductCategoryType_data = M_ProductCategoryType.objects.all()
                if M_ProductCategoryType_data.exists():
                    M_ProductCategoryType_data_serializer = M_ProductCategoryTypeSerializer(M_ProductCategoryType_data, many=True)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': M_ProductCategoryType_data_serializer.data})
                return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'Product Category Type Not available', 'Data': []})
        except Exception :
            raise JsonResponse({'StatusCode': 400, 'Status': True, 'Message': 'Execution Error', 'Data':[]})

    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                M_ProductCategoryType_data = JSONParser().parse(request)
                M_ProductCategoryType_serializer = M_ProductCategoryTypeSerializer(data=M_ProductCategoryType_data)
            if M_ProductCategoryType_serializer.is_valid():
                M_ProductCategoryType_serializer.save()
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Product Category Type Save Successfully', 'Data' :[]})
            else:
                transaction.set_rollback(True)
                return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': M_ProductCategoryType_serializer.errors, 'Data' : []})
        except Exception :
            raise JsonResponse({'StatusCode': 400, 'Status': True, 'Message': 'Execution Error', 'Data':[]})


class M_ProductCategoryTypeViewSecond(CreateAPIView):

    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request, id=0):
        try:
            with transaction.atomic():
                M_ProductCategoryType_data = M_ProductCategoryType.objects.get(id=id)
                M_ProductCategoryType_serializer = M_ProductCategoryTypeSerializer(M_ProductCategoryType_data)
                return JsonResponse({'StatusCode': 200, 'Status': True,'Message': '', 'Data': M_ProductCategoryType_serializer.data})
        except  M_Roles.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'Product Category Type Not available', 'Data': []})
        except Exception as e:
            raise JsonResponse({'StatusCode': 400, 'Status': True, 'Message':   'Execution Error', 'Data':[]})

    @transaction.atomic()
    def put(self, request, id=0):
        try:
            with transaction.atomic():
                M_ProductCategoryType_data = JSONParser().parse(request)
                M_ProductCategoryTypedataByID = M_ProductCategoryType.objects.get(id=id)
                M_ProductCategoryType_serializer = M_ProductCategoryTypeSerializer(
                    M_ProductCategoryTypedataByID, data=M_ProductCategoryType_data)
                if M_ProductCategoryType_serializer.is_valid():
                    M_ProductCategoryType_serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Product Category Type Updated Successfully','Data' :[]})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': M_ProductCategoryType_serializer.errors, 'Data' :[]})
        except Exception as e:
            raise JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  'Executiono Error', 'Data':[]})

    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                M_ProductCategoryType_data = M_ProductCategoryType.objects.get(id=id)
                M_ProductCategoryType_data.delete()
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Product Category Type Deleted Successfully','Data':[]})
        except M_ProductCategoryType.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Product Category Type Not available', 'Data': []})
        except IntegrityError:   
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Product Category Type used in another table', 'Data': []})