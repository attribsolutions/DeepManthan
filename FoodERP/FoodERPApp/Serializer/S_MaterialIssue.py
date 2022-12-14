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

# class MaterialIssueSerializer(serializers.ModelSerializer):
#     WorkOrderItems = WorkOrderItemsSerializer(many=True)
#     class Meta:
#         model = T_WorkOrder
#         fields = ['MaterialIssueDate','Item','Unit','Bom','NumberOfLot','Quantity','Company','Party','CreatedBy','UpdatedBy','WorkOrderItems']  
        
#     def create(self, validated_data):
#         WorkOrderItems_data = validated_data.pop('WorkOrderItems')
#         WorkOrderID= T_WorkOrder.objects.create(**validated_data)
        
#         for WorkOrderItem_data in WorkOrderItems_data:
#             WorkOrderItem = TC_WorkOrderItems.objects.create(WorkOrder=WorkOrderID, **WorkOrderItem_data)
            
#         return WorkOrderID  
    
#     def update(self, instance, validated_data):
    
#         instance.WorkOrderDate = validated_data.get(
#             'WorkOrderDate', instance.WorkOrderDate)
#         instance.Item = validated_data.get(
#             'Item', instance.Item)
#         instance.Unit = validated_data.get(
#             'Unit', instance.Unit)
#         instance.Bom = validated_data.get(
#             'Bom', instance.Bom)
#         instance.NumberOfLot = validated_data.get(
#             'NumberOfLot', instance.NumberOfLot)
#         instance.Quantity = validated_data.get(
#             'Quantity', instance.Quantity)
#         instance.Company = validated_data.get(
#             'Company', instance.Company)
#         instance.Party = validated_data.get(
#             'Party', instance.Party)
#         instance.CreatedBy = validated_data.get(
#             'CreatedBy', instance.CreatedBy)
#         instance.UpdatedBy = validated_data.get(
#             'UpdatedBy', instance.UpdatedBy)
            
#         instance.save()
        
#         for a in instance.WorkOrderItems.all():
#             a.delete()
        
#         for WorkOrderItems_data in  validated_data['WorkOrderItems']:
#             Item = TC_WorkOrderItems.objects.create(WorkOrder=instance, **WorkOrderItems_data)
#         return instance     
        

           