from ..models import *
from rest_framework import serializers



class SPOSInvoiceItemsSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = TC_SPOSInvoiceItems
        fields = [ 'SaleItemID', 'ClientID', 'ClientSaleItemID', 'ClientSaleID', 'ERPItemID', 'POSItemID', 'Quantity', 'BaseUnitQuantity', 'MRPValue', 'Rate', 'BasicAmount', 'TaxType', 'GSTPercentage', 'GSTAmount', 'Amount', 'DiscountType', 'Discount', 'DiscountAmount', 'CGST', 'SGST', 'IGST', 'CGSTPercentage', 'SGSTPercentage', 'IGSTPercentage', 'BatchDate', 'BatchCode', 'Item', 'Unit', 'QtyInNo', 'QtyInKg', 'QtyInBox']



class SPOSInvoiceSerializer(serializers.ModelSerializer):
    SaleItems = SPOSInvoiceItemsSerializer(many=True)
    
    class Meta:
        model = T_SPOSInvoices
        fields = '__all__'

    def create(self, validated_data):
        
        InvoiceItems_data = validated_data.pop('SaleItems')
        
        InvoiceID = T_SPOSInvoices.objects.create(**validated_data)
        
        for InvoiceItem_data in InvoiceItems_data:
            
            InvoiceItemID =TC_SPOSInvoiceItems.objects.create(Invoice=InvoiceID, **InvoiceItem_data)
            
        
        return InvoiceID   
