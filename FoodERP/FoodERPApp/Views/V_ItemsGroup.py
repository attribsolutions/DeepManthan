
from django.http import JsonResponse
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import connection, transaction
from rest_framework.parsers import JSONParser
from ..Serializer.S_ItemsGroup import *
from ..models import *

class M_ItemsGroupView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication
    
    @transaction.atomic()
    def get(self, request ):
        try:
            with transaction.atomic():
                ItemsGroupdata = M_ItemsGroup.objects.all()
                ItemsGroup_Serializer = M_ItemsGroupSerializer(ItemsGroupdata, many=True)
                return JsonResponse({'StatusCode': 200, 'Status': True,'Message': '','Data': ItemsGroup_Serializer.data })  
        except Exception as e:
            raise Exception(e)
            
            print(e)

    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                ItemsGroupdata = JSONParser().parse(request)
                ItemsGroup_Serializer = M_ItemsGroupSerializer(data=ItemsGroupdata)
                if ItemsGroup_Serializer.is_valid():
                    ItemsGroup_Serializer.save()
                   
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '  Data Save Successfully','Data' :''})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': ItemsGroup_Serializer.errors,'Data': ''})
        except Exception as e:
            raise Exception(e)
            print(e)


class M_ItemsGroupViewSecond(RetrieveAPIView):
    
    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request, id=0):
        try:
            with transaction.atomic():
                ItemsGroupdata = M_ItemsGroup.objects.filter(ID=id)
                if ItemsGroupdata.exists():
                    M_Employees_Serializer = M_ItemsGroupSerializer(ItemsGroupdata, many=True)
                    return JsonResponse({'StatusCode': 200, 'Status': True,'Message': '','Data': M_Employees_Serializer.data})
                return JsonResponse({'StatusCode': 200, 'Status': True,'Message':  'Records Not available', 'Data': ''})    
        except Exception as e:
            raise Exception(e)
            
            print(e)
        
    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                ItemsGroupdata = M_ItemsGroup.objects.get(ID=id)
                ItemsGroupdata.delete()
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Data Deleted Successfully','Data' : ''})
        except Exception as e:
            raise Exception(e)
            print(e)

    @transaction.atomic()
    def put(self, request, id=0):
        try:
            with transaction.atomic():
                ItemsGroupdata = JSONParser().parse(request)
                ItemsGroupdataaByID = M_ItemsGroup.objects.get(ID=id)
               
                ItemsGroup_Serializer = M_ItemsGroupSerializer(ItemsGroupdataaByID, data=ItemsGroupdata)
                if ItemsGroup_Serializer.is_valid():
                    ItemsGroup_Serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Updated Successfully','Data':''})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': ItemsGroup_Serializer.errors,'Data' :''})
                
        except Exception as e:
            raise Exception(e)
            print(e)            
