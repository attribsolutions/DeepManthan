from django.http import JsonResponse
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import connection, transaction
from rest_framework.parsers import JSONParser

from  ..Serializer.S_Items import M_ItemsSerializer
from ..models import *

 
class M_ItemsView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication
    
    @transaction.atomic()
    def get(self, request ):
        try:
            with transaction.atomic():
                M_Itemsdata = M_Items.objects.all()
                if M_Itemsdata.exists():
                    M_Items_Serializer = M_ItemsSerializer(
                    M_Itemsdata, many=True)
                    return JsonResponse({'StatusCode': 200, 'Status': True,'Message': '','Data': M_Items_Serializer.data})
                return JsonResponse({'StatusCode': 200, 'Status': True,'Message':  'Records Not available', 'Data': []]})    
        except Exception as e:
            raise Exception(e)
            
            print(e)


    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                M_Itemsdata = JSONParser().parse(request)
                M_Items_Serializer = M_ItemsSerializer(data=M_Itemsdata)
                if M_Items_Serializer.is_valid():
                    M_Items_Serializer.save()
                   
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'M_Items Save Successfully','Data' :''})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': M_Items_Serializer.errors,'Data': ''})
        except Exception as e:
            raise Exception(e)
            print(e)        
 

class M_ItemsViewSecond(CreateAPIView):

    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request, id=0):
        try:
            with transaction.atomic():
                M_Itemsdata = M_Items.objects.get(ID=id)
                M_Items_Serializer = M_ItemsSerializer(M_Itemsdata)
                return JsonResponse({'StatusCode': 200, 'Status': True,'Message': '', 'Data': M_Items_Serializer.data})
        except Exception as e:
            raise Exception(e)

    @transaction.atomic()
    def put(self, request, id=0):
        try:
            with transaction.atomic():
                M_Itemsdata = JSONParser().parse(request)
                M_ItemsdataByID = M_Items.objects.get(ID=id)
                M_Items_Serializer = M_ItemsSerializer(
                    M_ItemsdataByID, data=M_Itemsdata)
                if M_Items_Serializer.is_valid():
                    M_Items_Serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'M_Items Updated Successfully','Data' : ''})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': M_Items_Serializer.errors,'Data' : ''})
        except Exception as e:
            raise Exception(e)

    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                M_Itemsdata = M_Items.objects.get(ID=id)
                M_Itemsdata.delete()
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'M_Items Deleted Successfully','Data':''})
        except Exception as e:
            raise Exception(e)