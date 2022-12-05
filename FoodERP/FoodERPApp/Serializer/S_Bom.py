from dataclasses import fields
from rest_framework import serializers
from ..models import *
from ..Serializer.S_Items import *
from ..Serializer.S_Companies import *


# Post and Put Methods Serializer

class MC_BOMItemsSerializer(serializers.ModelSerializer):
    class Meta:
        model =  MC_BillOfMaterialItems
        fields = ['Quantity','Item','Unit'] 

class M_BOMSerializer(serializers.ModelSerializer):
    BOMItems = MC_BOMItemsSerializer(many=True)
    class Meta:
        model = M_BillOfMaterial
        fields = ['BomDate','EstimatedOutput','Comment','IsActive','Item','Unit','Company','CreatedBy','BOMItems']  
        
    def create(self, validated_data):
        BomItems_data = validated_data.pop('BOMItems')
        BomID= M_BillOfMaterial.objects.create(**validated_data)
        
        for BomItem_data in BomItems_data:
            BomItem = MC_BillOfMaterialItems.objects.create(BOM=BomID, **BomItem_data)
            
        return BomID  

    def update(self, instance, validated_data):

        instance.BomDate = validated_data.get(
            'BomDate', instance.BomDate)
        instance.EstimatedOutput = validated_data.get(
            'EstimatedOutput', instance.EstimatedOutput)
        instance.Comment = validated_data.get(
            'Comment', instance.Comment)
        instance.IsActive = validated_data.get(
            'IsActive', instance.IsActive)
        instance.Item = validated_data.get(
            'Item', instance.Item)
        instance.Unit = validated_data.get(
            'Unit', instance.Unit)
        instance.Company = validated_data.get(
            'Company', instance.Company)
          
        instance.save()
        
       

# Get ALL Category,Get Single BOM

class MC_BOMItemsSerializerSecond(serializers.ModelSerializer):
    Item = M_ItemsSerializer01(read_only=True)
    Unit = ItemUnitsSerializerSecond(read_only=True)
    class Meta:
        model =  MC_BillOfMaterialItems
        fields = ['id','Quantity','Item','Unit'] 

class  M_BOMSerializerSecond(serializers.ModelSerializer):
    BOMItems = MC_BOMItemsSerializerSecond(many=True,read_only=True)
    Item = M_ItemsSerializer01(read_only=True)
    Unit = ItemUnitsSerializerSecond(read_only=True)
    Company = C_CompanySerializer(read_only=True)
    class Meta:
        model = M_BillOfMaterial
        fields = ['id','Date','EstimatedOutput','Comment','IsActive','Item','Unit','Company','BOMItems']      