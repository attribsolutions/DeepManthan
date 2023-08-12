from ..models import *
from rest_framework import serializers


class B2BSerializer(serializers.Serializer):
    # id = serializers.IntegerField()
    GSTIN = serializers.CharField(max_length=100)
    Name = serializers.CharField(max_length=100)
    FullInvoiceNumber=serializers.CharField(max_length=100)
    InvoiceDate=serializers.CharField(max_length=100)
    GrandTotal=serializers.DecimalField(max_digits=15, decimal_places=2)
    aa=serializers.CharField(max_length=100)
    ReverseCharge=serializers.CharField(max_length=100)
    ApplicableofTaxRate=serializers.CharField(max_length=100)
    InvoiceType=serializers.CharField(max_length=100)
    ECommerceGSTIN=serializers.CharField(max_length=100)
    Rate=serializers.DecimalField(max_digits=15, decimal_places=2)
    TaxableValue=serializers.DecimalField(max_digits=15, decimal_places=2)
    CessAmount=serializers.DecimalField(max_digits=15, decimal_places=2)
    
    
class B2CLSerializer(serializers.Serializer):
    # id = serializers.IntegerField()
    FullInvoiceNumber=serializers.CharField(max_length=100)
    InvoiceDate=serializers.CharField(max_length=100)
    GrandTotal=serializers.DecimalField(max_digits=15, decimal_places=2)
    aa=serializers.CharField(max_length=100)
    ApplicableofTaxRate=serializers.CharField(max_length=100)
    ECommerceGSTIN=serializers.CharField(max_length=100)
    Rate=serializers.DecimalField(max_digits=15, decimal_places=2)
    TaxableValue=serializers.DecimalField(max_digits=15, decimal_places=2)
    CessAmount=serializers.DecimalField(max_digits=15, decimal_places=2)  
    
class B2CSSerializer(serializers.Serializer):
    # id = serializers.IntegerField()
    Type=serializers.CharField(max_length=100)
    aa=serializers.CharField(max_length=100)
    ApplicableofTaxRate=serializers.CharField(max_length=100)
    ECommerceGSTIN=serializers.CharField(max_length=100)
    Rate=serializers.DecimalField(max_digits=15, decimal_places=2)
    TaxableValue=serializers.DecimalField(max_digits=15, decimal_places=2)
    CessAmount=serializers.DecimalField(max_digits=15, decimal_places=2)        
    
        