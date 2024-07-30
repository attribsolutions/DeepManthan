from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
# from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, transaction
from rest_framework.parsers import JSONParser
from ..Serializer.S_Category import *
from ..models import *
from ..Views.V_CommFunction import *

class CategoryView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request,id=0):
        try:
            with transaction.atomic():
                Categoryquery = M_Category.objects.all()
                if Categoryquery.exists():
                    # return JsonResponse({'query':  str(Itemsquery.query)})
                    Categorydata = CategorySerializerSecond(Categoryquery, many=True).data
                    CategoryList=list()
                    for a in Categorydata:
                        CategoryList.append({
                            "id": a['id'],
                            "Name": a['Name'],
                            "CategoryType": a['CategoryType']['id'],
                            "CategoryTypeName": a['CategoryType']['Name'],
                            "CreatedBy": a['CreatedBy'],
                            "CreatedOn": a['CreatedOn'],
                            "UpdatedBy": a['UpdatedBy'],
                            "UpdatedOn": a['UpdatedOn']
                        })
                        log_entry = create_transaction_logNew(request, Categorydata,0,'',294,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': CategoryList})
                log_entry = create_transaction_logNew(request, Categorydata,0,'Category Not available',294,0)
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Category Not available ', 'Data': []})
        except M_Category.DoesNotExist:
            log_entry = create_transaction_logNew(request,0,0,'Category Does Not Exist',294,0)
            return JsonResponse({'StatusCode': 204, 'Status': True,'Message': 'Category Not available', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, 0, 0,'GETAllCategories:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': str(e), 'Data':[]})

    @transaction.atomic()
    def post(self, request):
        Category_data = JSONParser().parse(request)
        try:
            with transaction.atomic():
                Category_Serializer = CategorySerializer(data=Category_data)
                if Category_Serializer.is_valid():
                    Category_Serializer.save()
                    log_entry = create_transaction_logNew(request, Category_data,0,'',295,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Category Save Successfully', 'Data':[]})
                else:
                    log_entry = create_transaction_logNew(request, Category_data,0,'CategorySave:'+str(Category_Serializer.errors),34,0)
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message':  Category_Serializer.errors, 'Data':[]})
        except Exception as e:
            log_entry = create_transaction_logNew(request, Category_data, 0,'CategorySave:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data':[]})
            

class CategoryViewSecond(CreateAPIView):

    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication
    
    @transaction.atomic()
    def get(self, request,id=0):
        try:
            with transaction.atomic():
                Categoryquery = M_Category.objects.filter(id=id)
                if Categoryquery.exists():
                    # return JsonResponse({'query':  str(Itemsquery.query)})
                    Categorydata = CategorySerializerSecond(Categoryquery, many=True).data
                    CategoryList=list()
                    for a in Categorydata:
                        CategoryList.append({
                            "id": a['id'],
                            "Name": a['Name'],
                            "CategoryType": a['CategoryType']['id'],
                            "CategoryTypeName": a['CategoryType']['Name'],
                            "CreatedBy": a['CreatedBy'],
                            "CreatedOn": a['CreatedOn'],
                            "UpdatedBy": a['UpdatedBy'],
                            "UpdatedOn": a['UpdatedOn']
                        })
                        log_entry = create_transaction_logNew(request, Categorydata,0,'CategoryID:'+str(id),296,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': CategoryList[0]})
                log_entry = create_transaction_logNew(request, Categorydata,0,'Category Not available',296,0)
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Category Not available ', 'Data': []})
        except M_Category.DoesNotExist:
            log_entry = create_transaction_logNew(request,0,0,'Category Does Not Exist',296,0)
            return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'Category Not available', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, 0, 0,'GETSingleCategory:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data':[]})


    @transaction.atomic()
    def put(self, request, id=0):
        Categorydata = JSONParser().parse(request)
        try:
            with transaction.atomic():
                CategorydataByID = M_Category.objects.get(id=id)
                Categorydata_Serializer = CategorySerializer(
                    CategorydataByID, data=Categorydata)
                if Categorydata_Serializer.is_valid():
                    Categorydata_Serializer.save()
                    log_entry = create_transaction_logNew(request, Categorydata,0,'CategoryID:'+str(id),297,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Category Updated Successfully', 'Data':[]})
                else:
                    log_entry = create_transaction_logNew(request, Categorydata,0,'CategoryEdit:'+str(Categorydata_Serializer.errors),34,0)
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': Categorydata_Serializer.errors, 'Data':[]})
        except Exception as e:
            log_entry = create_transaction_logNew(request, Categorydata,0,'CategoryEdit:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data':[]})
        

    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                Categorydata = M_Category.objects.get(id=id)
                Categorydata.delete()
                log_entry = create_transaction_logNew(request, 0,0,'CategoryID:'+str(id),298,0)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Category Deleted Successfully', 'Data':[]})
        except M_Category.DoesNotExist:
            log_entry = create_transaction_logNew(request, 0,0,'Category Not available',298,0)
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Category Not available', 'Data': []})
        except IntegrityError:
            log_entry = create_transaction_logNew(request, 0,0,'Category used in another table',8,0)   
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Category used in another table', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, 0,0,'CategoryDeleted:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data':[]})   


class GetCategoryByCategoryTypeID(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request,id=0):
        try:
            with transaction.atomic():
                Categoryquery = M_Category.objects.filter(CategoryType_id=id)
                if Categoryquery.exists():
                    # return JsonResponse({'query':  str(Itemsquery.query)})
                    Categorydata = CategorySerializerSecond(Categoryquery, many=True).data
                    CategoryList=list()
                    for a in Categorydata:
                        CategoryList.append({
                            "id": a['id'],
                            "Name": a['Name'],
                            "CategoryType": a['CategoryType']['id'],
                            "CategoryTypeName": a['CategoryType']['Name'],
                            "CreatedBy": a['CreatedBy'],
                            "CreatedOn": a['CreatedOn'],
                            "UpdatedBy": a['UpdatedBy'],
                            "UpdatedOn": a['UpdatedOn']
                        })
                        log_entry = create_transaction_logNew(request, Categorydata,0,'',299,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': CategoryList})
                log_entry = create_transaction_logNew(request, Categorydata,0,'GetCategoryByCategoryTypeID Not available',299,0)
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Category Not available ', 'Data': []})
        except M_Category.DoesNotExist:
            log_entry = create_transaction_logNew(request,'',0,'GetCategoryByCategoryTypeID Does Not Exist',299,0)
            return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'Category Not available', 'Data': []})