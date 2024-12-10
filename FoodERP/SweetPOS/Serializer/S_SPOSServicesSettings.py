
from SweetPOS.models import *
from rest_framework import serializers



class SPOSServicesSettingstSerializer(serializers.Serializer):
    
    SettingName=serializers.CharField(max_length=500)
    ServiceSettingsID=serializers.IntegerField()
    PartyID=serializers.IntegerField()
    Flag = serializers.BooleanField()
    Value=serializers.CharField(max_length=100)
    Access=serializers.BooleanField()
    
class SPOSServicesSettingstSerializer1(serializers.ModelSerializer):
    class Meta:
        model = M_ServiceSettings
        fields = ['Flag', 'Value', 'Access']        
    