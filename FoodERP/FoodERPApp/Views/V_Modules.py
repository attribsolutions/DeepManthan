from django.http import JsonResponse
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
# from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, transaction
from rest_framework.parsers import JSONParser
from ..Serializer.S_Modules import *
from ..models import *
from ..Serializer.S_Orders import *

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
                    log_entry = create_transaction_logNew(request,Modules_Serializer, 0,'',267,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True,'Message': '','Data': Modules_Serializer.data })
                log_entry = create_transaction_logNew(request,Modules_Serializer, 0,'Modules Not available',267,0)
                return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'Modules Not available', 'Data': []})    
        except Exception as e:
            log_entry = create_transaction_logNew(request,0, 0,'GETAllModules:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data':[]})
         
    @transaction.atomic()
    def post(self, request):
        Modulesdata = JSONParser().parse(request)
        try:
            with transaction.atomic():
                Modules_Serializer = H_ModulesSerializer(data=Modulesdata)
                if Modules_Serializer.is_valid():
                    Modules_Serializer.save()
                    log_entry = create_transaction_logNew(request,Modulesdata, 0,'',268,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Module Save Successfully', 'Data':[]})
                else:
                    log_entry = create_transaction_logNew(request,Modulesdata, 0,'ModuleSave:'+str(Modules_Serializer.errors),34,0)
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': Modules_Serializer.errors, 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request,Modulesdata, 0,'ModuleSave:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data':[]})       

class H_ModulesViewSecond(RetrieveAPIView):
    
    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request, id=0):
        try:
            with transaction.atomic():
                Modulesdata = H_Modules.objects.get(id=id)
                Modules_Serializer = H_ModulesSerializer(Modulesdata)
                log_entry = create_transaction_logNew(request,Modules_Serializer, 0,'',269,0)
                return JsonResponse({'StatusCode': 200, 'Status': True,'Message': '','Data': Modules_Serializer.data})
        except H_Modules.DoesNotExist:
            log_entry = create_transaction_logNew(request,0, 0,'Module Not available',269,0)
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Module Not available', 'Data': []})
           

    @transaction.atomic()
    def put(self, request, id=0):
        Modulesdata = JSONParser().parse(request)
        try:
            with transaction.atomic():
                ModulesdataByID = H_Modules.objects.get(id=id)
                Modules_Serializer = H_ModulesSerializer(ModulesdataByID, data=Modulesdata)
                if Modules_Serializer.is_valid():
                    Modules_Serializer.save()
                    log_entry = create_transaction_logNew(request,Modulesdata, 0,'',270,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Module Updated Successfully','Data':[]})
                else:
                    log_entry = create_transaction_logNew(request,Modulesdata, 0,'ModuleUpdate:'+str(Modules_Serializer.errors),34,0)
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': Modules_Serializer.errors,'Data' :[]})
        except Exception as e:
            log_entry = create_transaction_logNew(request,Modulesdata, 0,'ModuleUpdate:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data':[]})            

    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                Modulesdata = H_Modules.objects.get(id=id)
                Modulesdata.delete()
                log_entry = create_transaction_logNew(request,0, 0,'',271,0)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Module Deleted Successfully', 'Data':[]})
        except H_Modules.DoesNotExist:
            log_entry = create_transaction_logNew(request,0, 0,'Module Not available',271,0)
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Module Not available', 'Data': []})    
        except IntegrityError:   
            log_entry = create_transaction_logNew(request,0, 0,'ModuleDelete:'+'Module used in another table',8,0)
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Module used in another table', 'Data': []})    