from rest_framework import serializers
from ..models import *

# Post and Put Methods Serializer

class CentralServiceItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = M_CentralServiceItems
        fields = '__all__'

class UnitSerializerSecond(serializers.ModelSerializer):
    class Meta:
        model = M_Units
        fields = ['id','Name','SAPUnit','EwayBillUnit']
        
class CentralServiceItemGetSerializer(serializers.ModelSerializer):
    Unit = UnitSerializerSecond()
    class Meta:
        model = M_CentralServiceItems
        fields = ['id', 'Name', 'HSNCode', 'GSTPercentage', 'isActive', 'CreatedBy', 'CreatedOn', 'UpdatedBy', 'UpdatedOn', 'Unit', 'Company', 'Rate']
  
class MC_CentralServiceItemAssignSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    Name=serializers.CharField(max_length=500)
    Party_id = serializers.IntegerField()
    PartyName=serializers.CharField(max_length=500)
    Rate = serializers.DecimalField(max_digits=10, decimal_places=2)
    
    
    
class MC_CentralServiceItemAssignSerializerSecond(serializers.ModelSerializer):
    class Meta:
        model =  MC_CentralServiceItemAssign
        fields = '__all__'      
             




  