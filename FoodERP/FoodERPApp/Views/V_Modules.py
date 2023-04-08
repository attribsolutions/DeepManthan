
from django.http import JsonResponse
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
# from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, transaction
from rest_framework.parsers import JSONParser

from ..Serializer.S_Modules import *

from ..models import *


class H_ModulesView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication
    
    @transaction.atomic()
    def get(self, request ):
        try:
            with transaction.atomic():
                Modulesdata = H_Modules.objects.all()
                if Modulesdata.exists():
                    Modules_Serializer = H_ModulesSerializer(
                    Modulesdata, many=True)
                    return JsonResponse({'StatusCode': 200, 'Status': True,'Message': '','Data': Modules_Serializer.data })
                return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'Modules Not available', 'Data': []})    
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})
         

    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                Modulesdata = JSONParser().parse(request)
                Modules_Serializer = H_ModulesSerializer(data=Modulesdata)
                if Modules_Serializer.is_valid():
                    Modules_Serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Module Save Successfully', 'Data':[]})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': Modules_Serializer.errors, 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})       

class H_ModulesViewSecond(RetrieveAPIView):
    
    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request, id=0):
        try:
            with transaction.atomic():
                Modulesdata = H_Modules.objects.get(id=id)
                Modules_Serializer = H_ModulesSerializer(Modulesdata)
                return JsonResponse({'StatusCode': 200, 'Status': True,'Message': '','Data': Modules_Serializer.data})
        except H_Modules.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Module Not available', 'Data': []})
           

    @transaction.atomic()
    def put(self, request, id=0):
        try:
            with transaction.atomic():
                Modulesdata = JSONParser().parse(request)
                ModulesdataByID = H_Modules.objects.get(id=id)
                Modules_Serializer = H_ModulesSerializer(ModulesdataByID, data=Modulesdata)
                if Modules_Serializer.is_valid():
                    Modules_Serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Module Updated Successfully','Data':[]})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': Modules_Serializer.errors,'Data' :[]})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})            

    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                Modulesdata = H_Modules.objects.get(id=id)
                Modulesdata.delete()
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Module  Deleted Successfully', 'Data':[]})
        except H_Modules.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Module Not available', 'Data': []})    
        except IntegrityError:   
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Module used in another table', 'Data': []})    