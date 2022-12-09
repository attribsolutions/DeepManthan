from dataclasses import fields
from rest_framework import serializers
from ..models import *
from ..Serializer.S_Items import *
from ..Serializer.S_Companies import *


# Post and Put Methods Serializer

class WorkOrderItemsSerializer(serializers.ModelSerializer):
    class Meta:
        model =  TC_WorkOrderItems
        fields = ['BomQuantity','Quantity','Item','Unit'] 

class WorkOrderSerializer(serializers.ModelSerializer):
    WorkOrderItems = WorkOrderItemsSerializer(many=True)
    class Meta:
        model = T_WorkOrder
        fields = ['WorkOrderDate','Item','Bom','NumberOfLot','Quantity','Company','Division','CreatedBy','UpdatedBy','WorkOrderItems']  
        
    def create(self, validated_data):
        WorkOrderItems_data = validated_data.pop('WorkOrderItems')
        WorkOrderID= T_WorkOrder.objects.create(**validated_data)
        
        for WorkOrderItem_data in WorkOrderItems_data:
            WorkOrderItem = TC_WorkOrderItems.objects.create(WorkOrder=WorkOrderID, **WorkOrderItem_data)
            
        return WorkOrderID  
     
    
# Get ALL Category,Get Single BOM

class WorkOrderItemsSerializerSecond(serializers.ModelSerializer):
    Unit = ItemUnitsSerializerSecond(read_only=True)
    Item = M_ItemsSerializer01(read_only=True)
    class Meta:
        model =  TC_WorkOrderItems
        fields = ['id','BomQuantity','Quantity','Item','Unit'] 

class WorkOrderSerializerSecond(serializers.ModelSerializer):
    WorkOrderItems = WorkOrderItemsSerializerSecond(many=True)
    Item = M_ItemsSerializer01(read_only=True)
    Company = C_CompanySerializer(read_only=True)
    class Meta:
        model = T_WorkOrder
        fields = ['id','WorkOrderDate','Item','Bom','NumberOfLot','Quantity','Company','Division','CreatedBy','UpdatedBy','CreatedOn','WorkOrderItems'] 

class StockQtyserializer(serializers.Serializer):
    id = serializers.IntegerField()
    actualStock = serializers.DecimalField(max_digits=10, decimal_places=3)
    Item_id=serializers.IntegerField()