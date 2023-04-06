from ..models import *
from rest_framework import serializers

class ReceiptInvoiceserializer(serializers.Serializer):
   
    Receipt_id=serializers.IntegerField()
    Invoice_ID=serializers.IntegerField()
    InvoiceDate = serializers.DateField()
    FullInvoiceNumber=serializers.CharField(max_length=100)
    GrandTotal=serializers.DecimalField(max_digits=10, decimal_places=2)  
    PaidAmount=serializers.DecimalField(max_digits=10, decimal_places=2)  
    BalAmt=serializers.DecimalField(max_digits=10, decimal_places=2)  
    

class ReceiptInvoiceSerializer(serializers.ModelSerializer):
    class Meta :
        model= TC_ReceiptInvoices
        fields = '__all__'

class ReceiptSerializer(serializers.ModelSerializer):
    ReceiptInvoices = ReceiptInvoiceSerializer(many=True)
    class Meta :
        model= T_Receipts
        fields = '__all__'


class GeneralMasterserializer(serializers.ModelSerializer):
    class Meta:
        model = M_GeneralMaster
        fields = '__all__'

class PartiesSerializer(serializers.ModelSerializer):
   
    class Meta:
        model = M_Parties
        fields = ['id','Name','GSTIN','PAN','Email']        
        
class ReceiptSerializerSecond(serializers.ModelSerializer):
    Customer = PartiesSerializer(read_only=True)
    Party = PartiesSerializer(read_only=True)
    ReceiptMode = GeneralMasterserializer(read_only=True)
    ReceiptInvoices = ReceiptInvoiceSerializer(many=True)
    
    class Meta:
        model = T_Receipts
        fields = '__all__'        