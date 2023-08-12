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
    
    
class CDNRSerializer(serializers.Serializer):
    # id = serializers.IntegerField()
    GSTIN = serializers.CharField(max_length=100)
    Name = serializers.CharField(max_length=100)
    FullNoteNumber=serializers.CharField(max_length=100)
    CRDRNoteDate=serializers.CharField(max_length=100)
    NoteType=serializers.CharField(max_length=100)
    aa=serializers.CharField(max_length=100)
    ReverseCharge=serializers.CharField(max_length=100)
    NoteSupplyType=serializers.CharField(max_length=100)
    GrandTotal=serializers.DecimalField(max_digits=15, decimal_places=2)
    ApplicableofTaxRate=serializers.CharField(max_length=100)
    Rate=serializers.DecimalField(max_digits=15, decimal_places=2)
    TaxableValue=serializers.DecimalField(max_digits=15, decimal_places=2)
    CessAmount=serializers.DecimalField(max_digits=15, decimal_places=2)    
    
    
class CDNURSerializer(serializers.Serializer):
    # id = serializers.IntegerField()
    URType=serializers.CharField(max_length=100)
    FullNoteNumber=serializers.CharField(max_length=100)
    CRDRNoteDate=serializers.CharField(max_length=100)
    NoteType=serializers.CharField(max_length=100)
    aa=serializers.CharField(max_length=100)
    GrandTotal=serializers.DecimalField(max_digits=15, decimal_places=2)
    ApplicableofTaxRate=serializers.CharField(max_length=100)
    Rate=serializers.DecimalField(max_digits=15, decimal_places=2)
    TaxableValue=serializers.DecimalField(max_digits=15, decimal_places=2)
    CessAmount=serializers.DecimalField(max_digits=15, decimal_places=2) 
    
    
class EXEMPSerializer(serializers.Serializer):
    # id = serializers.IntegerField()
    Description=serializers.CharField(max_length=100)
    Value=serializers.CharField(max_length=100)
    
    
    
class HSNSerializer(serializers.Serializer):
    # id = serializers.IntegerField()
    HSNCode=serializers.CharField(max_length=100)
    Description=serializers.CharField(max_length=100)
    UQC=serializers.CharField(max_length=100)
    TotalQuantity=serializers.DecimalField(max_digits=15, decimal_places=2)
    TotalValue=serializers.DecimalField(max_digits=15, decimal_places=2)
    TaxableValue=serializers.DecimalField(max_digits=15, decimal_places=2)
    IntegratedTaxAmount=serializers.DecimalField(max_digits=15, decimal_places=2)
    CentralTaxAmount=serializers.DecimalField(max_digits=15, decimal_places=2)
    StateUTTaxAmount=serializers.DecimalField(max_digits=15, decimal_places=2)
    CessAmount=serializers.CharField(max_length=100)
    
    
class DocsSerializer(serializers.Serializer):
    # id = serializers.IntegerField()
    a=serializers.CharField(max_length=100)
    MINID=serializers.CharField(max_length=100)
    MAXID=serializers.CharField(max_length=100)
    cnt=serializers.CharField(max_length=100)
    Cancelledcnt=serializers.CharField(max_length=100)
   