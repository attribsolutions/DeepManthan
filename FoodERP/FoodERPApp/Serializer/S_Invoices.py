from dataclasses import fields
import json
from ..models import *
from rest_framework import serializers


class T_InvoiceSerializerGETList(serializers.Serializer):
    id=serializers.IntegerField()
    Customer_id = serializers.IntegerField()
    CustomerName=serializers.CharField(max_length=500)
    Party_id =serializers.IntegerField()
    PartyName=serializers.CharField(max_length=500)
    InvoiceDate = serializers.DateField()
    InvoiceNumber  =  serializers.IntegerField()
    FullInvoiceNumber =  serializers.CharField(max_length=500)
    CustomerGSTTin = serializers.CharField(max_length=500)
    GrandTotal =  serializers.DecimalField(max_digits = 15,decimal_places=2)
    RoundOffAmount = serializers.DecimalField(max_digits = 5,decimal_places=2)
    CreatedBy  =  serializers.IntegerField()
    CreatedOn =  serializers.DateTimeField()
    UpdatedBy = serializers.IntegerField()
    UpdatedOn = serializers.DateTimeField()
    Order_id = serializers.IntegerField()
    
    


class TC_InvoiceItemBatchesSerializer(serializers.ModelSerializer):
    class Meta:
        model = TC_InvoiceItemBatches
        fields = ['Item','BatchDate','BatchCode','Quantity','Unit','MRP','CreatedOn']
        
class TC_InvoiceItemsSerializer(serializers.ModelSerializer):
    InvoiceItemBatches = TC_InvoiceItemBatchesSerializer(many=True) 
    class Meta:
        model = TC_InvoiceItems
        fields = ['Item','HSNCode','Quantity','Unit','BaseUnitQuantity','QtyInKg','QtyInNo','QtyInBox','MRP','Rate','BasicAmount','TaxType','GSTPercentage','GSTAmount','Amount','DiscountType','Discount','DiscountAmount','CGST','SGST','IGST','CGSTPercentage','SGSTPercentage','IGSTPercentage','InvoiceItemBatches']   
        
class T_InvoiceSerializer(serializers.ModelSerializer):
    InvoiceItems = TC_InvoiceItemsSerializer(many=True)
    class Meta:
        model = T_Invoices
        fields = ['Order','InvoiceDate','Customer','InvoiceNumber','FullInvoiceNumber','CustomerGSTTin','GrandTotal','Party','RoundOffAmount','CreatedBy','UpdatedBy','InvoiceItems']

    def create(self, validated_data):
        InvoiceItems_data = validated_data.pop('InvoiceItems')
        InvoiceID = T_Invoices.objects.create(**validated_data)
        for InvoiceItem_data in InvoiceItems_data:
            InvoiceItemBatches_data = InvoiceItem_data.pop('InvoiceItemBatches')
            InvoiceItemID =TC_InvoiceItems.objects.create(Invoice=InvoiceID, **InvoiceItem_data)
            for InvoiceItemBatch_data in InvoiceItemBatches_data:
               TC_InvoiceItemBatches.objects.create(Invoice=InvoiceID,InvoiceItem=InvoiceItemID, **InvoiceItemBatch_data)
        
        return InvoiceID       
    
    def update(self, instance, validated_data):
        
        instance.Order = validated_data.get(
            'Order', instance.Order)
        instance.Customer = validated_data.get(
            'Customer', instance.Customer)
        instance.Party = validated_data.get(
            'Party', instance.Party)
        instance.GrandTotal = validated_data.get(
            'GrandTotal', instance.GrandTotal)
        instance.RoundOffAmount = validated_data.get(
            'RoundOffAmount', instance.RoundOffAmount)    
        instance.save()
        
        for items in instance.InvoiceItems.all():
            items.delete()
        
        for InvoiceItem_data in validated_data['InvoiceItems']:
            InvoiceItemBatches_data = InvoiceItem_data.pop('InvoiceItemBatches')
            TC_InvoiceItemsID = TC_InvoiceItems.objects.create(Invoice=instance, **InvoiceItem_data)
            for InvoiceItemBatch_data in InvoiceItemBatches_data:
               TC_InvoiceItemBatches.objects.create(Invoice=instance,InvoiceItem=TC_InvoiceItemsID, **InvoiceItemBatch_data)
        return instance 



    