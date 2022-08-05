
from django.http import JsonResponse
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, connection, transaction
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
                if ItemsGroupdata.exists():
                    ItemsGroup_Serializer = M_ItemsGroupSerializer(ItemsGroupdata, many=True)
                    return JsonResponse({'StatusCode': 200, 'Status': True,'Message': '','Data': ItemsGroup_Serializer.data })
                return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'Item Group Not available', 'Data': []})      
        except Exception :
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  'Exception Found', 'Data': []})

    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                ItemsGroupdata = JSONParser().parse(request)
                ItemsGroup_Serializer = M_ItemsGroupSerializer(data=ItemsGroupdata)
                if ItemsGroup_Serializer.is_valid():
                    ItemsGroup_Serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Item Group Save Successfully','Data' :[]})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': ItemsGroup_Serializer.errors,'Data': []})
        except Exception :
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  'Exception Found', 'Data': []})


class M_ItemsGroupViewSecond(RetrieveAPIView):
    
    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request, id=0):
        try:
            with transaction.atomic():
                ItemsGroupdata = M_ItemsGroup.objects.get(id=id)
                ItemsGroup_Serializer = M_ItemsGroupSerializer(ItemsGroupdata)
                return JsonResponse({'StatusCode': 200, 'Status': True,'Message': '','Data': ItemsGroup_Serializer.data}) 
        except M_ItemsGroup.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Record Not available', 'Data': []})
            
    @transaction.atomic()
    def put(self, request, id=0):
        try:
            with transaction.atomic():
                ItemsGroupdata = JSONParser().parse(request)
                ItemsGroupdataaByID = M_ItemsGroup.objects.get(id=id)
               
                ItemsGroup_Serializer = M_ItemsGroupSerializer(ItemsGroupdataaByID, data=ItemsGroupdata)
                if ItemsGroup_Serializer.is_valid():
                    ItemsGroup_Serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Item Group Updated Successfully','Data':[]})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': ItemsGroup_Serializer.errors,'Data' :[]})   
        except Exception :
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  'Exception Found', 'Data': []}) 

    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                ItemsGroupdata = M_ItemsGroup.objects.get(ID=id)
                ItemsGroupdata.delete()
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Item Group Deleted Successfully','Data' :[]})
        except M_ItemsGroup.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Record Not available', 'Data': []})
        except IntegrityError:   
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Item Group used in another tbale', 'Data': []})    