from dataclasses import fields
import json
from ..models import *
from rest_framework import serializers


class T_InvoiceSerializerGETList(serializers.Serializer):
    id=serializers.IntegerField()
    Customer = serializers.IntegerField()
    CustomerName=serializers.CharField(max_length=500)
    Party =serializers.IntegerField()
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
   
    OrderID_id = serializers.IntegerField()
    


class TC_InvoiceItemBatchesSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = TC_InvoiceItemBatches
        fields = ['id','ItemID','BatchDate','BatchCode','Quantity','UnitID','MRP','CreatedOn']
        
class TC_InvoiceItemsSerializer(serializers.ModelSerializer):
    InvoiceItemBatches = TC_InvoiceItemBatchesSerializer(many=True) 
    class Meta:
        model = TC_InvoiceItems
        fields = ['id','ItemID','HSNCode','Quantity','UnitID','BaseUnitQuantity','QtyInKg','QtyInNo','QtyInBox','MRP','Rate','BasicAmount','TaxType','GSTPercentage','GSTAmount','Amount','DiscountType','Discount','DiscountAmount','CGST','SGST','IGST','CGSTPercentage','SGSTPercentage','IGSTPercentage','InvoiceItemBatches']   
        
class T_InvoiceSerializer(serializers.ModelSerializer):
    InvoiceItems = TC_InvoiceItemsSerializer(many=True)
    class Meta:
        model = T_Invoices
        fields = ['id','OrderID','InvoiceDate','CustomerID','InvoiceNumber','FullInvoiceNumber','CustomerGSTTin','GrandTotal','PartyID','RoundOffAmount','CreatedBy','CreatedOn','InvoiceItems']

    def create(self, validated_data):
        InvoiceItems_data = validated_data.pop('InvoiceItems')
        Invoice = T_Invoices.objects.create(**validated_data)
        for InvoiceItem_data in InvoiceItems_data:
            InvoiceItemBatches_data = InvoiceItem_data.pop('InvoiceItemBatches')
            InvoiceItemID =TC_InvoiceItems.objects.create(InvoiceID=Invoice, **InvoiceItem_data)
            for InvoiceItemBatch_data in InvoiceItemBatches_data:
               TC_InvoiceItemBatches.objects.create(InvoiceID=Invoice,InvoiceItemID=InvoiceItemID, **InvoiceItemBatch_data)
        
        return Invoice       
    
    def update(self, instance, validated_data):
        
        instance.OrderID = validated_data.get(
            'OrderID', instance.OrderID)
        instance.CustomerID = validated_data.get(
            'CustomerID', instance.CustomerID)
        instance.PartyID = validated_data.get(
            'PartyID', instance.PartyID)
        instance.GrandTotal = validated_data.get(
            'GrandTotal', instance.GrandTotal)
        instance.RoundOffAmount = validated_data.get(
            'RoundOffAmount', instance.RoundOffAmount)    
        instance.save()
        
        for items in instance.InvoiceItems.all():
            items.delete()
        
        for InvoiceItem_data in validated_data['InvoiceItems']:
            InvoiceItemBatches_data = InvoiceItem_data.pop('InvoiceItemBatches')
            TC_InvoiceItemsID = TC_InvoiceItems.objects.create(InvoiceID=instance, **InvoiceItem_data)
            for InvoiceItemBatch_data in InvoiceItemBatches_data:
               TC_InvoiceItemBatches.objects.create(InvoiceID=instance,InvoiceItemID=TC_InvoiceItemsID, **InvoiceItemBatch_data)
        return instance 