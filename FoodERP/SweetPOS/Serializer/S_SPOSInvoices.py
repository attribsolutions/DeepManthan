from ..models import *
from rest_framework import serializers
from datetime import datetime, timedelta


class SPOSInvoiceItemsSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = TC_SPOSInvoiceItems
        fields = [ 'InvoiceDate','SaleItemID', 'ClientID', 'ClientSaleItemID', 'ClientSaleID', 'ERPItemID', 'POSItemID', 'Quantity', 'BaseUnitQuantity', 'MRPValue', 'Rate', 'BasicAmount', 'TaxType', 'GSTPercentage', 'GSTAmount', 'Amount', 'DiscountType', 'Discount', 'DiscountAmount', 'CGST', 'SGST', 'IGST', 'CGSTPercentage', 'SGSTPercentage', 'IGSTPercentage', 'BatchDate', 'BatchCode', 'Item', 'Unit', 'QtyInNo', 'QtyInKg', 'QtyInBox','Party','HSNCode','IsMixItem','MixItemId']

class SPOSInvoicesReferencesSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = TC_SPOSInvoicesReferences
        fields = ['Order'] 
    


class SPOSInvoiceSerializer(serializers.ModelSerializer):
    SaleItems = SPOSInvoiceItemsSerializer(many=True)
    SPOSInvoicesReferences = SPOSInvoicesReferencesSerializer(many=True)
    
    class Meta:
        model = T_SPOSInvoices
        fields = '__all__'

    def create(self, validated_data):
        
        InvoiceItems_data = validated_data.pop('SaleItems')
        InvoicesReferences_data = validated_data.pop('SPOSInvoicesReferences')
        
        
        InvoiceID = T_SPOSInvoices.objects.create(**validated_data)
        
        for InvoiceItem_data in InvoiceItems_data:
            
            InvoiceItemID =TC_SPOSInvoiceItems.objects.create(Invoice=InvoiceID, **InvoiceItem_data)
            
        for InvoicesReference_data in InvoicesReferences_data:
          
            InvoicesReferences = TC_SPOSInvoicesReferences.objects.create(Invoice=InvoiceID, **InvoicesReference_data)
            
        
        return InvoiceID   
    
    

class SaleItemSerializer(serializers.Serializer):    
    id= serializers.IntegerField()     
    Item = serializers.IntegerField()
    ItemName = serializers.CharField(max_length=200)
    TotalAmount = serializers.DecimalField(max_digits=20, decimal_places=2)
    TotalQuantity = serializers.DecimalField(max_digits=20, decimal_places=3)
    UnitName = serializers.CharField(max_length=200)


class MobileSerializer(serializers.ModelSerializer):

    class Meta:
        model = M_ConsumerMobile
        fields = '__all__'
        
        
class SPOSInvoiceEditSerializer(serializers.Serializer):
    id=serializers.IntegerField()
    Rate=serializers.DecimalField(max_digits=10, decimal_places=2)
    MRP=serializers.DecimalField(max_digits=10, decimal_places=2)
    BaseUnitQuantity=serializers.DecimalField(max_digits=10, decimal_places=2)
    GST = serializers.DecimalField(max_digits=10, decimal_places=2)

class SPOSInvoiceEditItemSerializer(serializers.Serializer):
    id=serializers.IntegerField()
    Item=serializers.IntegerField()
    ItemName=serializers.CharField(max_length=100)
    MIUnitID = serializers.IntegerField() 
    Quantity=serializers.DecimalField(max_digits=10, decimal_places=2)
    MRPValue=serializers.DecimalField(max_digits=10, decimal_places=2)
    Rate=serializers.DecimalField(max_digits=10, decimal_places=2)
    Unit=serializers.IntegerField() 
    UnitName=serializers.CharField(max_length=100)
    MCUnitsUnitID=serializers.IntegerField() 
    ConversionUnit =serializers.DecimalField(max_digits=10, decimal_places=2) 
    BaseUnitQuantity=serializers.DecimalField(max_digits=10, decimal_places=2)
    HSNCode = serializers.CharField(max_length=100)
    GSTPercentage=serializers.DecimalField(max_digits=10, decimal_places=2)
    BasicAmount=serializers.DecimalField(max_digits=10, decimal_places=2)
    GSTAmount=serializers.DecimalField(max_digits=10, decimal_places=2)
    CGST=serializers.DecimalField(max_digits=10, decimal_places=2)
    SGST=serializers.DecimalField(max_digits=10, decimal_places=2)
    IGST=serializers.DecimalField(max_digits=10, decimal_places=2)
    CGSTPercentage=serializers.DecimalField(max_digits=10, decimal_places=2)
    SGSTPercentage=serializers.DecimalField(max_digits=10, decimal_places=2)
    IGSTPercentage=serializers.DecimalField(max_digits=10, decimal_places=2)
    Amount=serializers.DecimalField(max_digits=10, decimal_places=2) 
    DiscountType = serializers.IntegerField() 
    Discount = serializers.DecimalField(max_digits=20, decimal_places=2)
    DiscountAmount = serializers.DecimalField(max_digits=20, decimal_places=2)


