from dataclasses import fields
import json
from unittest.util import _MAX_LENGTH
from ..models import *
from rest_framework import serializers
from .S_Parties import * 



class M_TermsAndConditionsSerializer(serializers.ModelSerializer):
    class Meta : 
        model = M_TermsAndConditions
        fields = '__all__'

# POST Method
class PartiesSerializerSecond(serializers.ModelSerializer):
    class Meta:
        model = M_Parties
        fields = ['Name']

class TC_OrderItemsSerializer(serializers.ModelSerializer):
    
   class Meta:
        model = TC_OrderItems
        fields = ['Item','Quantity','MRP','Rate','Unit','BaseUnitQuantity','GST','Margin','BasicAmount','GSTAmount','CGST','SGST','IGST','CGSTPercentage','SGSTPercentage','IGSTPercentage','Amount']

class T_OrderSerializer(serializers.ModelSerializer):
    OrderItem = TC_OrderItemsSerializer(many=True)
    class Meta:
        model = T_Orders
        fields = ['id','OrderDate','Customer','Supplier','OrderAmount','Description','CreatedBy', 'UpdatedBy','OrderItem']

    def create(self, validated_data):
        OrderItems_data = validated_data.pop('OrderItem')
        Order = T_Orders.objects.create(**validated_data)
        for OrderItem_data in OrderItems_data:
           TC_OrderItems.objects.create(Order=Order, **OrderItem_data)    
        return Order

    def update(self, instance, validated_data):
        
        # * Order Info
        instance.Customer = validated_data.get(
            'Customer', instance.Customer)
        instance.OrderDate = validated_data.get(
            'OrderDate', instance.OrderDate)    
        instance.Supplier = validated_data.get(
            'Supplier', instance.Supplier)
        instance.OrderAmount = validated_data.get(
            'OrderAmount', instance.OrderAmount)
        instance.Description = validated_data.get(
            'Description', instance.Description)
        instance.UpdatedBy = validated_data.get(
            'UpdatedBy', instance.UpdatedBy) 
        instance.UpdatedOn = validated_data.get(
            'UpdatedOn', instance.UpdatedOn)           
        instance.save()

        for items in instance.OrderItem.all():
          items.delete()

        for OrderItem_data in validated_data['OrderItem']:
            Items = TC_OrderItems.objects.create(Order=instance, **OrderItem_data)
        instance.OrderItem.add(Items)
 
        return instance  


class T_OrderSerializerSecond(serializers.ModelSerializer):
    Customer = PartiesSerializerSecond(read_only=True)
    Supplier = PartiesSerializerSecond(read_only=True)
    class Meta:
        model = T_Orders
        fields = '__all__'
    



    