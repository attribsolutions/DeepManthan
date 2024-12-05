import base64
from ..models import *
from ..Serializer.S_SweetPosRoleAccess import *
from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
import pdb
from FoodERPApp.Views.V_CommFunction import create_transaction_logNew
from FoodERPApp.models import *
from ..Serializer.S_SPOSServicesSettings import *


class SweetPosServiceSettingsImportView(CreateAPIView):
    permission_classes = (IsAuthenticated,)   

    @transaction.atomic()
    def get(self, request,id=0):
        try:
            with transaction.atomic():
                ServiceSettingsData = M_ServiceSettings.objects.raw('''Select 1 as id, Party PartyID,GeneralMaster.Name SettingName,ServiceSettingsID ,Flag,Value,Access 
                                                                       from M_ServiceSettings 
                                                                       JOIN FoodERP.M_GeneralMaster GeneralMaster ON GeneralMaster.id=ServiceSettingsID  
                                                                       where Party=%s''',[id])   

                # print(ServiceSettingsData.query)                    
                
                ServicesSettings_serializer = SPOSServicesSettingstSerializer(ServiceSettingsData, many=True).data
                
                log_entry = create_transaction_logNew(request, ServicesSettings_serializer,0,'',347,0)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':'','Data': ServicesSettings_serializer})
        except  M_SweetPOSRoleAccess.DoesNotExist:
            log_entry = create_transaction_logNew(request, 0,0,'GETSweetPOSRoleAccessDetails'+'RoleAccess Not available',347,0)
            return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'RoleAccess Not available', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, 0,0,'GETSweetPOSRoleAccessDetails:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data':[]})
