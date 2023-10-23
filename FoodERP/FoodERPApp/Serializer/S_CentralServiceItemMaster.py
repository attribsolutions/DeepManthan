from rest_framework import serializers
from ..models import *

# Post and Put Methods Serializer

class CentralServiceItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = M_CentralServiceItems
        fields = '__all__'
        
class MC_CentralServiceItemAssignSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    Name=serializers.CharField(max_length=500)
    Party_id = serializers.IntegerField()
    PartyName=serializers.CharField(max_length=500)
    
    
    
class MC_CentralServiceItemAssignSerializerSecond(serializers.ModelSerializer):
    class Meta:
        model =  MC_CentralServiceItemAssign
        fields = '__all__'      
             




  