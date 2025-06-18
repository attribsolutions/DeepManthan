from decimal import Decimal, InvalidOperation
from ..models import *
from rest_framework import serializers

class FloatDecimalField(serializers.Field):
    def to_representation(self, value):
        return float(value)   

    
class B2BSerializer2(serializers.Serializer):
    # id = serializers.IntegerField()
    NoOfRecipients = serializers.IntegerField()
    NoOfInvoices  = serializers.IntegerField()
    TotalInvoiceValue =FloatDecimalField()
    
    def to_representation(self, obj):
        representation = super().to_representation(obj)
        representation ['No. Of Recipients'] = representation.pop('NoOfRecipients')
        representation ['No. Of Invoices'] = representation.pop('NoOfInvoices')
        representation ['Total Invoice Value'] = representation.pop('TotalInvoiceValue')
        return representation
    
    
class B2B3Serializer1(serializers.Serializer):
    # id = serializers.IntegerField()
    GSTIN_UINOfRecipient = serializers.CharField(max_length=100)
    ReceiverName = serializers.CharField(max_length=100)
    InvoiceNumber=serializers.CharField(max_length=100)
    InvoiceType=serializers.CharField(max_length=100)
    InvoiceDate=serializers.CharField(max_length=100)
    InvoiceValue=FloatDecimalField()
    PlaceOfSupply=serializers.CharField(max_length=100)
    ReverseCharge=serializers.CharField(max_length=100)
    ApplicableOfTaxRate=FloatDecimalField()
    TaxableValue=FloatDecimalField()
    IGST=FloatDecimalField()
    CGST=FloatDecimalField()
    SGST=FloatDecimalField()
    CessAmount=FloatDecimalField()
    IRN=serializers.CharField(max_length=100)
    IRNDate=serializers.CharField(max_length=100)
    

    def to_representation(self, obj):
        representation = super().to_representation(obj)
        representation ['GSTIN / UIN Of Recipient'] = representation.pop('GSTIN_UINOfRecipient')
        representation ['Receiver Name'] = representation.pop('ReceiverName')
        representation ['Invoice Number'] = representation.pop('InvoiceNumber')
        representation ['Invoice Type'] = representation.pop('InvoiceType')
        representation ['Invoice Date'] = representation.pop('InvoiceDate')
        representation ['Invoice Value (₹)'] = representation.pop('InvoiceValue')
        representation ['Place Of Supply'] = representation.pop('PlaceOfSupply')
        representation ['Reverse Charge'] = representation.pop('ReverseCharge')
        representation ['Applicable Of TaxRate'] = representation.pop('ApplicableOfTaxRate') 
        representation ['Taxable Value (₹)'] = representation.pop('TaxableValue')
        representation ['Integrated Tax (₹)'] = representation.pop('IGST')
        representation ['Central Tax(₹)'] = representation.pop('CGST')
        representation ['State Tax (₹)'] = representation.pop('SGST')
        representation ['Cess Amount'] = representation.pop('CessAmount')
        representation ['IRN'] = representation.pop('IRN')
        representation ['IRN Date'] = representation.pop('IRNDate')
        
        return representation
###########################################################################################################    
    

    
    
class B2CLSerializer2(serializers.Serializer):
    # id = serializers.IntegerField()
    NoOfInvoices  = serializers.IntegerField()
    TotalInvoiceValue =FloatDecimalField() 
    # TaxableValue =FloatDecimalField()  
    
    def to_representation(self, obj):
        representation = super().to_representation(obj)
        representation ['No. Of Invoices'] = representation.pop('NoOfInvoices')
        representation ['Total Invoice Value'] = representation.pop('TotalInvoiceValue')
        return representation
      
#################################################################################################################    

class B2CSSerializer(serializers.Serializer):
    # id = serializers.IntegerField()
    Type=serializers.CharField(max_length=100)
    PlaceOfSupply=serializers.CharField(max_length=100)
    ApplicableOfTaxRate=FloatDecimalField()
    InvoiceDate=serializers.CharField(max_length=100)
    InvoiceValue=FloatDecimalField()
    # ECommerceGSTIN=serializers.CharField(max_length=100)
    # Rate=FloatDecimalField()
    TaxableValue=serializers.IntegerField()
    IGST=FloatDecimalField()
    CGST=FloatDecimalField()
    SGST=FloatDecimalField()
    CessAmount=FloatDecimalField()    
    
    def to_representation(self, obj):
        representation = super().to_representation(obj)
        representation ['Type'] = representation.pop('Type')
        representation ['Place Of Supply'] = representation.pop('PlaceOfSupply')
        representation ['Invoice Date'] = representation.pop('InvoiceDate')
        representation ['Invoice Value'] = representation.pop('InvoiceValue')
        representation ['Applicable Of TaxRate %'] = representation.pop('ApplicableOfTaxRate')
        representation ['Taxable Value (₹)'] = representation.pop('TaxableValue')       
        # representation ['ECommerce GSTIN'] = representation.pop('ECommerceGSTIN')
        # representation ['Rate'] = representation.pop('Rate')       
        representation ['Integrated Tax (₹)'] = representation.pop('IGST')
        representation ['Central Tax(₹)'] = representation.pop('CGST')
        representation ['State Tax (₹)'] = representation.pop('SGST')
        representation ['Cess Amount'] = representation.pop('CessAmount')
        return representation
    
class B2CSSerializer2(serializers.Serializer):
    # id = serializers.IntegerField()
    TotalTaxableValue =FloatDecimalField() 
    TotalCess =FloatDecimalField() 
    
    def to_representation(self, obj):
        representation = super().to_representation(obj)
        representation ['Total Taxable Value'] = representation.pop('TotalTaxableValue')
        representation ['Total Cess'] = representation.pop('TotalCess')
        return representation 
    
################################################################################################################ 
    
class CDNRSerializer1(serializers.Serializer):
    # id = serializers.IntegerField()
    GSTIN_UINOfRecipient = serializers.CharField(max_length=100)
    ReceiverName = serializers.CharField(max_length=100)
    NoteNumber=serializers.CharField(max_length=100)
    NoteDate=serializers.CharField(max_length=100)
    NoteTypeName=serializers.CharField(max_length=100)    
    PlaceOfSupply=serializers.CharField(max_length=100)
    ReverseCharge=serializers.CharField(max_length=100)
    NoteValue =FloatDecimalField()    
    Rate=FloatDecimalField()
    TaxableValue=FloatDecimalField() 
    IGST=FloatDecimalField()
    CGST=FloatDecimalField()
    SGST=FloatDecimalField()
    CessAmount=FloatDecimalField()     
    IRN = serializers.CharField(max_length=500) 
    EINvoiceCreatedON=serializers.CharField(max_length=100)  
      
    def to_representation(self, obj):
        representation = super().to_representation(obj)
        representation ['GSTIN / UIN Of Recipient'] = representation.pop('GSTIN_UINOfRecipient')        
        representation ['Receiver Name'] = representation.pop('ReceiverName')
        representation ['Note Type'] = representation.pop('NoteTypeName')
        representation ['Note Number'] = representation.pop('NoteNumber')
        representation ['Note Date'] = representation.pop('NoteDate')
        representation ['Note Value'] = representation.pop('NoteValue')
        representation ['Place Of Supply'] = representation.pop('PlaceOfSupply')
        representation ['Reverse Charge'] = representation.pop('ReverseCharge')
        representation ['Rate'] = representation.pop('Rate')                
        representation ['Taxable Value'] = representation.pop('TaxableValue')
        representation ['Integrated Tax (₹)'] = representation.pop('IGST')
        representation ['Central Tax (₹)'] = representation.pop('CGST')
        representation ['State Tax (₹)'] = representation.pop('SGST')
        representation ['Cess Amount'] = representation.pop('CessAmount')
        representation['IRN'] = representation.pop('IRN')
        representation ['IRN Date'] = representation.pop('EINvoiceCreatedON')
        return representation 
     
    
class CDNRSerializer2(serializers.Serializer):
    # id = serializers.IntegerField()
    NoOfRecipients = serializers.IntegerField()
    NoOfNotes  = serializers.IntegerField()
    TotalInvoiceValue =FloatDecimalField()
    TotalTaxableValue =FloatDecimalField()
    TotalCess=FloatDecimalField() 
    
    def to_representation(self, obj):
        representation = super().to_representation(obj)
        representation ['No. Of Recipients'] = representation.pop('NoOfRecipients')
        representation ['No. Of Notes'] = representation.pop('NoOfNotes')
        representation ['Total Invoice Value'] = representation.pop('TotalInvoiceValue')
        representation ['Total Taxable Value'] = representation.pop('TotalTaxableValue')
        representation ['Total Cess'] = representation.pop('TotalCess')
        return representation 
    
    
#####################################################################################################################        
    
    
class CDNURSerializer(serializers.Serializer):
    # id = serializers.IntegerField()
    URType=serializers.CharField(max_length=100)
    NoteNumber=serializers.CharField(max_length=100)
    NoteDate=serializers.CharField(max_length=100)
    NoteType=serializers.CharField(max_length=100)
    PlaceOfSupply=serializers.CharField(max_length=100)
    NoteValue=FloatDecimalField()
    ApplicableOfTaxRate=FloatDecimalField() 
    Rate=FloatDecimalField()
    TaxableValue=FloatDecimalField()
    CessAmount=FloatDecimalField() 
    
        
    def to_representation(self, obj):
        representation = super().to_representation(obj)
        representation ['UR Type'] = representation.pop('URType')
        representation ['Note Number'] = representation.pop('NoteNumber')
        representation ['Note Date'] = representation.pop('NoteDate')
        representation ['Note Type'] = representation.pop('NoteType')
        representation ['Place Of Supply'] = representation.pop('PlaceOfSupply')
        representation ['Note Value'] = representation.pop('NoteValue')
        representation ['Applicable Of TaxRate'] = representation.pop('ApplicableOfTaxRate')
        representation ['Rate'] = representation.pop('Rate')
        representation ['Taxable Value'] = representation.pop('TaxableValue')
        representation ['Cess Amount'] = representation.pop('CessAmount')
        return representation
    

class CDNURSerializer2(serializers.Serializer):
   # id = serializers.IntegerField()
    NoOfNotes  = serializers.IntegerField()
    TotalNoteValue =FloatDecimalField()
    TotalTaxableValue =FloatDecimalField()
    TotalCess=FloatDecimalField()   
    
    def to_representation(self, obj):
        representation = super().to_representation(obj)
        representation ['No. Of Notes'] = representation.pop('NoOfNotes')
        representation ['Total Note Value'] = representation.pop('TotalNoteValue')
        representation ['Total Taxable Value'] = representation.pop('TotalTaxableValue')
        representation ['Total Cess'] = representation.pop('TotalCess')
        return representation 
    
################################################################################################################    
       
class EXEMPSerializer(serializers.Serializer):
    # id = serializers.IntegerField()
    Descriptionn=serializers.CharField(max_length=100)
    Total=FloatDecimalField()
    
    
    def to_representation(self, obj):
        representation = super().to_representation(obj)
        representation ['Description'] = representation.pop('Descriptionn')
        representation ['Nil Rated Supplies'] = representation.pop('Total')
        representation ['Exempted Other Than NilRated Non GST Supply'] = ''
        representation ['Non GST Supplies'] = ''
        return representation
    
    
class EXEMP2Serializer2(serializers.Serializer):
    # id = serializers.IntegerField()
    # AA=serializers.CharField(max_length=100)
    TotalNilRatedSupplies=FloatDecimalField()
    TotalExemptedSupplies=serializers.CharField(max_length=100)
    TotalNonGSTSupplies=serializers.CharField(max_length=100)
    
    def to_representation(self, obj):
        representation = super().to_representation(obj)
        representation ['Total Nil Rated Supplies'] = representation.pop('TotalNilRatedSupplies')
        representation ['Total Exempted Supplies'] = representation.pop('TotalExemptedSupplies')
        representation ['Total Non GST Supplies'] = representation.pop('TotalNonGSTSupplies')
        return representation
    
#######################################################################################################      

    
class HSNSerializer1(serializers.Serializer):    
    # HSN=serializers.IntegerField()
    HSN=serializers.CharField()
    # Description=serializers.CharField(max_length=100)
    UQC=serializers.CharField(max_length=100)
    TotalQuantity=FloatDecimalField()
    Rate=FloatDecimalField()
    TotalValue=FloatDecimalField()
    TaxableValue=FloatDecimalField()
    IntegratedTaxAmount=FloatDecimalField()
    CentralTaxAmount=FloatDecimalField()
    StateUTTaxAmount=FloatDecimalField()
    # CessAmount=serializers.CharField(max_length=100)
      
    def to_representation(self, obj):
        representation = super().to_representation(obj)
        representation ['HSN'] = representation.pop('HSN')
        # representation ['Description'] = representation.pop('Description')
        representation ['UQC'] = representation.pop('UQC')
        representation ['Total Quantity'] = representation.pop('TotalQuantity')
        representation ['Rate'] = representation.pop('Rate')
        representation ['Total Value'] = representation.pop('TotalValue')
        representation ['Taxable Value'] = representation.pop('TaxableValue')
        representation ['Integrated Tax Amount'] = representation.pop('IntegratedTaxAmount')
        representation ['Central Tax Amount'] = representation.pop('CentralTaxAmount')
        representation ['State UT Tax Amount'] = representation.pop('StateUTTaxAmount')
        # representation ['Cess Amount'] = representation.pop('CessAmount')
        return representation
    
class HSNSerializerWithDescription(HSNSerializer1):
    Description = serializers.CharField(max_length=100) 
    def to_representation(self, obj):
        representation = super().to_representation(obj)  
        representation['Description'] = getattr(obj, 'Description', '')  
        return representation
    
    
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
    
    def to_representation(self, obj):
        representation = super().to_representation(obj)
        representation ['No. Of HSN'] = representation.pop('NoOfHSN')
        representation ['Total Value'] = representation.pop('TotalValue')
        representation ['Total Taxable Value'] = representation.pop('TotalTaxableValue')
        representation ['Total Integrated Tax Amount'] = representation.pop('TotalIntegratedTaxAmount')
        representation ['Total Central Tax Amount'] = representation.pop('TotalCentralTaxAmount')
        representation ['Total State UT Tax Amount'] = representation.pop('TotalStateUTTaxAmount')
        representation ['Total Cess Amount'] = representation.pop('TotalCessAmount')
        return representation   
    
#######################################################################################################    
    
class DocsSerializer(serializers.Serializer):
    # id = serializers.IntegerField()
    NatureOfDocument=serializers.CharField(max_length=100)
    Sr_No_From=serializers.CharField()
    Sr_No_To=serializers.CharField()
    TotalNumber=FloatDecimalField()
    Cancelled=FloatDecimalField()
    
    def to_representation(self, obj):
        representation = super().to_representation(obj)
        representation ['Nature Of Document'] = representation.pop('NatureOfDocument')
        representation ['Sr. No. From'] = representation.pop('Sr_No_From')
        representation ['Sr. No. To'] = representation.pop('Sr_No_To')
        representation ['Total Number'] = representation.pop('TotalNumber')
        representation ['Cancelled'] = representation.pop('Cancelled')
        return representation
  
class Docs2Serializer2(serializers.Serializer):
    # id = serializers.IntegerField()
    # AA=serializers.CharField(max_length=100)
    # bb=serializers.CharField(max_length=100)
    # cc=serializers.CharField(max_length=100)
    TotalNumbers=serializers.IntegerField()
    TotalCancelled=serializers.IntegerField()
    
    def to_representation(self, obj):
        representation = super().to_representation(obj)
        representation ['Total Numbers'] = representation.pop('TotalNumbers')
        representation ['Total Cancelled'] = representation.pop('TotalCancelled')
        return representation


   