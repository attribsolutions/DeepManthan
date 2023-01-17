from dataclasses import fields
import json
from unittest.util import _MAX_LENGTH
from ..models import *
from rest_framework import serializers
from .S_Parties import * 
from .S_Items import * 
from .S_GSTHSNCode import * 
from .S_Margins import * 
from .S_Mrps import * 
from .S_TermsAndConditions import *



# POST Method
class PartiesSerializerSecond(serializers.ModelSerializer):
    class Meta:
        model = M_Parties
        fields = ['id','Name']
        
class DemandReferencesSerializer(serializers.ModelSerializer):
    class Meta:
        model = TC_DemandReferences
        fields = ['MaterialIssue']        
        
class DemandItemsSerializer(serializers.ModelSerializer):
   class Meta:
        model = TC_DemandItems
        fields = ['Item','Quantity','MRP','Rate','Unit','BaseUnitQuantity','GST','Margin','BasicAmount','GSTAmount','CGST','SGST','IGST','CGSTPercentage','SGSTPercentage','IGSTPercentage','Amount', 'Comment']

class DemandSerializer(serializers.ModelSerializer):
    DemandItem = DemandItemsSerializer(many=True)
    DemandReferences = DemandReferencesSerializer(many=True)
    class Meta:
        model = T_Demands
        fields = ['id','DemandDate','Customer','Supplier','DemandNo','FullDemandNumber', 'Division','DemandAmount','Description','BillingAddress','ShippingAddress','CreatedBy', 'UpdatedBy', 'DemandItem', 'DemandReferences']

    def create(self, validated_data):
        DemandItems_data = validated_data.pop('DemandItem')
        DemandReferences_data = validated_data.pop('DemandReferences')
        Demand = T_Demands.objects.create(**validated_data)
        
        for DemandItem_data in DemandItems_data:
            Items=TC_DemandItems.objects.create(Demand=Demand, **DemandItem_data)
            
        for DemandReference_data in DemandReferences_data:
            References = TC_DemandReferences.objects.create(Demand=Demand, **DemandReference_data)
        
        return Demand

class DemandSerializerSecond(serializers.ModelSerializer):
    Customer = PartiesSerializerSecond(read_only=True)
    Supplier = PartiesSerializerSecond(read_only=True)
    class Meta:
        model = T_Demands
        fields = '__all__'
        
class DemandSerializerThird(serializers.ModelSerializer):
    Customer = PartiesSerializerSecond(read_only=True)
    Supplier = PartiesSerializerSecond(read_only=True)
    DemandReferences = DemandReferencesSerializer(many=True)
    DemandItem = DemandItemsSerializer(read_only=True,many=True)
    BillingAddress=PartyAddressSerializerSecond(read_only=True) 
    ShippingAddress=PartyAddressSerializerSecond(read_only=True) 
  
    class Meta:
        model = T_Orders
        fields = '__all__'        