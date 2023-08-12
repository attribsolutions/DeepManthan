from decimal import Decimal, InvalidOperation
from ..models import *
from rest_framework import serializers

class FloatDecimalField(serializers.Field):
    def to_representation(self, value):
        return float(value)
    
    
class B2BSerializer(serializers.Serializer):
    # id = serializers.IntegerField()
    GSTIN = serializers.CharField(max_length=100)
    Name = serializers.CharField(max_length=100)
    FullInvoiceNumber=serializers.CharField(max_length=100)
    InvoiceDate=serializers.CharField(max_length=100)
    GrandTotal=FloatDecimalField()
    aa=serializers.CharField(max_length=100)
    ReverseCharge=serializers.CharField(max_length=100)
    ApplicableofTaxRate=serializers.CharField(max_length=100)
    InvoiceType=serializers.CharField(max_length=100)
    ECommerceGSTIN=serializers.CharField(max_length=100)
    Rate=FloatDecimalField()
    TaxableValue=FloatDecimalField()
    CessAmount=FloatDecimalField()