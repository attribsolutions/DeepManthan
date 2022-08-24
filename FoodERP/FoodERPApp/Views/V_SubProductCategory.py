from django.http import JsonResponse
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, connection, transaction
from rest_framework.parsers import JSONParser
from ..Serializer.S_SubProductCategory import *
from ..models import *


class SubProductCategoryView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request):
        try:
            with transaction.atomic():
                query = M_ProductSubCategory.objects.raw('''SELECT m_productsubcategory.id,m_productsubcategory.Name,m_productcategory.Name ProductCategoryName FROM m_productsubcategory
JOIN m_productcategory ON m_productcategory.id=m_productsubcategory.ProductCategory_id''')
                if not query:
                    return JsonResponse({'StatusCode': 204, 'Status': True,'Message': ' SubCategory Not available', 'Data': []})
                else:    
                    SubProductCategory_Serializer = SubProductCategorySerializer2(query, many=True).data
                    return JsonResponse({'StatusCode': 200, 'Status': True,'Message': '','Data': SubProductCategory_Serializer})       
        except Exception  :
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  'Exception', 'Data':[]})


    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                SubProductCategory_data = JSONParser().parse(request)
                SubProductCategory_Serializer = SubProductCategorySerializer(data=SubProductCategory_data)
                if SubProductCategory_Serializer.is_valid():
                    SubProductCategory_Serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': ' SubCategory Save Successfully', 'Data':[]})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message':  SubProductCategory_Serializer.errors, 'Data':[]})
        except Exception  :
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  'Exception', 'Data':[]})
            

class SubProductCategoryViewSecond(CreateAPIView):

    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication
    
    def get(self, request, id=0 ):
        try:
            with transaction.atomic():
                query = M_ProductSubCategory.objects.raw('''SELECT m_productsubcategory.id,m_productsubcategory.Name,m_productcategory.Name ProductCategoryName FROM m_productsubcategory
JOIN m_productcategory ON m_productcategory.id=m_productsubcategory.ProductCategory_id
WHERE m_productsubcategory.id = %s''',[id])
                if not query:
                    return JsonResponse({'StatusCode': 204, 'Status': True,'Message': ' SubCategory Not available', 'Data': []})
                else:    
                    SubProductCategory_Serializer = SubProductCategorySerializer2(query, many=True).data
                    return JsonResponse({'StatusCode': 200, 'Status': True,'Message': '','Data': SubProductCategory_Serializer[0]})   
        except Exception :
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  'Exception', 'Data': []})
            

    @transaction.atomic()
    def put(self, request, id=0):
        try:
            with transaction.atomic():
                SubProductCategorydata = JSONParser().parse(request)
                SubProductCategorydataByID = M_ProductSubCategory.objects.get(id=id)
                SubProductCategorydata_Serializer = SubProductCategorySerializer(
                    SubProductCategorydataByID, data=SubProductCategorydata)
                if SubProductCategorydata_Serializer.is_valid():
                    SubProductCategorydata_Serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': ' SubCategory Updated Successfully', 'Data':[]})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': SubProductCategorydata_Serializer.errors, 'Data':[]})
        except Exception  :
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  'Exception', 'Data':[]})
        

    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                SubProductCategorydata = M_ProductSubCategory.objects.get(id=id)
                SubProductCategorydata.delete()
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': ' SubCategory Deleted Successfully', 'Data':[]})
        except M_ProductSubCategory.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':' SubCategory Not available', 'Data': []})
        except IntegrityError:   
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':' SubCategory used in another table', 'Data': []})   


class GetSubCategoryByCategoryID(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request, id=0):
        try:
            with transaction.atomic():
                SubCategory_data = M_ProductSubCategory.objects.filter(ProductCategory=id)
                if SubCategory_data.exists():
                    SubCategory_serializer = SubProductCategorySerializer(SubCategory_data, many=True)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': SubCategory_serializer.data})
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'SubCategory Not available ', 'Data': []})
        except Exception :
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  'Exception Found', 'Data':[]})  