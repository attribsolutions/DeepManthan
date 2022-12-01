from dataclasses import fields
from django.forms import SlugField
from rest_framework import serializers

from ..models import *


# Post and Put Methods Serializer

class MC_BOMItemsSerializer(serializers.ModelSerializer):
    class Meta:
        model =  MC_BillOfMaterialItems
        fields = ['Quantity','Item','Unit'] 

class M_BOMSerializer(serializers.ModelSerializer):
    BOMItems = MC_BOMItemsSerializer(many=True)
    class Meta:
        model = M_BillOfMaterial
        fields = ['Date','EstimatedOutput','Comment','IsActive','Item','Unit','BOMItems']  

# Get ALL Category,Get Single BOM

class MC_BOMItemsSerializerSecond(serializers.ModelSerializer):
    class Meta:
        model =  MC_BillOfMaterialItems
        fields = ['Quantity','Item','Unit'] 

class M_BOMSerializerSecond(serializers.ModelSerializer):
    BOMItems = MC_BOMItemsSerializerSecond(read_only=True)
    class Meta:
        model = M_BillOfMaterial
        fields = ['Date','EstimatedOutput','Comment','IsActive','Item','Unit','BOMItems']      