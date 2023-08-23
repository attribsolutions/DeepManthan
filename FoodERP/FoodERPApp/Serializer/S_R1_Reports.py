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
    
class B2BSerializer2(serializers.Serializer):
    # id = serializers.IntegerField()
    NoofRecipients = serializers.IntegerField()
    NoOfInvoices  = serializers.IntegerField()
    TotalInvoiceValue =FloatDecimalField()

###########################################################################################################    
    
class B2CLSerializer(serializers.Serializer):
    # id = serializers.IntegerField()
    FullInvoiceNumber=serializers.CharField(max_length=100)
    InvoiceDate=serializers.CharField(max_length=100)
    GrandTotal=FloatDecimalField()
    aa=serializers.CharField(max_length=100)
    ApplicableofTaxRate=serializers.CharField(max_length=100)
    ECommerceGSTIN=serializers.CharField(max_length=100)
    Rate=FloatDecimalField()
    TaxableValue=FloatDecimalField()
    CessAmount=FloatDecimalField()
    
    
class B2CLSerializer2(serializers.Serializer):
    # id = serializers.IntegerField()
    NoOfInvoices  = serializers.IntegerField()
    TotalInvoiceValue =FloatDecimalField() 
    TaxableValue =FloatDecimalField()  
      
#################################################################################################################    

class B2CSSerializer(serializers.Serializer):
    # id = serializers.IntegerField()
    Type=serializers.CharField(max_length=100)
    aa=serializers.CharField(max_length=100)
    ApplicableofTaxRate=serializers.CharField(max_length=100)
    ECommerceGSTIN=serializers.CharField(max_length=100)
    Rate=FloatDecimalField()
    TaxableValue=FloatDecimalField()
    CessAmount=FloatDecimalField()
    
class B2CSSerializer2(serializers.Serializer):
    # id = serializers.IntegerField()
    TaxableValue =FloatDecimalField() 
    CessAmount=serializers.CharField(max_length=100)   
    
################################################################################################################    

class CDNRSerializer(serializers.Serializer):
    # id = serializers.IntegerField()
    GSTIN = serializers.CharField(max_length=100)
    Name = serializers.CharField(max_length=100)
    FullNoteNumber=serializers.CharField(max_length=100)
    CRDRNoteDate=serializers.CharField(max_length=100)
    NoteTypeName=serializers.CharField(max_length=100)
    NoteType_id=serializers.IntegerField()
    aa=serializers.CharField(max_length=100)
    ReverseCharge=serializers.CharField(max_length=100)
    NoteSupplyType=serializers.CharField(max_length=100)
    GrandTotal=FloatDecimalField()
    ApplicableofTaxRate=serializers.CharField(max_length=100)
    Rate=FloatDecimalField()
    TaxableValue=FloatDecimalField()
    CessAmount=serializers.CharField(max_length=100)
    
class CDNRSerializer2(serializers.Serializer):
    # id = serializers.IntegerField()
    NoofRecipients = serializers.IntegerField()
    NoOfNotes  = serializers.IntegerField()
    TotalInvoiceValue =FloatDecimalField()
    TotalTaxableValue =FloatDecimalField()
    CessAmount=serializers.IntegerField()
    
    
#####################################################################################################################        
    
    
class CDNURSerializer(serializers.Serializer):
    # id = serializers.IntegerField()
    URType=serializers.CharField(max_length=100)
    FullNoteNumber=serializers.CharField(max_length=100)
    CRDRNoteDate=serializers.CharField(max_length=100)
    NoteType=serializers.CharField(max_length=100)
    aa=serializers.CharField(max_length=100)
    GrandTotal=FloatDecimalField()
    ApplicableofTaxRate=serializers.CharField(max_length=100)
    Rate=FloatDecimalField()
    TaxableValue=FloatDecimalField()
    CessAmount=serializers.CharField(max_length=100)
    

class CDNURSerializer2(serializers.Serializer):
   # id = serializers.IntegerField()
    NoOfNotes  = serializers.IntegerField()
    TotalInvoiceValue =FloatDecimalField()
    TotalTaxableValue =FloatDecimalField()
    CessAmount=serializers.IntegerField()   
    
################################################################################################################    
       
class EXEMPSerializer(serializers.Serializer):
    # id = serializers.IntegerField()
    Description=serializers.CharField(max_length=100)
    Total=FloatDecimalField()
    
    
class EXEMP2Serializer2(serializers.Serializer):
    # id = serializers.IntegerField()
    AA=serializers.CharField(max_length=100)
    TotalNilRatedSupplies=FloatDecimalField()
    TotalExemptedSupplies=serializers.CharField(max_length=100)
    TotalNonGSTSupplies=serializers.CharField(max_length=100)
    
#######################################################################################################    
    
class HSNSerializer(serializers.Serializer):
    # id = serializers.IntegerField()
    HSNCode=serializers.CharField(max_length=100)
    Description=serializers.CharField(max_length=100)
    UQC=serializers.CharField(max_length=100)
    TotalQuantity=FloatDecimalField()
    TotalValue=FloatDecimalField()
    TaxableValue=FloatDecimalField()
    IntegratedTaxAmount=FloatDecimalField()
    CentralTaxAmount=FloatDecimalField()
    StateUTTaxAmount=FloatDecimalField()
    CessAmount=serializers.CharField(max_length=100)
    
    
class HSN2Serializer2(serializers.Serializer):
    # id = serializers.IntegerField()
    NoofHSN=serializers.CharField(max_length=100)
    a=serializers.CharField(max_length=100)
    b=serializers.CharField(max_length=100)
    c=serializers.CharField(max_length=100)
    TotalValue=FloatDecimalField()
    TaxableValue=FloatDecimalField()
    IntegratedTaxAmount=FloatDecimalField()
    CentralTaxAmount=FloatDecimalField()
    StateUTTaxAmount=FloatDecimalField()
    CessAmount=serializers.CharField(max_length=100)    
    
#######################################################################################################    
    
class DocsSerializer(serializers.Serializer):
    # id = serializers.IntegerField()
    a=serializers.CharField(max_length=100)
    MINID=serializers.IntegerField()
    MAXID=serializers.IntegerField()
    cnt=FloatDecimalField()
    Cancelledcnt=FloatDecimalField()



class Docs2Serializer2(serializers.Serializer):
    # id = serializers.IntegerField()
    AA=serializers.CharField(max_length=100)
    bb=serializers.CharField(max_length=100)
    cc=serializers.CharField(max_length=100)
    cnt=serializers.IntegerField()
    Cancelledcnt=serializers.IntegerField()
   
     
    

   