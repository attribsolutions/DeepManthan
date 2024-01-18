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
    Image = serializers.SerializerMethodField()
    ImageID = serializers.IntegerField()
    def get_Image(self, obj):
        if obj.Image:
            media_url = f"http://cbmfooderp.com:8000/downloadQr/{obj.ImageID}/1"  # Replace with your actual media URL prefix from settings
            return media_url
        return None
    
    
class PartiesSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model =  M_PartySettingsDetails
        fields = ['Value','Setting','Company','Party','CreatedBy','Image']
        
        
class MC_SettingsDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = MC_SettingsDetails
        fields = ['Value','IsDeleted','CreatedBy','CreatedOn','UpdatedBy','UpdatedOn','Company']

class SettingsSerializer(serializers.ModelSerializer):
    SettingDetails = MC_SettingsDetailsSerializer(write_only=True)

    class Meta:
        model = M_Settings
        fields = ['SystemSetting', 'Description', 'IsActive', 'IsPartyRelatedSetting', 'DefaultValue', 'SettingDetails']

    def create(self, validated_data):
        SettingDetailsData = validated_data.pop('SettingDetails')
        a = M_Settings.objects.create(**validated_data)
        MC_SettingsDetails.objects.create(SettingID=a, **SettingDetailsData)
        return a
