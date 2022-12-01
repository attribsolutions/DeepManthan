
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, connection, transaction
from rest_framework.parsers import JSONParser

from ..Serializer.S_Bom import *

from ..models import *

'''BOM ---   Bill Of Material'''
class M_BOMsView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication
    
    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                Bomsdata = JSONParser().parse(request)
                Boms_Serializer = M_BOMSerializer(data=Bomsdata)
                if Boms_Serializer.is_valid():
                    Boms_Serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Bill Of Material Save Successfully', 'Data':[]})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': Boms_Serializer.errors, 'Data': []})
        except Exception  :
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': 'Execution Error' , 'Data':[]})       

class M_BOMsViewSecond(RetrieveAPIView):
    
    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request, id=0):
        try:
            with transaction.atomic():
                Bomsdata = M_BillOfMaterial.objects.get(id=id)
                Boms_Serializer = M_BOMSerializerSecond(Bomsdata)
                return JsonResponse({'StatusCode': 200, 'Status': True,'Message': '','Data': Boms_Serializer.data})
        except H_Modules.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Bill Of Material Not available', 'Data': []})
           

    @transaction.atomic()
    def put(self, request, id=0):
        try:
            with transaction.atomic():
                Bomsdata = JSONParser().parse(request)
                BomsdataByID = M_BillOfMaterial.objects.get(id=id)
                Boms_Serializer = M_BOMSerializerSecond(BomsdataByID, data=Bomsdata)
                if Boms_Serializer.is_valid():
                    Boms_Serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Bill Of Material Updated Successfully','Data':[]})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': Boms_Serializer.errors,'Data' :[]})
        except Exception :
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': 'Execution Error', 'Data':[]})            

    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                Bomsdata = M_BillOfMaterial.objects.get(id=id)
                Bomsdata.delete()
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Bill Of Material  Deleted Successfully', 'Data':[]})
        except H_Modules.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Bill Of Material Not available', 'Data': []})    
        except IntegrityError:   
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Bill Of Material used in another table', 'Data': []})    