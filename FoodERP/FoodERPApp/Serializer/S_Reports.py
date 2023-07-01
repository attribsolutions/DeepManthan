
from rest_framework import serializers
from ..Serializer.S_Pages import *
from ..Serializer.S_Modules import *
from ..models import *


class PartyLedgerReportSerializer(serializers.Serializer):
    
    id = serializers.IntegerField()
    InvoiceDate=serializers.DateField()
    BillNo = serializers.CharField(max_length=500)
    BankName=serializers.CharField(max_length=500)
    BranchName = serializers.CharField(max_length=500)
    DocumentNo = serializers.CharField(max_length=500)
    ReceiptMode = serializers.CharField(max_length=500)
    InvoiceAmount = serializers.DecimalField(max_digits=10, decimal_places=2)
    ReceiptAmt =  serializers.DecimalField(max_digits=10, decimal_places=2)
    CashReceiptAmt =  serializers.DecimalField(max_digits=10, decimal_places=2)
    Flag = serializers.IntegerField()
    
    
    