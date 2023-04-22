from rest_framework import serializers
from ..models import *
from ..Serializer.S_GeneralMaster import  *
from ..Serializer.S_Parties import  *
from ..Serializer.S_Receipts import  *
from ..Serializer.S_Invoices import  *
from ..Serializer.S_PurchaseReturn import *

# Credit Or Debit Save Serializer 

class CreditDebitNoteInvoiceSerializer(serializers.ModelSerializer):
    class Meta :
        model= TC_ReceiptInvoices
        fields = '__all__'

class CreditDebitNoteItemSerializer(serializers.ModelSerializer):
    
    class Meta :
        model= TC_CreditDebitNoteItems
        fields = ['CRDRNote','Item','Quantity','Unit','BaseUnitQuantity','MRP','Rate','BasicAmount','TaxType','GST','GSTAmount','Amount','CGST','SGST','IGST','CGSTPercentage','SGSTPercentage','IGSTPercentage','BatchDate','BatchCode','LiveBatch']

class CreditDebitNoteSerializer(serializers.ModelSerializer):
    CRDRInvoices = CreditDebitNoteInvoiceSerializer(many=True)
    CRDRNoteItems = CreditDebitNoteItemSerializer(many=True)
    class Meta :
        model= T_CreditDebitNotes
        fields = ['CRDRNoteDate', 'NoteNo', 'FullNoteNumber', 'NoteReason', 'GrandTotal', 'RoundOffAmount', 'Narration', 'Comment', 'CreatedBy', 'UpdatedBy', 'Customer', 'Invoice', 'NoteType', 'Party', 'PurchaseReturn', 'Receipt','CRDRNoteItems','CRDRInvoices']
        
    def create(self, validated_data):
        CRDRNoteItems_data = validated_data.pop('CRDRNoteItems')
        CRDRInvoices_data = validated_data.pop('CRDRInvoices')
        
        CreditDebitNoteID = T_CreditDebitNotes.objects.create(**validated_data)
        
        for CRDRNoteItem_data in CRDRNoteItems_data:
            CRDRNoteItem =TC_CreditDebitNoteItems.objects.create(CRDRNote=CreditDebitNoteID, **CRDRNoteItem_data)
       
        for CRDRInvoice_data in CRDRInvoices_data:
            CRDRInvoice =TC_ReceiptInvoices.objects.create(CRDRNote=CreditDebitNoteID, **CRDRInvoice_data)    
            
        return CreditDebitNoteID 
    
    
    
# CreditDebitNote List Serializer             
        
class CreditDebitNoteSecondSerializer(serializers.ModelSerializer):
    Customer = PartiesSerializer(read_only=True)
    Party = PartiesSerializer(read_only=True)
    NoteReason = GeneralMasterserializer(read_only=True)
    NoteType = GeneralMasterserializer(read_only=True)
    Receipt = ReceiptSerializer(read_only=True)
    Invoice = InvoiceSerializer(read_only=True)
    PurchaseReturn = PurchaseReturnSerializer(read_only=True)
    class Meta :
        model= T_CreditDebitNotes
        fields = '__all__'
                
    def to_representation(self, instance):
        # get representation from ModelSerializer
        ret = super(CreditDebitNoteSecondSerializer, self).to_representation(instance)
        # if parent is None, overwrite
        if not ret.get("NoteReason", None):
            ret["NoteReason"] = {"id": None, "Name": None}
        
        if not ret.get("NoteType", None):
            ret["NoteType"] = {"id": None, "Name": None}
        
        if not ret.get("Receipt", None):
            ret["Receipt"] = {"id": None, "FullReceiptNumber": None}  
        
        if not ret.get("Invoice", None):
            ret["Invoice"] = {"id": None, "FullInvoiceNumber": None} 
            
        if not ret.get("PurchaseReturn", None):
            ret["PurchaseReturn"] = {"id": None, "FullReturnNumber": None}         
                  
        return ret    
    
    
# CreditDebitNote Single get Serializer        
    
class SingleCreditDebitNoteThirdSerializer(serializers.ModelSerializer):
    Customer = PartiesSerializer(read_only=True)
    Party = PartiesSerializer(read_only=True)
    NoteReason = GeneralMasterserializer(read_only=True)
    NoteType = GeneralMasterserializer(read_only=True)
    Receipt = ReceiptSerializer(read_only=True)
    Invoice = InvoiceSerializer(read_only=True)
    PurchaseReturn = PurchaseReturnSerializer(read_only=True)
    class Meta :
        model= T_CreditDebitNotes
        fields = '__all__'
                
    def to_representation(self, instance):
        # get representation from ModelSerializer
        ret = super(SingleCreditDebitNoteThirdSerializer, self).to_representation(instance)
        # if parent is None, overwrite
        if not ret.get("NoteReason", None):
            ret["NoteReason"] = {"id": None, "Name": None}
        
        if not ret.get("NoteType", None):
            ret["NoteType"] = {"id": None, "Name": None}
        
        if not ret.get("Receipt", None):
            ret["Receipt"] = {"id": None, "FullReceiptNumber": None}  
        
        if not ret.get("Invoice", None):
            ret["Invoice"] = {"id": None, "FullInvoiceNumber": None} 
            
        if not ret.get("PurchaseReturn", None):
            ret["PurchaseReturn"] = {"id": None, "FullReturnNumber": None}         
                  
        return ret