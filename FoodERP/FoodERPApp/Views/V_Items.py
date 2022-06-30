from genericpath import exists
from django.http import JsonResponse
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, connection, transaction
from rest_framework.parsers import JSONParser

from  ..Serializer.S_Items import *
from ..models import *

 
class M_ItemsView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication
    
    @transaction.atomic()
    def get(self, request, id=0 ):
        try:
            with transaction.atomic():
                query = M_Items.objects.raw('''SELECT p.ID,p.Name,p.BaseunitID,p.GSTPercentage,p.MRP,RP.ID ItemGroupID,RP.Name ItemGroupName,p.Rate,p.isActive,p.CreatedBy,p.CreatedOn,p.UpdatedBy,p.UpdatedOn
FROM M_Items p 
join M_ItemsGroup RP ON p.ItemGroup_id=RP.ID
Order BY RP.Sequence, p.Sequence''')
                if not query:
                    return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'Items Not available', 'Data': []})
                else:
                    M_Items_Serializer = M_ItemsSerializer02(query, many=True).data
                    return JsonResponse({'StatusCode': 200, 'Status': True,'Message': '','Data': M_Items_Serializer})   
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})
        

    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                M_Itemsdata = JSONParser().parse(request)
                M_Items_Serializer = M_ItemsSerializer01(data=M_Itemsdata)
                if M_Items_Serializer.is_valid():
                    M_Items_Serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Item Save Successfully','Data' :M_Items_Serializer.data})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': M_Items_Serializer.errors,'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})
                 
 

class M_ItemsViewSecond(CreateAPIView):

    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request, id=0 ):
        try:
            with transaction.atomic():
                query = M_Items.objects.raw('''SELECT p.ID,p.Name,p.BaseunitID,p.GSTPercentage,p.MRP,RP.ID ItemGroupID,RP.Name ItemGroupName,p.Rate,p.isActive,p.CreatedBy,p.CreatedOn,p.UpdatedBy,p.UpdatedOn
FROM M_Items p 
join M_ItemsGroup RP ON p.ItemGroup_id=RP.ID where p.id= %s''',[id])
                if not query:
                    return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'Items Not available', 'Data': []})
                else:
                    M_Items_Serializer = M_ItemsSerializer02(query, many=True).data
                    return JsonResponse({'StatusCode': 200, 'Status': True,'Message': '','Data': M_Items_Serializer})   
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})
        

    @transaction.atomic()
    def put(self, request, id=0):
        try:
            with transaction.atomic():
                M_Itemsdata = JSONParser().parse(request)
                M_ItemsdataByID = M_Items.objects.get(ID=id)
                M_Items_Serializer = M_ItemsSerializer01(
                    M_ItemsdataByID, data=M_Itemsdata)
                if M_Items_Serializer.is_valid():
                    M_Items_Serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Item Updated Successfully','Data' : []})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': M_Items_Serializer.errors,'Data' :[]})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e),'Data' :[]})

    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                M_Itemsdata = M_Items.objects.get(ID=id)
                M_Itemsdata.delete()
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Item Deleted Successfully','Data':[]})
        except M_Items.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Item Not available', 'Data': []})
        except IntegrityError:   
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Item used in another table', 'Data': []})     