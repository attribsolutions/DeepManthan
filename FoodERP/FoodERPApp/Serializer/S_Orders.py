from dataclasses import fields
import json
from unittest.util import _MAX_LENGTH
from ..models import *
from rest_framework import serializers
from .S_Parties import * 
from .S_Items import * 
from .S_GSTHSNCode import * 
from .S_Margins import * 
from .S_Mrps import * 


class M_POTypeserializer(serializers.ModelSerializer):
    class Meta : 
        model = M_POType
        fields = '__all__'


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
        fields = ['Item','Quantity','MRP','Rate','Unit','BaseUnitQuantity','GST','Margin','BasicAmount','GSTAmount','CGST','SGST','IGST','CGSTPercentage','SGSTPercentage','IGSTPercentage','Amount','IsDeleted']

class TC_OrderTermsAndConditionsSerializer(serializers.ModelSerializer):
    class Meta:
        model=TC_OrderTermsAndConditions
        fields =['TermsAndCondition','IsDeleted']

class T_OrderSerializer(serializers.ModelSerializer):
    OrderItem = TC_OrderItemsSerializer(many=True)
    OrderTermsAndConditions=TC_OrderTermsAndConditionsSerializer(many=True)
    class Meta:
        model = T_Orders
        fields = ['id','OrderDate','DeliveryDate','Customer','Supplier','OrderNo','FullOrderNumber','OrderType','POType','Division','OrderAmount','Description','BillingAddress','ShippingAddress','CreatedBy', 'UpdatedBy','IsOpenPO','POFromDate','POToDate','OrderItem','OrderTermsAndConditions','Inward']

    def create(self, validated_data):
        OrderItems_data = validated_data.pop('OrderItem')
        OrderTermsAndConditions_data = validated_data.pop('OrderTermsAndConditions')
        
        Order = T_Orders.objects.create(**validated_data)
        
        for OrderItem_data in OrderItems_data:
           TC_OrderItems.objects.create(Order=Order, **OrderItem_data)

        for OrderTermsAndCondition_data in OrderTermsAndConditions_data:
            TC_OrderTermsAndConditions.objects.create(Order=Order, **OrderTermsAndCondition_data)       
        
        return Order

    def update(self, instance, validated_data):
        
        # * Order Info
        
        instance.OrderDate = validated_data.get(
            'OrderDate', instance.OrderDate)   
        instance.DeliveryDate = validated_data.get(
            'DeliveryDate', instance.DeliveryDate)
        instance.POFromDate = validated_data.get(
            'POFromDate', instance.POFromDate)   
        instance.POToDate = validated_data.get(
            'POToDate', instance.POToDate)          
        instance.OrderAmount = validated_data.get(
            'OrderAmount', instance.OrderAmount)
        instance.Description = validated_data.get(
            'Description', instance.Description)
        instance.BillingAddress = validated_data.get(
            'BillingAddress', instance.BillingAddress)
        instance.ShippingAddress = validated_data.get(
            'ShippingAddress', instance.ShippingAddress)
        instance.UpdatedBy = validated_data.get(
            'UpdatedBy', instance.UpdatedBy) 
                
        instance.save()

        # for items in instance.OrderItem.all():
        #     print(items.IsDeleted)
        #     SetFlag=TC_OrderItems.objects.filter(id=items.id).update(IsDeleted=1)
            
            
        # for items in instance.OrderTermsAndConditions.all():
            
        #     SetFlag=TC_OrderItems.objects.filter(id=items.id).update(IsDeleted=1)
            

        for OrderItem_data in validated_data['OrderItem']:
            if(OrderItem_data['Quantity'] == 0 and OrderItem_data['IsDeleted'] == 1 ) :
                SetFlag=TC_OrderItems.objects.filter(Item=OrderItem_data['Item'],Order=instance,IsDeleted=0).update(IsDeleted=1)
            elif(OrderItem_data['IsDeleted'] == 0 ) :
                SetFlag=TC_OrderItems.objects.filter(Item=OrderItem_data['Item'],Order=instance,IsDeleted=0)
                
                if SetFlag.count() == 0:
                    OrderItem_data['IsDeleted']=0
                    Items = TC_OrderItems.objects.create(Order=instance, **OrderItem_data)
            else: 
                SetFlag=TC_OrderItems.objects.filter(Item=OrderItem_data['Item'],Order=instance).update(IsDeleted=1)
                OrderItem_data['IsDeleted']=0
                Items = TC_OrderItems.objects.create(Order=instance, **OrderItem_data)
            
            
            
       
        for OrderTermsAndCondition_data in validated_data['OrderTermsAndConditions']:
            if(OrderTermsAndCondition_data['IsDeleted'] == 1 ) :
                SetFlag=TC_OrderTermsAndConditions.objects.filter(Order=instance).update(IsDeleted=1)
            else:
                TestExistance=TC_OrderTermsAndConditions.objects.filter(Order=instance ,TermsAndCondition=OrderTermsAndCondition_data['TermsAndCondition'])
                if TestExistance.count() == 0:
                    Items = TC_OrderTermsAndConditions.objects.create(Order=instance, **OrderTermsAndCondition_data)
       
 
        return instance  


class T_OrderSerializerSecond(serializers.ModelSerializer):
    Customer = PartiesSerializerSecond(read_only=True)
    Supplier = PartiesSerializerSecond(read_only=True)
    BillingAddress=PartyAddressSerializerSecond(read_only=True) 
    ShippingAddress=PartyAddressSerializerSecond(read_only=True) 
    class Meta:
        model = T_Orders
        fields = '__all__'

class PartiesSerializerThird(serializers.ModelSerializer):
    class Meta:
        model = M_Parties
        fields = ['id','Name']


class UnitSerializerThird(serializers.ModelSerializer):
    class Meta:
        model = M_Units
        fields = ['id','Name']
        
class Mc_ItemUnitSerializerThird(serializers.ModelSerializer):
    UnitID = UnitSerializerSecond(read_only=True)
    class Meta:
        model = MC_ItemUnits
        fields = ['id','UnitID']      
        
class TC_OrderItemSerializer(serializers.ModelSerializer):
    
    MRP = M_MRPsSerializer(read_only=True)
    GST = M_GstHsnCodeSerializer(read_only=True)
    Margin = M_MarginsSerializer(read_only=True)
    Item = M_ItemsSerializer01(read_only=True)
    Unit = Mc_ItemUnitSerializerThird(read_only=True)
    class Meta:
        model = TC_OrderItems
        fields = '__all__'
        
    def to_representation(self, instance):
        # get representation from ModelSerializer
        ret = super(TC_OrderItemSerializer, self).to_representation(instance)
        # if parent is None, overwrite
        if not ret.get("MRP", None):
            ret["MRP"] = {"id": None, "MRP": None}
            
        if not ret.get("Margin", None):
            ret["Margin"] = {"id": None, "Margin": None}    
        return ret      



class TC_OrderTermsAndConditionsSerializer(serializers.ModelSerializer):
    TermsAndCondition=M_TermsAndConditionsSerializer(read_only=True)
    class Meta:
        model=TC_OrderTermsAndConditions
        fields ='__all__'

class T_OrderSerializerThird(serializers.ModelSerializer):
    Customer = PartiesSerializerThird(read_only=True)
    Supplier = PartiesSerializerThird(read_only=True)
    OrderItem = TC_OrderItemSerializer(read_only=True,many=True)
    OrderTermsAndConditions=TC_OrderTermsAndConditionsSerializer(many=True)
    BillingAddress=PartyAddressSerializerSecond(read_only=True) 
    ShippingAddress=PartyAddressSerializerSecond(read_only=True) 
    
    class Meta:
        model = T_Orders
        fields = '__all__'


'''Order Serializer For Make Grn'''


# class PartiesSerializerForGrn(serializers.ModelSerializer):
#     class Meta:
#         model = M_Parties
#         fields = ['id','Name']
        
class OrderSerializerForGrn(serializers.Serializer):
    id=serializers.IntegerField()
    SupplierName = serializers.CharField(max_length=500)     
    OrderAmount=serializers.DecimalField(max_digits=10, decimal_places=2) 
    CustomerID =serializers.IntegerField() 


    