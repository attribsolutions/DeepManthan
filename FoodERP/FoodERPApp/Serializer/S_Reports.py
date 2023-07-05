
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
    TotalTCS=serializers.DecimalField(max_digits=10, decimal_places=2)
    DebitNote=  serializers.DecimalField(max_digits=10, decimal_places=2)
    CreditNote =  serializers.DecimalField(max_digits=10, decimal_places=2)
    InvoiceAmount = serializers.DecimalField(max_digits=10, decimal_places=2)
    ReceiptAmt =  serializers.DecimalField(max_digits=10, decimal_places=2)
    CashReceiptAmt =  serializers.DecimalField(max_digits=10, decimal_places=2)
    Flag = serializers.IntegerField()
    BasicAmount=  serializers.DecimalField(max_digits=10, decimal_places=2)
    BA5=  serializers.DecimalField(max_digits=10, decimal_places=2)
    BA12=  serializers.DecimalField(max_digits=10, decimal_places=2)
    BA18=  serializers.DecimalField(max_digits=10, decimal_places=2)
    GA5=  serializers.DecimalField(max_digits=10, decimal_places=2)
    GA12=  serializers.DecimalField(max_digits=10, decimal_places=2)
    GA18=  serializers.DecimalField(max_digits=10, decimal_places=2)