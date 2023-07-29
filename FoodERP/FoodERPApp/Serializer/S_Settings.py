from ..models import *
from rest_framework import serializers

              
class MasterSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model =  M_Settings
        fields = '__all__'
        
class PartiesSettingsDetailsListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    SystemSetting = serializers.CharField(max_length=500)
    Description = serializers.CharField(max_length=500)
    CompanyValue = serializers.CharField(max_length=500)
    DefaultValue = serializers.CharField(max_length=500)
    PartyValue = serializers.CharField(max_length=500)
    IsPartyRelatedSetting=serializers.IntegerField()
    Value  = serializers.CharField(max_length=500)
    
class PartiesSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model =  M_PartySettingsDetails
        fields = ['Value','Setting','Company','Party','CreatedBy']
        