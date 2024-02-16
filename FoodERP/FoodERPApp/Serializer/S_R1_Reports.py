from decimal import Decimal, InvalidOperation
from ..models import *
from rest_framework import serializers

class FloatDecimalField(serializers.Field):
    def to_representation(self, value):
        return float(value)
    
class B2BSerializer(serializers.Serializer):
    # id = serializers.IntegerField()
    GSTIN_UINOfRecipient = serializers.CharField(max_length=100)
    ReceiverName = serializers.CharField(max_length=100)
    InvoiceNumber=serializers.CharField(max_length=100)
    InvoiceDate=serializers.CharField(max_length=100)
    InvoiceValue=FloatDecimalField()
    PlaceOfSupply=serializers.CharField(max_length=100)
    ReverseCharge=serializers.CharField(max_length=100)
    ApplicableOfTaxRate=serializers.CharField(max_length=100)
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
    InvoiceNumber=serializers.CharField(max_length=100)
    InvoiceDate=serializers.CharField(max_length=100)
    InvoiceValue=FloatDecimalField()
    PlaceOfSupply=serializers.CharField(max_length=100)
    ApplicableOfTaxRate=serializers.CharField(max_length=100)
    ECommerceGSTIN=serializers.CharField(max_length=100)
    Rate=FloatDecimalField()
    TaxableValue=FloatDecimalField()
    CessAmount=FloatDecimalField()
    
    
class B2CLSerializer2(serializers.Serializer):
    # id = serializers.IntegerField()
    NoOfInvoices  = serializers.IntegerField()
    TotalInvoiceValue =FloatDecimalField() 
    # TaxableValue =FloatDecimalField()  
      
#################################################################################################################    

class B2CSSerializer(serializers.Serializer):
    # id = serializers.IntegerField()
    Type=serializers.CharField(max_length=100)
    PlaceOfSupply=serializers.CharField(max_length=100)
    ApplicableOfTaxRate=serializers.CharField(max_length=100)
    ECommerceGSTIN=serializers.CharField(max_length=100)
    Rate=FloatDecimalField()
    TaxableValue=FloatDecimalField()
    CessAmount=FloatDecimalField()
    
class B2CSSerializer2(serializers.Serializer):
    # id = serializers.IntegerField()
    TotalTaxableValue =FloatDecimalField() 
    TotalCess =serializers.CharField(max_length=100)   
    
################################################################################################################    

class CDNRSerializer(serializers.Serializer):
    # id = serializers.IntegerField()
    GSTIN_UINOfRecipient = serializers.CharField(max_length=100)
    ReceiverName = serializers.CharField(max_length=100)
    NoteNumber=serializers.CharField(max_length=100)
    NoteDate=serializers.CharField(max_length=100)
    NoteTypeName=serializers.CharField(max_length=100)
    # NoteType_id=serializers.IntegerField()
    PlaceOfSupply=serializers.CharField(max_length=100)
    ReverseCharge=serializers.CharField(max_length=100)
    NoteValue =serializers.CharField(max_length=100)
    # GrandTotal=FloatDecimalField()
    ApplicableOfTaxRate=serializers.CharField(max_length=100)
    Rate=FloatDecimalField()
    TaxableValue=FloatDecimalField()
    CessAmount=serializers.CharField(max_length=100)
    
class CDNRSerializer2(serializers.Serializer):
    # id = serializers.IntegerField()
    NoOfRecipients = serializers.IntegerField()
    NoOfNotes  = serializers.IntegerField()
    TotalInvoiceValue =FloatDecimalField()
    TotalTaxableValue =FloatDecimalField()
    TotalCess=serializers.IntegerField()
    
    
#####################################################################################################################        
    
    
class CDNURSerializer(serializers.Serializer):
    # id = serializers.IntegerField()
    URType=serializers.CharField(max_length=100)
    NoteNumber=serializers.CharField(max_length=100)
    NoteDate=serializers.CharField(max_length=100)
    NoteType=serializers.CharField(max_length=100)
    PlaceOfSupply=serializers.CharField(max_length=100)
    NoteValue=FloatDecimalField()
    ApplicableOfTaxRate=serializers.CharField(max_length=100)
    Rate=FloatDecimalField()
    TaxableValue=FloatDecimalField()
    CessAmount=serializers.CharField(max_length=100)
    

class CDNURSerializer2(serializers.Serializer):
   # id = serializers.IntegerField()
    NoOfNotes  = serializers.IntegerField()
    TotalNoteValue =FloatDecimalField()
    TotalTaxableValue =FloatDecimalField()
    TotalCess=serializers.IntegerField()   
    
################################################################################################################    
       
class EXEMPSerializer(serializers.Serializer):
    # id = serializers.IntegerField()
    Description=serializers.CharField(max_length=100)
    NilRatedSupplies=FloatDecimalField()
    Exempted_OtherThanNilRatedNonGSTSupply=serializers.CharField(max_length=100)
    NonGSTSupplies=serializers.CharField(max_length=100)
    # Total=FloatDecimalField()
    
    
class EXEMP2Serializer2(serializers.Serializer):
    # id = serializers.IntegerField()
    # AA=serializers.CharField(max_length=100)
    TotalNilRatedSupplies=FloatDecimalField()
    TotalExemptedSupplies=serializers.CharField(max_length=100)
    TotalNonGSTSupplies=serializers.CharField(max_length=100)
    
#######################################################################################################    
    
class HSNSerializer(serializers.Serializer):
    # id = serializers.IntegerField()
    HSN=serializers.CharField(max_length=100)
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
    NoOfHSN=serializers.CharField(max_length=100)
    # a=serializers.CharField(max_length=100)
    # b=serializers.CharField(max_length=100)
    # c=serializers.CharField(max_length=100)
    TotalValue=FloatDecimalField()
    TotalTaxableValue=FloatDecimalField()
    TotalIntegratedTaxAmount=FloatDecimalField()
    TotalCentralTaxAmount=FloatDecimalField()
    TotalStateUTTaxAmount=FloatDecimalField()
    TotalCessAmount=serializers.CharField(max_length=100)    
    
#######################################################################################################    
    
class DocsSerializer(serializers.Serializer):
    # id = serializers.IntegerField()
    NatureOfDocument=serializers.CharField(max_length=100)
    Sr_No_From=serializers.CharField()
    Sr_No_To=serializers.CharField()
    TotalNumber=FloatDecimalField()
    Cancelled=FloatDecimalField()



class Docs2Serializer2(serializers.Serializer):
    # id = serializers.IntegerField()
    # AA=serializers.CharField(max_length=100)
    # bb=serializers.CharField(max_length=100)
    # cc=serializers.CharField(max_length=100)
    TotalNumbers=serializers.IntegerField()
    TotalCancelled=serializers.IntegerField()
   
     
    

   