
from ..Serializer.S_MaterialIssue import obatchwiseStockSerializer
from ..Views.V_CommFunction import *
from ..models import *
from ..Serializer.S_Items import *
from rest_framework import serializers

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
        # fields=['IssueQuantity','BatchDate','BatchCode','SystemBatchDate','SystemBatchCode','Item','LiveBatchID','Unit']

class ProductionReIssueSerializer(serializers.ModelSerializer):
    ProductionItem=ItemSerializer()
    ProductionReIssueItems=ProductionReIssueItemsSerializer(many=True)
    
    class Meta:
        model=T_ProductionReIssue
        # fields = [ 'Date', 'CreatedBy', 'UpdatedBy', 'ProductionID', 'ProductionItem','ProductionReIssueItems','obatchwiseStock']
        fields='__all__'




class ProductionReIssueItemsSerializerForSave(serializers.ModelSerializer):
   
    class Meta:
        model=TC_ProductionReIssueItems
        fields=['IssueQuantity','BatchDate','BatchCode','SystemBatchDate','SystemBatchCode','Item','LiveBatchID','Unit']

class ProductionReIssueSerializerForSave(serializers.ModelSerializer):
    
    ProductionReIssueItems=ProductionReIssueItemsSerializerForSave(many=True)
    obatchwiseStock=obatchwiseStockSerializer(many=True)
    class Meta:
        model=T_ProductionReIssue
        fields = [ 'Date', 'CreatedBy', 'UpdatedBy', 'ProductionID', 'ProductionItem','ProductionReIssueItems','obatchwiseStock']
        # fields='__all__'
    def create(self, validated_data):
       
        ReIssueItems_data = validated_data.pop('ProductionReIssueItems')
        O_BatchWiseLiveStockItems_data= validated_data.pop('obatchwiseStock')
        
        
        
        ProductionIssueID= T_ProductionReIssue.objects.create(**validated_data)
       
        for ProductionReIssueItem_data in ReIssueItems_data:
           
            ProductionReIssueItem = TC_ProductionReIssueItems.objects.create(ProductionReIssue=ProductionIssueID, **ProductionReIssueItem_data)
            
      
        for O_BatchWiseLiveStockItem_data in O_BatchWiseLiveStockItems_data:
            
                OBatchQuantity=O_BatchWiseLiveStock.objects.filter(id=O_BatchWiseLiveStockItem_data['Quantity']).values('BaseUnitQuantity')
                print(OBatchQuantity[0]['BaseUnitQuantity'],O_BatchWiseLiveStockItem_data['BaseUnitQuantity'])
                if(OBatchQuantity[0]['BaseUnitQuantity'] >= O_BatchWiseLiveStockItem_data['BaseUnitQuantity']):
                   
                    OBatchWiseLiveStock=O_BatchWiseLiveStock.objects.filter(id=O_BatchWiseLiveStockItem_data['Quantity']).update(BaseUnitQuantity =  OBatchQuantity[0]['BaseUnitQuantity'] - O_BatchWiseLiveStockItem_data['BaseUnitQuantity'])
                else:
                    
                    raise serializers.ValidationError("Not In Stock ")

        
            
        return ProductionIssueID


class ProductionReIssueItemsSerializerForDelete(serializers.ModelSerializer):
    
    class Meta:
        model=TC_ProductionReIssueItems
        fields='__all__'

class ProductionReIssueSerializerForDelete(serializers.ModelSerializer):
    ProductionReIssueItems=ProductionReIssueItemsSerializerForDelete(many=True)
    
    class Meta:
        model = T_ProductionReIssue
        fields = '__all__'        