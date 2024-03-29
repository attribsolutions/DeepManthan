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
                Settings_data = SettingsSerializerSecond(query, many=True).data
                SettingsList = list()

                if Settings_data:
                    a=Settings_data[0]
                    if Settings_data[0]['SettingDetails'] :
                        for Setting_Info in Settings_data[0]['SettingDetails'] : 
                            
                            if Setting_Info['IsDeleted'] == False:
                                SettingsList.append({
                                    "id": a['id'],
                                    "SystemSetting": a['SystemSetting'],
                                    "Description": a['Description'],
                                    "IsActive": a['IsActive'],
                                    "IsPartyRelatedSetting": a['IsPartyRelatedSetting'],
                                    "DefaultValue": a['DefaultValue'],
                                    "Value": Setting_Info.get('Value'),
                                    "IsDeleted": Setting_Info.get('IsDeleted'),
                                    "CreatedBy": Setting_Info.get('CreatedBy'),
                                    "CreatedOn": Setting_Info.get('CreatedOn'),
                                    "UpdatedBy": Setting_Info.get('UpdatedBy'),
                                    "UpdatedOn": Setting_Info.get('UpdatedOn'),
                                    "Company": Setting_Info.get('Company'),
                                })

                    else:
                        SettingsList.append({
                            "id": a['id'],
                            "SystemSetting": a['SystemSetting'],
                            "Description": a['Description'],
                            "IsActive": a['IsActive'],
                            "IsPartyRelatedSetting": a['IsPartyRelatedSetting'],
                            "DefaultValue": a['DefaultValue'],
                            "Value": "",
                            "IsDeleted": "",
                            "CreatedBy": "",
                            "CreatedOn": "",
                            "UpdatedBy": '',
                            "UpdatedOn": "",
                            "Company": "",
                        })

                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': SettingsList})
                else:
                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Settings data Not available ', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': Exception(e), 'Data': []})

    # @transaction.atomic()
    # def delete(self, request, id=0):
    #     try:
    #         with transaction.atomic():
    #             Settings_data = M_Settings.objects.get(id=id)
    #             Settings_data.delete()
    #             return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Settings Data Deleted Successfully','Data':[]})
    #     except M_SubCluster.DoesNotExist:
    #         return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Settings Data Not available', 'Data': []})
    #     except IntegrityError:   
    #         return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Settings Data used in another table', 'Data': []})
        
    
    @transaction.atomic()
    def put(self, request, id=0):
        try:
            with transaction.atomic():
                Settings_Data = JSONParser().parse(request)
                
                query = M_Settings.objects.get(id=id)

                Settings_data_serializer = SettingsSerializerSecond(query, data=Settings_Data)
                if Settings_data_serializer.is_valid():
                    Settings_data_serializer.save()
                    
                    Setting_Details_Data = Settings_Data.get('SettingDetails', [])
                    
                    if Setting_Details_Data:
                        q = MC_SettingsDetails.objects.filter(SettingID=query).update(IsDeleted=1)

                    for Setting_Details in Setting_Details_Data:
                        Setting_ID = Setting_Details.get('id', None)
                        query2 = None
                        
                        if Setting_ID:
                            query2 = MC_SettingsDetails.objects.filter(id=Setting_ID, SettingID=query).first()
                        else:
                            Setting_Details['SettingID'] = query.id

                        Setting_details_serializer = MC_SettingsDetailsSerializerSecond(query2, data=Setting_Details)
                        if Setting_details_serializer.is_valid():
                            Setting_details_serializer.save()
                        else:
                            transaction.set_rollback(True)
                            return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': Setting_details_serializer.errors, 'Data': []})
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Settings Data Updated Successfully', 'Data': []})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': Settings_data_serializer.errors, 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': Exception(e), 'Data': []})





  