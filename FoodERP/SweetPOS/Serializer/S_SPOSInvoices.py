from ..models import *
from rest_framework import serializers



class SPOSInvoiceItemsSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = TC_SPOSInvoiceItems
        fields = [ 'InvoiceDate','SaleItemID', 'ClientID', 'ClientSaleItemID', 'ClientSaleID', 'ERPItemID', 'POSItemID', 'Quantity', 'BaseUnitQuantity', 'MRPValue', 'Rate', 'BasicAmount', 'TaxType', 'GSTPercentage', 'GSTAmount', 'Amount', 'DiscountType', 'Discount', 'DiscountAmount', 'CGST', 'SGST', 'IGST', 'CGSTPercentage', 'SGSTPercentage', 'IGSTPercentage', 'BatchDate', 'BatchCode', 'Item', 'Unit', 'QtyInNo', 'QtyInKg', 'QtyInBox','Party','HSNCode']



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
    
    

class SaleItemSerializer(serializers.Serializer):    
    id= serializers.IntegerField()     
    Item = serializers.IntegerField()
    ItemName = serializers.CharField(max_length=200)
    TotalAmount = serializers.DecimalField(max_digits=20, decimal_places=2)
    TotalQuantity = serializers.DecimalField(max_digits=20, decimal_places=3)
    UnitName = serializers.CharField(max_length=200)

