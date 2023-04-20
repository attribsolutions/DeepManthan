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
        fields = '__all__'

class CreditDebitNoteSerializer(serializers.ModelSerializer):
    CRDRInvoices = CreditDebitNoteInvoiceSerializer(many=True)
    CRDRNoteItems = CreditDebitNoteItemSerializer(many=True)
    class Meta :
        model= T_CreditDebitNotes
        fields = '__all__'      
        
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