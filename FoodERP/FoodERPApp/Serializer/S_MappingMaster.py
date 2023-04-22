from rest_framework import serializers
from ..models import *


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