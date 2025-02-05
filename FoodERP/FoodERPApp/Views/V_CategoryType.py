from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
# from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, transaction
from rest_framework.parsers import JSONParser
from ..Serializer.S_CategoryType import *
from ..models import *
from ..Views.V_CommFunction import *

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
                    log_entry = create_transaction_logNew(request, CategoryType_serializer,0,'',300,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': CategoryType_serializer.data})
                log_entry = create_transaction_logNew(request, CategoryType_serializer,0,'CategoryType Not available',300,0)
                return JsonResponse({'StatusCode': 204, 'Status': True,'Message':'Category Type Not available', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, 0, 0,'GETAllCategoryTypes:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data':[]})

    @transaction.atomic()
    def post(self, request):
        CategoryType_data = JSONParser().parse(request)
        try:
            with transaction.atomic():
                CategoryType_serializer = CategoryTypeSerializer(data=CategoryType_data)
            if CategoryType_serializer.is_valid():
                CategoryType_serializer.save()
                log_entry = create_transaction_logNew(request, CategoryType_data,0,'',301,0)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'CategoryType Save Successfully', 'Data' :[]})
            else:
                log_entry = create_transaction_logNew(request, CategoryType_data,0,'CategoryTypeSave:'+str(CategoryType_serializer.errors),34,0)
                transaction.set_rollback(True)
                return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': CategoryType_serializer.errors, 'Data' : []})
        except Exception as e:
            log_entry = create_transaction_logNew(request,CategoryType_data, 0,'CategoryTypeSave:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data':[]})


class CategoryTypeViewSecond(CreateAPIView):

    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request, id=0):
        try:
            with transaction.atomic():
                CategoryTypedata = M_CategoryType.objects.get(id=id)
                CategoryType_serializer = CategoryTypeSerializer(CategoryTypedata)
                log_entry = create_transaction_logNew(request, CategoryType_serializer,0,'CategoryID:'+str(id),302,0)
                return JsonResponse({'StatusCode': 200, 'Status': True,'Message': '', 'Data': CategoryType_serializer.data})
        except  M_CategoryType.DoesNotExist:
            log_entry = create_transaction_logNew(request,'',0,'CategoryType Does Not Exist',302,0)
            return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'Category Type Not available', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, 0, 0,'GETSingleCategoryType:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data':[]})

    @transaction.atomic()
    def put(self, request, id=0):
        CategoryTypedata = JSONParser().parse(request)
        try:
            with transaction.atomic():
                CategoryTypedatadataByID = M_CategoryType.objects.get(id=id)
                CategoryType_serializer = CategoryTypeSerializer(
                    CategoryTypedatadataByID, data=CategoryTypedata)
                if CategoryType_serializer.is_valid():
                    CategoryType_serializer.save()
                    log_entry = create_transaction_logNew(request, CategoryTypedata,0,'CategoryType Updated',303,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Category Type Updated Successfully','Data' :[]})
                else:
                    log_entry = create_transaction_logNew(request, CategoryTypedata,0,'CategoryTypeEdit:'+str(CategoryType_serializer.errors),34,0)
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': CategoryType_serializer.errors, 'Data' :[]})
        except Exception as e:
            log_entry = create_transaction_logNew(request,CategoryTypedata,0,'CategoryTypeEdit:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data':[]})

    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                CategoryType_data = M_CategoryType.objects.get(id=id)
                CategoryType_data.delete()
                log_entry = create_transaction_logNew(request, 0,0,'CategoryTypeID:'+str(id),304,0)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'CategoryType Deleted Successfully','Data':[]})
        except M_CategoryType.DoesNotExist:
            log_entry = create_transaction_logNew(request, 0,0,'CategoryType Does Not Exist',304,0)
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Category Type Not available', 'Data': []})
        except IntegrityError:  
            log_entry = create_transaction_logNew(request, 0,0,'CategoryType used in another table',8,0)  
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Category Type used in another table', 'Data': []})