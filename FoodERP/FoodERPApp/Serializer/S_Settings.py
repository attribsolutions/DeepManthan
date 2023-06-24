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
    IsActive = serializers.BooleanField()
    Value = serializers.CharField(max_length=500)
    Party_id =serializers.IntegerField()
    
class PartiesSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model =  M_PartySettingsDetails
        fields = ['Value','Setting','Company','Party','CreatedBy']
        