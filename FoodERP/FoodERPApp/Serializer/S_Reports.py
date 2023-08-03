
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
    Description = serializers.CharField(max_length=500)
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


class StockProcessingReportSerializer(serializers.Serializer):
    
    id = serializers.IntegerField()
    ItemID=serializers.IntegerField()
    UnitID=serializers.IntegerField()
    OpeningBalance=serializers.DecimalField(max_digits=10, decimal_places=3)
    GRN=serializers.DecimalField(max_digits=10, decimal_places=3)
    SalesReturn = serializers.DecimalField(max_digits=10, decimal_places=3)
    Sale = serializers.DecimalField(max_digits=10, decimal_places=3)
    PurchaseReturn = serializers.DecimalField(max_digits=10, decimal_places=3)
    ClosingBalance=serializers.DecimalField(max_digits=10, decimal_places=3)
    

class StockReportSerializer(serializers.Serializer):
    
    
    Item_id=serializers.IntegerField()
    Unit_id=serializers.IntegerField()
    UnitName=serializers.CharField(max_length=500)
    OpeningBalance=serializers.DecimalField(max_digits=10, decimal_places=3)
    GRNInward=serializers.DecimalField(max_digits=10, decimal_places=3)
    SalesReturn = serializers.DecimalField(max_digits=10, decimal_places=3)
    Sale = serializers.DecimalField(max_digits=10, decimal_places=3)
    PurchaseReturn = serializers.DecimalField(max_digits=10, decimal_places=3)
    ClosingBalance=serializers.DecimalField(max_digits=10, decimal_places=3)
    ActualStock=serializers.DecimalField(max_digits=10, decimal_places=3)
    ItemName = serializers.CharField(max_length=500)
    GroupTypeName = serializers.CharField(max_length=500)
    GroupName = serializers.CharField(max_length=500)
    SubGroupName = serializers.CharField(max_length=500)
    
    
class PurchaseGSTRateWiseReportSerializer(serializers.Serializer):
    
    GSTPercentage = serializers.DecimalField(max_digits=10, decimal_places=2)
    TaxableValue = serializers.DecimalField(max_digits=20, decimal_places=2)
    CGST = serializers.DecimalField(max_digits=10, decimal_places=2)
    SGST = serializers.DecimalField(max_digits=10, decimal_places=2)
    IGST= serializers.DecimalField(max_digits=10, decimal_places=2)
    GSTAmount=serializers.DecimalField(max_digits=10, decimal_places=2)
    TotalValue=serializers.DecimalField(max_digits=10, decimal_places=2)
   
       
class PurchaseGSTReportSerializer(serializers.Serializer):
    
    Name = serializers.CharField(max_length=500)
    FullGRNNumber=serializers.CharField(max_length=500)
    InvoiceNumber=serializers.CharField(max_length=500)
    GRNDate = serializers.DateField()
    GSTRate = serializers.DecimalField(max_digits=10, decimal_places=2)
    TaxableValue = serializers.DecimalField(max_digits=10, decimal_places=2)
    CGST = serializers.DecimalField(max_digits=10, decimal_places=2)
    SGST = serializers.DecimalField(max_digits=10, decimal_places=2)
    IGST= serializers.DecimalField(max_digits=10, decimal_places=2)
    GSTAmount=serializers.DecimalField(max_digits=10, decimal_places=2)
    DiscountAmount =serializers.DecimalField(max_digits=10, decimal_places=2)
    TotalValue=serializers.DecimalField(max_digits=10, decimal_places=2)
    
    
    
class InvoiceDataExportSerializer(serializers.Serializer):
    
    PartyID=serializers.IntegerField()
    PartyName = serializers.CharField(max_length=500)
    FullInvoiceNumber=serializers.CharField(max_length=500)
    InvoiceDate = serializers.DateField()
    CustomerID=serializers.IntegerField()
    CustomerName = serializers.CharField(max_length=500)
    ItemID=serializers.IntegerField()
    ItemName=serializers.CharField(max_length=100)
    CompanyName=serializers.CharField(max_length=100)
    HSNCode=serializers.CharField(max_length=100)
    MRP=serializers.DecimalField(max_digits=10, decimal_places=2)
    QtyInNo = models.DecimalField(max_digits=30, decimal_places=20)
    QtyInKg = models.DecimalField(max_digits=30, decimal_places=20)
    QtyInBox = models.DecimalField(max_digits=30, decimal_places=20)
    BasicRate=serializers.DecimalField(max_digits=10, decimal_places=2)
    WithGSTRate=serializers.DecimalField(max_digits=10, decimal_places=2)  
    UnitName=serializers.CharField(max_length=100)
    DiscountType=serializers.IntegerField()
    Discount = serializers.DecimalField(max_digits=20, decimal_places=2)
    DiscountAmount = serializers.DecimalField(max_digits=20, decimal_places=2)
    TaxableValue = serializers.DecimalField(max_digits=10, decimal_places=2)
    CGST = serializers.DecimalField(max_digits=10, decimal_places=2)
    CGSTPercentage=serializers.DecimalField(max_digits=10, decimal_places=2)
    SGST = serializers.DecimalField(max_digits=10, decimal_places=2)
    SGSTPercentage=serializers.DecimalField(max_digits=10, decimal_places=2)
    IGST= serializers.DecimalField(max_digits=10, decimal_places=2)
    IGSTPercentage=serializers.DecimalField(max_digits=10, decimal_places=2)
    GSTPercentage=serializers.DecimalField(max_digits=10, decimal_places=2)
    GSTAmount=serializers.DecimalField(max_digits=10, decimal_places=2)
    TotalValue = serializers.DecimalField(max_digits=10, decimal_places=2) 
    FullOrderNumber = serializers.CharField(max_length=500)
    OrderDate= serializers.DateField()
    TCSAmount = serializers.DecimalField(max_digits=10, decimal_places=2)
    RoundOffAmount = serializers.DecimalField(max_digits=10, decimal_places=2)
    GrandTotal = serializers.DecimalField(max_digits=10, decimal_places=2) 
    RouteName = serializers.CharField(max_length=500)
    StateName = serializers.CharField(max_length=500)
    GSTIN = serializers.CharField(max_length=500)
   
class DamageStocktSerializer(serializers.Serializer):
    ItemName = serializers.CharField(max_length=500) 
    Qty = serializers.DecimalField(max_digits=10, decimal_places=2)
    UnitName = serializers.CharField(max_length=500) 
     
   
    

    
   