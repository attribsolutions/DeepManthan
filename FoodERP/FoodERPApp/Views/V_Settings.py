from django.http import JsonResponse
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
# from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, transaction
from rest_framework.parsers import JSONParser
from ..Serializer.S_Settings import *
from ..models import *


class SettingsView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    
    @transaction.atomic()
    def post(self, request ):
        try:
            with transaction.atomic():
                Settings_data = JSONParser().parse(request)
                Settings_data_serializer = SettingsSerializer(data= Settings_data)
                if  Settings_data_serializer.is_valid():
                    Settings_data_serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Settings Save Successfully', 'Data': []})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message':  Settings_data_serializer.errors, 'Data': []})
        except Exception as e:
            raise JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})
        
      
class SystemSettingsView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    @transaction.atomic()
    def get(self, request, id=0):
        try:
            with transaction.atomic():
                query = M_Settings.objects.filter(id=id)
                print(query.query)
                Settings_data = SettingsSerializerSecond(query, many=True).data
                SettingsList=list()

                for a in Settings_data:
                    SettingsList.append({
                        "id": a['id'],
                        "SystemSetting": a['SystemSetting'],
                        "Description": a['Description'],
                        "IsActive": a['IsActive'],
                        "IsPartyRelatedSetting": a['IsPartyRelatedSetting'],
                        "DefaultValue": a['DefaultValue'],
                        "Value": a['SettingDetails'][0]['Value'],
                        "IsDeleted": a['SettingDetails'][0]['IsDeleted'],
                        "CreatedBy": a['SettingDetails'][0]['CreatedBy'],
                        "CreatedOn": a['SettingDetails'][0]['CreatedOn'],
                        "UpdatedBy": a['SettingDetails'][0]['UpdatedBy'],
                        "UpdatedOn": a['SettingDetails'][0]['UpdatedOn'],
                        "Company": a['SettingDetails'][0]['Company'],
                        
                        })

                
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': SettingsList[0]})
                
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Settings data Not available ', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': Exception(e), 'Data': []})
          
        
    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                Settings_data = M_Settings.objects.get(id=id)
                Settings_data.delete()
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Settings Data Deleted Successfully','Data':[]})
        except M_SubCluster.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Settings Data Not available', 'Data': []})
        except IntegrityError:   
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Settings Data used in another table', 'Data': []})
