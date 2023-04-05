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
    
