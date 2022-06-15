from dataclasses import fields
import json
from ..models import *
from rest_framework import serializers


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
        model = T_Invoice
        fields = ['id','OrderID','InvoiceDate','CustomerID','InvoiceNumber','FullInvoiceNumber','CustomerGSTTin','GrandTotal','PartyID','RoundOffAmount','CreatedBy','CreatedOn','InvoiceItems']

    def create(self, validated_data):
        InvoiceItems_data = validated_data.pop('InvoiceItems')
        Invoice = T_Invoice.objects.create(**validated_data)
        for InvoiceItem_data in InvoiceItems_data:
            InvoiceItemBatches_data = InvoiceItem_data.pop('InvoiceItemBatches')
            InvoiceItemID =TC_InvoiceItems.objects.create(InvoiceID=Invoice, **InvoiceItem_data)
            for InvoiceItemBatch_data in InvoiceItemBatches_data:
               TC_InvoiceItemBatches.objects.create(InvoiceID=Invoice,InvoiceItemID=InvoiceItemID, **InvoiceItemBatch_data)
        
        return Invoice       