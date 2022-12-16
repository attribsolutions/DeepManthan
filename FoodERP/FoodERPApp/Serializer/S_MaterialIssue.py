from dataclasses import fields
from rest_framework import serializers
from ..models import *
from ..Serializer.S_Items import *
from ..Serializer.S_Companies import *
from ..Serializer.S_Parties import *


class StockQtyserializerForMaterialIssue(serializers.ModelSerializer):
    class Meta:
        model = O_BatchWiseLiveStock
        fields = ['id','Item','BatchDate','BatchCode','SystemBatchDate','SystemBatchCode','Quantity','BaseUnitQuantity','Party']  

class MaterialIssueWorkOrdersSerializer(serializers.ModelSerializer):
    class Meta:
        model = TC_MaterialIssueWorkOrders
        fields =['WorkOrder', 'Bom']

class MaterialIssueItemsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TC_MaterialIssueItems
        fields =['WorkOrderQuantity', 'IssueQuantity', 'BatchDate', 'BatchCode', 'SystemBatchDate', 'SystemBatchCode', 'Item','Unit']

class MaterialIssueSerializer(serializers.ModelSerializer):
    MaterialIssueWorkOrder = MaterialIssueWorkOrdersSerializer(many=True)
    MaterialIssueItems = MaterialIssueItemsSerializer(many=True)
    class Meta:
        model = T_MaterialIssue
        fields = ['id', 'MaterialIssueDate', 'NumberOfLot', 'LotQuantity','CreatedBy','UpdatedBy','Company','Party','Item','MaterialIssueItems','MaterialIssueWorkOrder']
    
    def create(self, validated_data):
        MaterialIssueItems_data = validated_data.pop('MaterialIssueItems')
        MaterialIssueWorkOrders_data = validated_data.pop('MaterialIssueWorkOrder')
        
        MaterialIssueID= T_MaterialIssue.objects.create(**validated_data)
        
        for MaterialIssueItem_data in MaterialIssueItems_data:
            WorkOrderItem = TC_MaterialIssueItems.objects.create(MaterialIssue=MaterialIssueID, **MaterialIssueItem_data)
        
        for MaterialIssueWorkOrder_data in MaterialIssueWorkOrders_data:
            MaterialIssueWorkOrder = TC_MaterialIssueWorkOrders.objects.create(MaterialIssue=MaterialIssueID, **MaterialIssueWorkOrder_data)    
            
        return MaterialIssueID    

# Get ALL ,Get Single BOM

class MaterialIssueItemsSerializerSecond(serializers.ModelSerializer):
    Unit = ItemUnitsSerializerSecond(read_only=True)
    Item = M_ItemsSerializer01(read_only=True)
    class Meta:
        model =  TC_MaterialIssueItems
        fields = ['id', 'WorkOrderQuantity', 'IssueQuantity', 'BatchDate', 'BatchCode','BatchCodeQuantity', 'SystemBatchDate', 'SystemBatchCode', 'Item', 'MaterialIssue', 'Unit']
        
             
        
class MatetrialIssueSerializerSecond(serializers.ModelSerializer):
    MaterialIssueItems = MaterialIssueItemsSerializerSecond(many=True)
    Item = M_ItemsSerializer01(read_only=True)
    Company = C_CompanySerializer(read_only=True)
    Party = DivisionsSerializer(read_only=True)
    Unit = ItemUnitsSerializerSecond(read_only=True)
    class Meta:
        model = T_MaterialIssue
        fields = ['MaterialIssueDate','Item','Unit','Bom','NumberOfLot','Quantity','Company','Party','CreatedBy','UpdatedBy','MaterialIssueItems']
    
           