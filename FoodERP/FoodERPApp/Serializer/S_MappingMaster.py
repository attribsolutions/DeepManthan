from rest_framework import serializers
from ..models import *

#For Party Customer Mapping 

class PartyMasterMappingSerializer(serializers.ModelSerializer):
    class Meta:
        model = M_PartyCustomerMappingMaster
        fields = '__all__'
    
class PartyCustomerMappingSerializerSecond(serializers.Serializer):
    id = serializers.IntegerField()
    Party_id = serializers.IntegerField()
    Customer = serializers.IntegerField()
    CustomerName = serializers.CharField(max_length=100)
    MapCustomer = serializers.CharField(max_length=200)    

# For Items Mapping Serializers

class ItemsMappingSerializer(serializers.ModelSerializer):
    class Meta:
        model = M_ItemMappingMaster
        fields = '__all__'

class ItemsSerializerSecond(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField(max_length=200)
    MapItem = serializers.CharField(max_length= 200)