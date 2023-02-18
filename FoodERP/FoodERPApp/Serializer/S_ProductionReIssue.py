from asyncore import read
from dataclasses import field
from ..Views.V_CommFunction import *
from ..models import *
from ..Serializer.S_Items import *
from rest_framework import serializers
from django.db.models import Max


class ItemSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = M_Items
        fields = ['id','Name']


class MaterialIssueItemsSerializer(serializers.ModelSerializer):
    Item=ItemSerializer(read_only=True)
    Unit = ItemUnitsSerializerSecond(read_only=True)
    class Meta:
        model = TC_MaterialIssueItems
        # fields = ['Item']
        fields='__all__'

class ProductionReIssueItemsSerializer(serializers.ModelSerializer):
    Item=ItemSerializer(read_only=True)
    Unit = ItemUnitsSerializerSecond(read_only=True)
    class Meta:
        model=TC_ProductionReIssueItems
        fields='__all__'

class ProductionReIssueSerializer(serializers.ModelSerializer):
    ProductionItem=ItemSerializer(read_only=True)
    ProductionReIssueItems=ProductionReIssueItemsSerializer(read_only=True,many=True)
    class Meta:
        model=T_ProductionReIssue
        # fields = [ 'Date', 'CreatedBy', 'UpdatedBy', 'ProductionID', 'ProductionItem','ProductionReIssueItems']
        fields='__all__'
    def create(self, validated_data):
       
        ReIssueItems_data = validated_data.pop('ProductionReIssueItems')
        O_BatchWiseLiveStockItems_data= validated_data.pop('obatchwiseStock')
        ProductionIssueID= T_ProductionReIssue.objects.create(**validated_data)
        
        for ProductionRelIssueItem_data in ReIssueItems_data:
            ProductionReIssueItem = TC_ProductionReIssueItems.objects.create(ProductionReIssue=ProductionIssueID, **ProductionRelIssueItem_data)
            
        
        for O_BatchWiseLiveStockItem_data in O_BatchWiseLiveStockItems_data:
            
                OBatchQuantity=O_BatchWiseLiveStock.objects.filter(id=O_BatchWiseLiveStockItem_data['Quantity']).values('BaseUnitQuantity')
                
                if(OBatchQuantity[0]['BaseUnitQuantity'] >= O_BatchWiseLiveStockItem_data['BaseUnitQuantity']):
                    OBatchWiseLiveStock=O_BatchWiseLiveStock.objects.filter(id=O_BatchWiseLiveStockItem_data['Quantity']).update(BaseUnitQuantity =  OBatchQuantity[0]['BaseUnitQuantity'] - O_BatchWiseLiveStockItem_data['BaseUnitQuantity'])
                else:
                
                    raise serializers.ValidationError("Not In Stock ")

        # # for MaterialIssueWorkOrder_data in MaterialIssueWorkOrders_data:
        # #     MaterialIssueWorkOrder = TC_MaterialIssueWorkOrders.objects.create(MaterialIssue=MaterialIssueID, **MaterialIssueWorkOrder_data)   
           
            
        return ProductionIssueID