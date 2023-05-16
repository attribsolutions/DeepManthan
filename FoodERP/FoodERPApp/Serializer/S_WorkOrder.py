from rest_framework import serializers
from ..models import *
from ..Serializer.S_Items import *
from ..Serializer.S_Companies import *
from ..Serializer.S_Parties import *
# Post and Put Methods Serializer

class WorkOrderItemsSerializer(serializers.ModelSerializer):
    class Meta:
        model =  TC_WorkOrderItems
        fields = ['BomQuantity','Quantity','Item','Unit'] 

class WorkOrderSerializer(serializers.ModelSerializer):
    WorkOrderItems = WorkOrderItemsSerializer(many=True)
    class Meta:
        model = T_WorkOrder
        fields = ['WorkOrderDate','WorkOrderNumber','FullWorkOrderNumber','Item','Unit','Bom','NumberOfLot','Quantity','Company','Party','CreatedBy','UpdatedBy','WorkOrderItems']  
        
    def create(self, validated_data):
        WorkOrderItems_data = validated_data.pop('WorkOrderItems')
        WorkOrderID= T_WorkOrder.objects.create(**validated_data)
        
        for WorkOrderItem_data in WorkOrderItems_data:
            WorkOrderItem = TC_WorkOrderItems.objects.create(WorkOrder=WorkOrderID, **WorkOrderItem_data)
            
        return WorkOrderID  
    
    def update(self, instance, validated_data):
    
        instance.WorkOrderDate = validated_data.get(
            'WorkOrderDate', instance.WorkOrderDate)
        instance.WorkOrderNumber = validated_data.get(
            'WorkOrderNumber', instance.WorkOrderNumber)
        instance.FullWorkOrderNumber = validated_data.get(
            'FullWorkOrderNumber', instance.FullWorkOrderNumber)
        instance.Item = validated_data.get(
            'Item', instance.Item)
        instance.Unit = validated_data.get(
            'Unit', instance.Unit)
        instance.Bom = validated_data.get(
            'Bom', instance.Bom)
        instance.NumberOfLot = validated_data.get(
            'NumberOfLot', instance.NumberOfLot)
        instance.Quantity = validated_data.get(
            'Quantity', instance.Quantity)
        instance.Company = validated_data.get(
            'Company', instance.Company)
        instance.Party = validated_data.get(
            'Party', instance.Party)
        instance.UpdatedBy = validated_data.get(
            'UpdatedBy', instance.UpdatedBy)
            
        instance.save()
        
        for a in instance.WorkOrderItems.all():
            a.delete()
        
        for WorkOrderItems_data in  validated_data['WorkOrderItems']:
            Item = TC_WorkOrderItems.objects.create(WorkOrder=instance, **WorkOrderItems_data)
        return instance   
    
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
    Party = DivisionsSerializer(read_only=True)
    Unit = ItemUnitsSerializerSecond(read_only=True)
    class Meta:
        model = T_WorkOrder
        fields = ['id','WorkOrderDate','WorkOrderNumber','FullWorkOrderNumber','Item','Unit','Bom','NumberOfLot','Quantity','Company','Party','CreatedBy','UpdatedBy','CreatedOn','WorkOrderItems'] 
