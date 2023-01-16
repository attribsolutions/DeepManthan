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


class M_POTypeserializer(serializers.ModelSerializer):
    class Meta : 
        model = M_POType
        fields = '__all__'

# POST Method
class PartiesSerializerSecond(serializers.ModelSerializer):
    class Meta:
        model = M_Parties
        fields = ['id','Name']

class DemandItemsSerializer(serializers.ModelSerializer):
    
   class Meta:
        model = TC_DemandItems
        fields = ['Item','Quantity','MRP','Rate','Unit','BaseUnitQuantity','GST','Margin','BasicAmount','GSTAmount','CGST','SGST','IGST','CGSTPercentage','SGSTPercentage','IGSTPercentage','Amount','IsDeleted','Comment']

class DemandSerializer(serializers.ModelSerializer):
    DemandItem = DemandItemsSerializer(many=True)
   
    class Meta:
        model = T_Demands
        fields = ['id','DemandDate','DeliveryDate','Customer','Supplier','DemandNo','FullDemandNumber','OrderType','POType','Division','DemandAmount','Description','BillingAddress','ShippingAddress','CreatedBy', 'UpdatedBy','IsOpenPO','POFromDate','POToDate','DemandItem']

    def create(self, validated_data):
        DemandItems_data = validated_data.pop('DemandItem')
        Demand = T_Demands.objects.create(**validated_data)
        
        for DemandItem_data in DemandItems_data:
            TC_DemandItems.objects.create(Demand=Demand, **DemandItem_data)

        return Demand
