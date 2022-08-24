from django.http import JsonResponse
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, connection, transaction
from rest_framework.parsers import JSONParser
from ..Serializer.S_ProductCategory import *
from ..models import *


class ProductCategoryView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request):
        try:
            with transaction.atomic():
                query = M_ProductCategory.objects.raw('''SELECT m_productcategory.id,m_productcategory.Name,m_productcategorytype.Name ProductCategoryTypeName FROM m_productcategory
JOIN m_productcategorytype ON m_productcategorytype.id=m_productcategory.ProductCategoryType_id''')
                if not query:
                    return JsonResponse({'StatusCode': 204, 'Status': True,'Message': 'Product Category Not available', 'Data': []})
                else:    
                    ProductCategory_Serializer = ProductCategorySerializer2(query, many=True).data
                    return JsonResponse({'StatusCode': 200, 'Status': True,'Message': '','Data': ProductCategory_Serializer})       
        except Exception  :
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  'Exception', 'Data':[]})


    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                ProductCategory_data = JSONParser().parse(request)
                ProductCategory_Serializer = ProductCategorySerializer(data=ProductCategory_data)
                if ProductCategory_Serializer.is_valid():
                    ProductCategory_Serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Product Category Save Successfully', 'Data':[]})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message':  ProductCategory_Serializer.errors, 'Data':[]})
        except Exception  :
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  'Exception', 'Data':[]})
            

class ProductCategoryViewSecond(CreateAPIView):

    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication
    
    def get(self, request, id=0 ):
        try:
            with transaction.atomic():
                query = M_ProductCategory.objects.raw('''SELECT m_productcategory.id,m_productcategory.Name,m_productcategorytype.Name ProductCategoryTypeName FROM m_productcategory
JOIN m_productcategorytype ON m_productcategorytype.id=m_productcategory.ProductCategoryType_id
WHERE m_productcategory.id = %s''',[id])
                if not query:
                    return JsonResponse({'StatusCode': 204, 'Status': True,'Message': 'Product Category Not available', 'Data': []})
                else:    
                    ProductCategory_Serializer = ProductCategorySerializer2(query, many=True).data
                    return JsonResponse({'StatusCode': 200, 'Status': True,'Message': '','Data': ProductCategory_Serializer[0]})   
        except Exception :
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  'Exception', 'Data': []})
            

    @transaction.atomic()
    def put(self, request, id=0):
        try:
            with transaction.atomic():
                ProductCategorydata = JSONParser().parse(request)
                ProductCategorydataByID = M_ProductCategory.objects.get(id=id)
                ProductCategorydata_Serializer = ProductCategorySerializer(
                    ProductCategorydataByID, data=ProductCategorydata)
                if ProductCategorydata_Serializer.is_valid():
                    ProductCategorydata_Serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Product Category Updated Successfully', 'Data':[]})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': ProductCategorydata_Serializer.errors, 'Data':[]})
        except Exception  :
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  'Exception', 'Data':[]})
        

    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                ProductCategorydata = M_ProductCategory.objects.get(id=id)
                ProductCategorydata.delete()
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Product Category Deleted Successfully', 'Data':[]})
        except M_ProductCategory.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Product Category Not available', 'Data': []})
        except IntegrityError:   
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Product Category used in another table', 'Data': []})   


class GetCategoryByCategoryTypeID(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request, id=0):
        try:
            with transaction.atomic():
                Category_data = M_ProductCategory.objects.filter(ProductCategoryType=id)
                if Category_data.exists():
                    Category_serializer = ProductCategorySerializer(Category_data, many=True)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': Category_serializer.data})
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Category Not available ', 'Data': []})
        except Exception :
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  'Exception Found', 'Data':[]})  