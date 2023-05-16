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

class ItemMappingMasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = M_ItemMappingMaster
        fields = '__all__'

class ItemMappingMasterSerializerSecond(serializers.Serializer):
    id = serializers.IntegerField()
    Item_id = serializers.IntegerField()
    Party_id = serializers.IntegerField()
    Name = serializers.CharField(max_length=200)
    MapItem = serializers.CharField(max_length= 200)

# For Units Mapping Serializers

class UnitsMappingSerializer(serializers.ModelSerializer):
    class Meta:
        model = M_UnitMappingMaster
        fields = '__all__'

class UnitsMappingSerializerSecond(serializers.Serializer):
    id = serializers.IntegerField()
    Party_id = serializers.IntegerField()
    Name = serializers.CharField(max_length= 200)
    MapUnit = serializers.CharField(max_length= 200)


