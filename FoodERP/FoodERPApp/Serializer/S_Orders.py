from dataclasses import fields
import json
from unittest.util import _MAX_LENGTH
from ..models import *
from rest_framework import serializers


class M_ItemsSerializer(serializers.ModelSerializer):
    class meta:
        model = M_Items
        fields='__all__'

class TC_OrderItemsSerializer(serializers.ModelSerializer):
    
   class Meta:
        model = TC_OrderItems
        fields = ['Item','Quantity','MRP','Rate','Unit','BaseUnitQuantity','GST','Margin','BasicAmount','GSTAmount','CGST','SGST','IGST','CGSTPercentage','SGSTPercentage','IGSTPercentage','Amount']


class TC_OrderItemsSerializerForGET(serializers.Serializer): 
    
    ItemName = serializers.CharField(max_length=500, read_only=True)
    Item_id = serializers.IntegerField(read_only=True)
    Quantity  =  serializers.DecimalField(max_digits = 5,decimal_places=2)
    MRP =  serializers.DecimalField(max_digits = 5,decimal_places=2)
    Rate =  serializers.DecimalField(max_digits = 5,decimal_places=2)
    Unit_id = serializers.IntegerField( read_only=True )
    BaseUnitQuantity = serializers.DecimalField(max_digits = 5,decimal_places=2)
    GST = serializers.DecimalField(max_digits = 5,decimal_places=2) 

class T_OrderSerializerforGET1(serializers.Serializer):
    
    id = serializers.IntegerField()
    OrderDate = serializers.DateField()
    Customer_id = serializers.IntegerField()
    customerName=serializers.CharField(max_length=500)
    Party_id  =  serializers.IntegerField()
    partyName = serializers.CharField(max_length=500)
    OrderAmount = serializers.DecimalField(max_digits = 20,decimal_places=2)
    Description = serializers.CharField(max_length=500)
    CreatedBy = serializers.IntegerField(default=False)
    CreatedOn = serializers.DateTimeField()
   

class T_OrderSerializerforGET(serializers.Serializer):
    id = serializers.IntegerField()
    OrderDate = serializers.DateField()
    Customer_id = serializers.IntegerField()
    customerName=serializers.CharField(max_length=500)
    Party_id  =  serializers.IntegerField()
    partyName = serializers.CharField(max_length=500)
    OrderAmount = serializers.DecimalField(max_digits = 20,decimal_places=2)
    Description = serializers.CharField(max_length=500)
    CreatedBy = serializers.IntegerField(default=False)
    CreatedOn = serializers.DateTimeField()
    ItemName=serializers.CharField(max_length=500)
    Item_id=serializers.IntegerField()
    Quantity=serializers.DecimalField(max_digits=20,decimal_places=2)
    MRP=serializers.DecimalField(max_digits=20,decimal_places=2)
    Rate=serializers.DecimalField(max_digits=20,decimal_places=2)
    Unit_id=serializers.DecimalField(max_digits=20,decimal_places=2)
    BaseUnitQuantity=serializers.DecimalField(max_digits=20,decimal_places=2)
    GST=serializers.DecimalField(max_digits=20,decimal_places=2) 
    BasicAmount=serializers.DecimalField(max_digits=20,decimal_places=2)
    GSTAmount=serializers.DecimalField(max_digits=20,decimal_places=2)
    Amount=serializers.DecimalField(max_digits=20,decimal_places=2)
    CGST = serializers.DecimalField(max_digits = 20,decimal_places=2)
    SGST = serializers.DecimalField(max_digits = 20,decimal_places=2)
    IGST = serializers.DecimalField(max_digits = 20,decimal_places=2)
    CGSTPercentage = serializers.DecimalField(max_digits = 20,decimal_places=2)
    SGSTPercentage = serializers.DecimalField(max_digits = 20,decimal_places=2)
    IGSTPercentage = serializers.DecimalField(max_digits = 20,decimal_places=2)

 

class M_TermsAndConditionsSerializer(serializers.ModelSerializer):
    class Meta : 
        model = M_TermsAndConditions
        fields = '__all__'

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






    # Order input json

    # {
      
    #   "CustomerID": 22,
    #   "PartyID": 22,
    #   "OrderAmount": "333",
    #   "Discreption": "bbb",
    #   "CreatedBy": 22,
    #   "OrderItem": [
    #     {
    #       "ItemID": "aa",
    #       "Quantity": "1.00",
    #       "MRP": "1.00",
    #       "Rate": "10.00",
    #       "UnitID": 1,
    #       "BaseUnitQuantity": "1.00",
    #       "GST": "5.00"
    #     },
    #     {
    #       "ItemID": 2,
    #       "Quantity": "2.00",
    #       "MRP": "2.00",
    #       "Rate": "12.00",
    #       "UnitID": 2,
    #       "BaseUnitQuantity": "2.00",
    #       "GST": "5.00"
    #     }
    #   ]
    # }