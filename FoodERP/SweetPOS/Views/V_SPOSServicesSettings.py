
from ..models import *
from ..Serializer.S_SweetPosRoleAccess import *
from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from SweetPOS.Views.SweetPOSCommonFunction import BasicAuthenticationfunction
from FoodERPApp.Views.V_CommFunction import create_transaction_logNew
from FoodERPApp.models import *
from ..Serializer.S_SPOSServicesSettings import *
from rest_framework.authentication import BasicAuthentication
from rest_framework.parsers import JSONParser 
from SweetPOS.models import M_ServiceSettings


class SweetPosServiceSettingsImportView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = [BasicAuthentication]

    @transaction.atomic()
    def get(self, request,id=0):
        try:
           
            with transaction.atomic():                
                user=BasicAuthenticationfunction(request)                    
            if user is not None:
                ServiceSettingsData = M_ServiceSettings.objects.raw('''Select 1 as id, Party PartyID,GeneralMaster.Name SettingName,ServiceSettingsID ,Flag,Value,Access 
                                                                       from M_ServiceSettings
                                                                       JOIN FoodERP.M_GeneralMaster GeneralMaster ON GeneralMaster.id=ServiceSettingsID  
                                                                       where Party=%s''',[id])      
                
                ServicesSettings_serializer = SPOSServicesSettingstSerializer(ServiceSettingsData, many=True).data
                
                log_entry = create_transaction_logNew(request, ServicesSettings_serializer,0,'',347,0)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':'','Data': ServicesSettings_serializer})
        except  M_SweetPOSRoleAccess.DoesNotExist:
            log_entry = create_transaction_logNew(request, 0,0,'GETSweetPOSServiceSettingDetails'+'Service Settings Not available',347,0)
            return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'Service Settings Not available', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, 0,0,'GETSweetPOSServiceSettingDetails:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data':[]})
    
    
    def patch(self, request,id=0):
        ServiceSettings_Data = JSONParser().parse(request)
        
        ServiceSettingsID=ServiceSettings_Data['ServiceSettingsID']        
        try:
            with transaction.atomic():
                SettingID = M_ServiceSettings.objects.get(Party=id,ServiceSettingsID=ServiceSettingsID)      
                        
                ServiceSetting_Serializer = SPOSServicesSettingstSerializer1(
                    SettingID, data=ServiceSettings_Data, partial=True)  
                if ServiceSetting_Serializer.is_valid():                   
                    
                    ServiceSetting_Serializer.save()
                    log_entry = create_transaction_logNew(request, ServiceSettings_Data, 0, '', 413, 0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Service Settings Updated Successfully','Data' :[]})
                else:
                    log_entry = create_transaction_logNew(request, ServiceSettings_Data, 0, 'Service Settings Update:'+str(ServiceSetting_Serializer.errors), 412, 0)
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': str(ServiceSetting_Serializer.errors), 'Data' :[]})
        except Exception as e:
            log_entry = create_transaction_logNew(request, ServiceSettings_Data, 0, 'Service Settings Update:'+str(e), 33, 0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data':[]})  
        