from dataclasses import fields

from ..Serializer.S_GRNs import O_BatchWiseLiveStockSerializer
from ..models import *
from rest_framework import serializers


class ProductionMaterialIssueSerializer(serializers.ModelSerializer):
    class Meta:
        model =TC_ProductionMaterialIssue
        fields=['MaterialIssue']

class H_ProductionSerializer(serializers.ModelSerializer):
    ProductionMaterialIssue=ProductionMaterialIssueSerializer(many=True)
    O_BatchWiseLiveStockItems = O_BatchWiseLiveStockSerializer(many=True)
    class Meta:
        model = T_Production
        fields = '__all__'

    def create(self, validated_data):
        ProductionMaterialIssues_data = validated_data.pop('ProductionMaterialIssue')
        O_BatchWiseLiveStockItems_data=validated_data.pop('O_BatchWiseLiveStockItems')
        
        ProductionID= T_Production.objects.create(**validated_data)
       
        for O_BatchWiseLiveStockItem_data in O_BatchWiseLiveStockItems_data :
            O_BatchWiseLiveStockdata=O_BatchWiseLiveStock.objects.create(**O_BatchWiseLiveStockItem_data)  
          
        for ProductionMaterialIssue_data in ProductionMaterialIssues_data:
            Productionreff = TC_ProductionMaterialIssue.objects.create(Production=ProductionID, **ProductionMaterialIssue_data)
            
        return ProductionID



class ProductionMaterialIssueSerializer(serializers.ModelSerializer):
    class Meta:
        model =TC_ProductionMaterialIssue
        fields='__all__'


class H_ProductionSerializer2(serializers.ModelSerializer):
    class Meta:
        model = H_Modules
        fields = ['id','Name']
