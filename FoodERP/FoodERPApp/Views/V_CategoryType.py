from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
# from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, transaction
from rest_framework.parsers import JSONParser
from ..Serializer.S_CategoryType import *
from ..models import *

class CategoryTypeView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request):
        try:
            with transaction.atomic():
                CategoryType_data = M_CategoryType.objects.all()
                if CategoryType_data.exists():
                    CategoryType_serializer = CategoryTypeSerializer(CategoryType_data, many=True)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': CategoryType_serializer.data})
                return JsonResponse({'StatusCode': 204, 'Status': True,'Message':'Category Type Not available', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})

    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                CategoryType_data = JSONParser().parse(request)
                CategoryType_serializer = CategoryTypeSerializer(data=CategoryType_data)
            if CategoryType_serializer.is_valid():
                CategoryType_serializer.save()
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Category Type Save Successfully', 'Data' :[]})
            else:
                transaction.set_rollback(True)
                return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': CategoryType_serializer.errors, 'Data' : []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})


class CategoryTypeViewSecond(CreateAPIView):

    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request, id=0):
        try:
            with transaction.atomic():
                CategoryTypedata = M_CategoryType.objects.get(id=id)
                CategoryType_serializer = CategoryTypeSerializer(CategoryTypedata)
                return JsonResponse({'StatusCode': 200, 'Status': True,'Message': '', 'Data': CategoryType_serializer.data})
        except  M_CategoryType.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'Category Type Not available', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})

    @transaction.atomic()
    def put(self, request, id=0):
        try:
            with transaction.atomic():
                CategoryTypedata = JSONParser().parse(request)
                CategoryTypedatadataByID = M_CategoryType.objects.get(id=id)
                CategoryType_serializer = CategoryTypeSerializer(
                    CategoryTypedatadataByID, data=CategoryTypedata)
                if CategoryType_serializer.is_valid():
                    CategoryType_serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Category Type Updated Successfully','Data' :[]})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': CategoryType_serializer.errors, 'Data' :[]})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})

    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                CategoryType_data = M_CategoryType.objects.get(id=id)
                CategoryType_data.delete()
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Category Type Deleted Successfully','Data':[]})
        except M_CategoryType.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Category Type Not available', 'Data': []})
        except IntegrityError:   
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Category Type used in another table', 'Data': []})