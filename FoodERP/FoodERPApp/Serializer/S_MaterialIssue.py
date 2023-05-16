from rest_framework import serializers
from ..models import *
from ..Serializer.S_Items import *
from ..Serializer.S_Companies import *
from ..Serializer.S_Parties import * 

class LiveBatchSerializer(serializers.ModelSerializer):
    class Meta:
        model =O_LiveBatches
        fields='__all__'

class StockQtyserializerForMaterialIssue(serializers.ModelSerializer):
    LiveBatche=LiveBatchSerializer()
    class Meta:
        model = O_BatchWiseLiveStock
        fields = ['id','Item','Quantity','BaseUnitQuantity','Party','LiveBatche']  

class MaterialIssueWorkOrdersSerializer(serializers.ModelSerializer):
    class Meta:
        model = TC_MaterialIssueWorkOrders
        fields =['WorkOrder', 'Bom']

class MaterialIssueItemsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TC_MaterialIssueItems
        fields =['WorkOrderQuantity', 'IssueQuantity', 'BatchDate', 'BatchCode', 'SystemBatchDate', 'SystemBatchCode', 'LiveBatchID','Item','Unit']

class obatchwiseStockSerializer(serializers.ModelSerializer):
    class Meta:
        model=O_BatchWiseLiveStock
        fields=['Quantity','BaseUnitQuantity','Item']

class MaterialIssueSerializer(serializers.ModelSerializer):
    MaterialIssueWorkOrder = MaterialIssueWorkOrdersSerializer(many=True)
    MaterialIssueItems = MaterialIssueItemsSerializer(many=True)
    obatchwiseStock=obatchwiseStockSerializer(many=True)
    class Meta:
        model = T_MaterialIssue
        fields = ['id', 'MaterialIssueDate', 'MaterialIssueNumber', 'FullMaterialIssueNumber', 'NumberOfLot', 'LotQuantity','CreatedBy','UpdatedBy','Company','Party','Item','Unit','MaterialIssueItems','MaterialIssueWorkOrder','obatchwiseStock']
    
    def create(self, validated_data):
        
        MaterialIssueItems_data = validated_data.pop('MaterialIssueItems')
        MaterialIssueWorkOrders_data = validated_data.pop('MaterialIssueWorkOrder')
        O_BatchWiseLiveStockItems_data= validated_data.pop('obatchwiseStock')

        MaterialIssueID= T_MaterialIssue.objects.create(**validated_data)
        
        for MaterialIssueItem_data in MaterialIssueItems_data:
            WorkOrderItem = TC_MaterialIssueItems.objects.create(MaterialIssue=MaterialIssueID, **MaterialIssueItem_data)
            
        
        for O_BatchWiseLiveStockItem_data in O_BatchWiseLiveStockItems_data:
            
                OBatchQuantity=O_BatchWiseLiveStock.objects.filter(id=O_BatchWiseLiveStockItem_data['Quantity']).values('BaseUnitQuantity')
                
                if(OBatchQuantity[0]['BaseUnitQuantity'] >= O_BatchWiseLiveStockItem_data['BaseUnitQuantity']):
                    OBatchWiseLiveStock=O_BatchWiseLiveStock.objects.filter(id=O_BatchWiseLiveStockItem_data['Quantity']).update(BaseUnitQuantity =  OBatchQuantity[0]['BaseUnitQuantity'] - O_BatchWiseLiveStockItem_data['BaseUnitQuantity'])
                else:
                
                    raise serializers.ValidationError("Not In Stock ")

        for MaterialIssueWorkOrder_data in MaterialIssueWorkOrders_data:
            MaterialIssueWorkOrder = TC_MaterialIssueWorkOrders.objects.create(MaterialIssue=MaterialIssueID, **MaterialIssueWorkOrder_data)   
           
            
        return MaterialIssueID    
    


    
# Get ALL ,Get Single BOM

class MaterialIssueItemsSerializerSecond(serializers.ModelSerializer):
    Unit = ItemUnitsSerializerSecond(read_only=True)
    Item = M_ItemsSerializer01(read_only=True)
    class Meta:
        model = TC_MaterialIssueItems
        fields =['WorkOrderQuantity', 'IssueQuantity', 'BatchDate', 'BatchCode', 'SystemBatchDate', 'SystemBatchCode', 'Item','Unit']
        
             
        
class MatetrialIssueSerializerSecond(serializers.ModelSerializer):
    Item = M_ItemsSerializer01(read_only=True)
    Company = C_CompanySerializer(read_only=True)
    Party = DivisionsSerializer(read_only=True)
    Unit = ItemUnitsSerializerSecond(read_only=True)
    class Meta:
        model = T_MaterialIssue
        fields = ['id', 'MaterialIssueDate','MaterialIssueNumber','FullMaterialIssueNumber','NumberOfLot', 'LotQuantity','CreatedBy','UpdatedBy','Company','Party','Item','Unit','CreatedOn']
    


class obatchwiseStockSerializerfordelete(serializers.ModelSerializer):
    
    # def create(self, validated_data):
    #     for aa in validated_data:
    #         bb=O_BatchWiseLiveStock.objects.create(**aa)
    #     return bb
    
    class Meta:
        model=O_BatchWiseLiveStock
        # fields=['Item','Quantity','Unit','BaseUnitQuantity','OriginalBaseUnitQuantity','Party','LiveBatche','CreatedBy']
        fields = '__all__'
class MatetrialIssueSerializerForDelete(serializers.ModelSerializer):
    MaterialIssueItems = MaterialIssueItemsSerializer(many=True)
    
    class Meta:
        model = T_MaterialIssue
        fields = '__all__'

      
class TestMaterialIssueItemSerializer(serializers.ModelSerializer):
    Item = M_ItemsSerializer01(read_only=True)
    Unit = ItemUnitsSerializerSecond(read_only=True)

    class Meta:
        model = TC_MaterialIssueItems
        fields = '__all__'
    def to_representation(self, instance):
        # get representation from ModelSerializer
        data = super(TestMaterialIssueItemSerializer, self).to_representation(instance)

        data['Item'] = instance.Item.id
        data['ItemName'] = instance.Item.Name
        data['Unit'] = instance.Unit.id
        data['UnitName'] = instance.Unit.UnitID.Name
        
        return data        

class TestMaterialIssueShowSerializer(serializers.ModelSerializer):
    Party = DivisionsSerializer(read_only=True)
    Company = C_CompanySerializer(read_only=True)
    Item = M_ItemsSerializer01(read_only=True)
    Unit = ItemUnitsSerializerSecond(read_only=True)
    MaterialIssueItems = TestMaterialIssueItemSerializer(many=True)

    class Meta:
        model = T_MaterialIssue
        fields = '__all__'

    def to_representation(self, instance):
        data = super(TestMaterialIssueShowSerializer, self).to_representation(instance)
        data['Party'] = instance.Party.id
        data['PartyName'] = instance.Party.Name
        data['Company'] = instance.Company.id
        data['CompanyName'] = instance.Company.Name
        data['Item'] = instance.Item.id
        data['ItemName'] = instance.Item.Name
        data['Unit'] = instance.Unit.id
        data['UnitName'] = instance.Unit.UnitID.Name
        return data
                