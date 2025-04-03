
from rest_framework import serializers
from ..Serializer.S_Pages import *
from ..Serializer.S_Modules import *
from ..models import *
from decimal import Decimal

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
    ActualStock=serializers.DecimalField(max_digits=10, decimal_places=3)
    StockAdjustment=serializers.DecimalField(max_digits=10, decimal_places=3)
    Production=serializers.DecimalField(max_digits=10, decimal_places=3)
    

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
    StockAdjustment=serializers.DecimalField(max_digits=10, decimal_places=3)
    Production =serializers.DecimalField(max_digits=10, decimal_places=3)
    
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
    InvoiceNumber=serializers.CharField(max_length=500)
    FullInvoiceNumber=serializers.CharField(max_length=500)
    InvoiceDate = serializers.DateField()
    GSTRate = serializers.DecimalField(max_digits=10, decimal_places=2)
    GSTPercentage = serializers.DecimalField(max_digits=10, decimal_places=2)
    TaxableValue = serializers.DecimalField(max_digits=10, decimal_places=2)
    CGST = serializers.DecimalField(max_digits=10, decimal_places=2)
    SGST = serializers.DecimalField(max_digits=10, decimal_places=2)
    IGST= serializers.DecimalField(max_digits=10, decimal_places=2)
    GSTAmount=serializers.DecimalField(max_digits=10, decimal_places=2)
    DiscountAmount =serializers.DecimalField(max_digits=10, decimal_places=2)
    TotalValue=serializers.DecimalField(max_digits=10, decimal_places=2)
    
    
    
class InvoiceDataExportSerializer(serializers.Serializer):
    
    SupplierID=serializers.IntegerField()
    SupplierName = serializers.CharField(max_length=500)
    InvoiceNumber=serializers.CharField(max_length=500)
    InvoiceDate = serializers.DateField()
    CustomerID=serializers.IntegerField()
    CustomerName = serializers.CharField(max_length=500)
    FE2MaterialID=serializers.IntegerField()
    MaterialName=serializers.CharField(max_length=100)
    CompanyName=serializers.CharField(max_length=100)
    HSNCode=serializers.CharField(max_length=100)
    MRP=serializers.DecimalField(max_digits=10, decimal_places=2)
    QtyInNo = serializers.DecimalField(max_digits=30, decimal_places=20)
    QtyInKg = serializers.DecimalField(max_digits=30, decimal_places=20)
    QtyInBox = serializers.DecimalField(max_digits=30, decimal_places=20)
    BasicRate=serializers.DecimalField(max_digits=10, decimal_places=2)
    WithGSTRate=serializers.DecimalField(max_digits=10, decimal_places=2)  
    UnitName=serializers.CharField(max_length=100)
    DiscountType=serializers.CharField(max_length=100)
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
    TCSAmount = serializers.DecimalField(max_digits=10, decimal_places=2)
    RoundOffAmount = serializers.DecimalField(max_digits=10, decimal_places=2)
    GrandTotal = serializers.DecimalField(max_digits=10, decimal_places=2) 
    RouteName = serializers.CharField(max_length=500)
    StateName = serializers.CharField(max_length=500)
    GSTIN = serializers.CharField(max_length=500)
    Irn = serializers.CharField(max_length=500)
    AckNo = serializers.CharField(max_length=500)
    EwayBillNo = serializers.CharField(max_length=500)
    GroupName = serializers.CharField(max_length=500)
    SubGroupName = serializers.CharField(max_length=500)
    def to_representation(self, instance):
        a = super().to_representation(instance)
        Discount_Type = a['DiscountType']
        if Discount_Type == '1':
            a['DiscountType'] = 'Rs'
        elif Discount_Type == '2':
            a['DiscountType'] = '%'

        return a

   

    
class DamageStocktSerializer(serializers.Serializer):
    id=serializers.IntegerField()
    ItemName = serializers.CharField(max_length=500) 
    Qty = serializers.DecimalField(max_digits=10, decimal_places=2)
    UnitID=serializers.IntegerField()
    MRPValue = serializers.DecimalField(max_digits=10, decimal_places=2)       
    
    
    
class GenericSaleReportSerializer(serializers.Serializer):
    
    SAPPartyID=serializers.CharField(max_length=500)
    PartyID=serializers.IntegerField()
    PartyName = serializers.CharField(max_length=500)
    PartyType = serializers.CharField(max_length=500)
    ImportFromExcel = serializers.BooleanField()
    FullInvoiceNumber=serializers.CharField(max_length=500)
    InvoiceDate = serializers.DateField()
    CustomerID=serializers.IntegerField()
    CustomerName = serializers.CharField(max_length=500)
    CustomeType = serializers.CharField(max_length=500)
    ItemID=serializers.IntegerField()
    ItemName=serializers.CharField(max_length=100)
    CompanyName=serializers.CharField(max_length=100)
    HSNCode=serializers.CharField(max_length=100)
    MRP=serializers.DecimalField(max_digits=10, decimal_places=2)
    QtyInNo = serializers.DecimalField(max_digits=20, decimal_places=6)
    QtyInKg = serializers.DecimalField(max_digits=20, decimal_places=6)
    QtyInBox = serializers.DecimalField(max_digits=20, decimal_places=6)
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
    Group = serializers.CharField(max_length=500)
    SubGroup = serializers.CharField(max_length=500) 
    Cluster = serializers.CharField(max_length=500)
    SubCluster = serializers.CharField(max_length=500)
    BatchNo = serializers.CharField(max_length=500)
    BatchDate = serializers.DateField()
    SAPItemID = serializers.CharField(max_length=500)
    VoucherCode = serializers.CharField(max_length=500)
    CashierName = serializers.CharField(max_length=500)
     
    def to_representation(self, instance):
        # Ensure proper rounding for specific fields
        representation = super().to_representation(instance)
        representation['QtyInNo'] = Decimal(representation['QtyInNo']).quantize(Decimal('0.00'))
        representation['QtyInKg'] = Decimal(representation['QtyInKg']).quantize(Decimal('0.00'))
        representation['QtyInBox'] = Decimal(representation['QtyInBox']).quantize(Decimal('0.00'))
        representation ['Data Upload / FE2 Billing'] = "Data Upload" if representation['ImportFromExcel'] else "FE2 Billing"
        return representation
     
     
class RetailerDataExportSerializer(serializers.Serializer):
    
    id=serializers.IntegerField()
    SupplierName=serializers.CharField(max_length=500)
    Name = serializers.CharField(max_length=500)
    isActive=serializers.BooleanField()
    PartyCreation = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')
    Email = serializers.CharField(max_length=200)
    MobileNo=serializers.CharField()
    AlternateContactNo=serializers.CharField(max_length=500)
    Address=serializers.CharField(max_length=100)
    PIN=serializers.CharField(max_length=100)
    FSSAINo=serializers.CharField(max_length=100)
    FSSAIExipry=serializers.CharField(max_length=100)
    GSTIN = serializers.CharField(max_length=500) 
    PAN = serializers.CharField(max_length=500)
    StateName = serializers.CharField(max_length=500)
    DistrictName = serializers.CharField(max_length=500)
    CityName = serializers.CharField(max_length=500)
    Routeid =serializers.IntegerField()
    RouteName = serializers.CharField(max_length=500)
    CompanyName=serializers.CharField(max_length=100) 
    PartyTypeName=serializers.CharField(max_length=100) 
    PriceListName=serializers.CharField(max_length=100)
    Latitude=serializers.CharField(max_length=100)
    Longitude=serializers.CharField(max_length=100)
    SAPPartyCode = serializers.CharField(max_length=500)
    Supplierid = serializers.CharField(max_length=500)
    Cluster = serializers.CharField(max_length=500)
    SubCluster = serializers.CharField(max_length=500)
    
    
    
class ReturnReportSerializer(serializers.Serializer):
    id=serializers.IntegerField()
    ReturnDate = serializers.DateField()
    CustomerName = serializers.CharField(max_length=500)
    CustomerType = serializers.CharField(max_length=500)
    CompanyName=serializers.CharField(max_length=100)
    Product =serializers.CharField(max_length=100)
    SubProduct =serializers.CharField(max_length=100)

    ERPItemCode =  serializers.IntegerField()  
    SAPItemCode = serializers.IntegerField()

    MaterialName=serializers.CharField(max_length=100)
    ReturnQtyNos =serializers.DecimalField(max_digits=20, decimal_places=2)
    MRPValue=serializers.DecimalField(max_digits=10, decimal_places=2)
    Rate=serializers.DecimalField(max_digits=10, decimal_places=2)
    BasicAmount=serializers.DecimalField(max_digits=14, decimal_places=2)
    GSTPercentage=serializers.DecimalField(max_digits=10, decimal_places=2)
    GSTAmount=serializers.DecimalField(max_digits=14, decimal_places=2)
    Amount=serializers.DecimalField(max_digits=14, decimal_places=2)
    DiscountType=serializers.CharField(max_length=100)
    Discount = serializers.DecimalField(max_digits=20, decimal_places=2)
    DiscountAmount = serializers.DecimalField(max_digits=20, decimal_places=2)
    BatchDate = serializers.DateField()
    BatchCode = serializers.CharField(max_length=500)
    ReasonForReturn = serializers.CharField(max_length=500)
    ApprovedQuantityInNo=serializers.DecimalField(max_digits=14, decimal_places=2)
    Address = serializers.CharField(max_length=500)
    PIN = serializers.CharField(max_length=500)
    RouteName = serializers.CharField(max_length=500)
    SupplierName = serializers.CharField(max_length=500)
    SupplierType = serializers.CharField(max_length=500)
    FullReturnNumber = serializers.CharField(max_length=500)
    ApprovedByCompany=serializers.DecimalField(max_digits=20, decimal_places=2)
    FinalApprovalDate=serializers.DateField()
    ApprovedRate=serializers.DecimalField(max_digits=20, decimal_places=2)
    ApprovedBasicAmount=serializers.DecimalField(max_digits=20, decimal_places=2)
    ApprovedGSTPercentage=serializers.DecimalField(max_digits=20, decimal_places=2)
    ApprovedCGST=serializers.DecimalField(max_digits=20, decimal_places=2)
    ApprovedIGST=serializers.DecimalField(max_digits=20, decimal_places=2)
    ApprovedSGST=serializers.DecimalField(max_digits=20, decimal_places=2)
    ApprovedCGSTPercentage=serializers.DecimalField(max_digits=20, decimal_places=2)
    ApprovedSGSTPercentage=serializers.DecimalField(max_digits=20, decimal_places=2)
    ApprovedIGSTPercentage=serializers.DecimalField(max_digits=20, decimal_places=2)
    ApprovedGSTAmount=serializers.DecimalField(max_digits=20, decimal_places=2)
    ApprovedAmount=serializers.DecimalField(max_digits=20, decimal_places=2)
    ApprovedDiscountAmount=serializers.DecimalField(max_digits=20, decimal_places=2)
    
    def to_representation(self, instance):
        a = super().to_representation(instance)
        Discount_Type = a['DiscountType']
        if Discount_Type == '1':
            a['DiscountType'] = 'Rs'
        elif Discount_Type == '2':
            a['DiscountType'] = '%'

        return a  


class MaterialRegisterSerializerView(serializers.Serializer):
    # id=serializers.IntegerField()
    Sequence=serializers.IntegerField()
    TransactionDate = serializers.DateField()
    CreatedOn = serializers.DateTimeField()
    TransactionNumber = serializers.CharField(max_length=500)
    Name = serializers.CharField(max_length=500)
    QtyInBox=serializers.DecimalField(max_digits=10, decimal_places=2)
    QtyInKg =serializers.DecimalField(max_digits=10, decimal_places=2)
    QtyInNo =serializers.DecimalField(max_digits=10, decimal_places=2)
    
    
    
    
class CreditDebitDataExportSerializer(serializers.Serializer):
    
    SupplierID=serializers.IntegerField()
    SupplierName = serializers.CharField(max_length=500)
    InvoiceNumber=serializers.CharField(max_length=500)
    InvoiceDate = serializers.DateField()
    Narration = serializers.CharField(max_length=500) 
    NoteTypeName = serializers.CharField(max_length=500)
    NoteReasonName = serializers.CharField(max_length=500)
    CustomerID=serializers.IntegerField()
    CustomerName = serializers.CharField(max_length=500)
    FE2MaterialID=serializers.IntegerField()
    MaterialName=serializers.CharField(max_length=100)
    CompanyName=serializers.CharField(max_length=100)
    HSNCode=serializers.CharField(max_length=100)
    MRPValue=serializers.DecimalField(max_digits=10, decimal_places=2)
    QtyInNo = serializers.DecimalField(max_digits=30, decimal_places=20)
    QtyInKg = serializers.DecimalField(max_digits=30, decimal_places=20)
    QtyInBox = serializers.DecimalField(max_digits=30, decimal_places=20)
    BasicRate=serializers.DecimalField(max_digits=10, decimal_places=2)
    WithGSTRate=serializers.DecimalField(max_digits=10, decimal_places=2)  
    UnitName=serializers.CharField(max_length=100)
    DiscountType=serializers.CharField(max_length=100)
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
    # TCSAmount = serializers.DecimalField(max_digits=10, decimal_places=2)
    RoundOffAmount = serializers.DecimalField(max_digits=10, decimal_places=2)
    GrandTotal = serializers.DecimalField(max_digits=10, decimal_places=2) 
    RouteName = serializers.CharField(max_length=500)
    StateName = serializers.CharField(max_length=500)
    GSTIN = serializers.CharField(max_length=500)
    Irn = serializers.CharField(max_length=500)
    AckNo = serializers.CharField(max_length=500)
    EwayBillNo = serializers.CharField(max_length=500)
    

    def to_representation(self, instance):
        a = super().to_representation(instance)
        Discount_Type = a['DiscountType']
        if Discount_Type == '1':
            a['DiscountType'] = 'Rs'
        elif Discount_Type == '2':
            a['DiscountType'] = '%'

        return a    
    
class ReceiptDataExportSerializer(serializers.Serializer):
    id=serializers.IntegerField()
    SupplierID=serializers.IntegerField()
    SupplierName = serializers.CharField(max_length=500)
    ReceiptNumber=serializers.CharField(max_length=500)
    ReceiptDate = serializers.DateField()
    CustomerID=serializers.IntegerField()
    CustomerName = serializers.CharField(max_length=500)
    ReceiptTypeName=serializers.CharField(max_length=100)
    ReceiptModeName=serializers.CharField(max_length=100)
    BankName=serializers.CharField(max_length=100)
    DepositorBankName=serializers.CharField(max_length=100)
    AmountPaid=serializers.DecimalField(max_digits=10, decimal_places=2)
    Description = serializers.CharField(max_length=500)
    ChequeDate = serializers.DateField()
    DocumentNo = serializers.CharField(max_length=500)


class BalanceSerializer(serializers.Serializer):
    id= serializers.IntegerField()
    PartyName = serializers.CharField(max_length=500)
    RouteName = serializers.CharField(max_length=500)

class ManPowerSerializer(serializers.Serializer):
    SAPCode = serializers.CharField(max_length=500)
    FEParty_id = serializers.IntegerField(allow_null=True)
    PartyName = serializers.CharField(max_length=500)
    PartyActive = serializers.BooleanField(default=True)
    PartyCreation = serializers.DateTimeField()
    PartyType = serializers.CharField(max_length=500)
    Email = serializers.CharField(max_length=500)
    PAN = serializers.CharField(max_length=500)
    SS_id = serializers.IntegerField(allow_null=True)
    SSName = serializers.CharField(max_length=500)
    LoginID = serializers.CharField(max_length=500)
    country = serializers.CharField(max_length=500)
    Cluster = serializers.CharField(max_length=500)
    SubCluster = serializers.CharField(max_length=500)
    Address = serializers.CharField(max_length=500)
    State = serializers.CharField(max_length=500)
    District = serializers.CharField(max_length=500)
    City = serializers.CharField(max_length=500)
    PIN = serializers.IntegerField(allow_null=True)
    Mobile = serializers.CharField(max_length=500)
    OwnerName = serializers.CharField(max_length=500)
    Latitude = serializers.CharField(max_length=500)
    Longitude = serializers.CharField(max_length=500)
    FSSAINo = serializers.CharField(max_length=500)
    FSSAIExpiry = serializers.DateField()
    GSTIN = serializers.CharField(max_length=500)
    GM = serializers.CharField(max_length=500)
    NSM =  serializers.CharField(max_length=500)
    RSM =  serializers.CharField(max_length=500)
    ASM = serializers.CharField(max_length=500)
    SE = serializers.CharField(max_length=500)
    SO = serializers.CharField(max_length=500)
    SR = serializers.CharField(max_length=500)
    MT =  serializers.CharField(max_length=500)
    fssaidocument = serializers.CharField(max_length=500)
    

class TCSAmountReportSerializer(serializers.Serializer):
    InvoiceDate = serializers.DateField()
    InvoiceNumber = serializers.IntegerField()
    GrandTotal = serializers.DecimalField(max_digits=20, decimal_places=2)
    TCSTaxAmount = serializers.DecimalField(max_digits=20, decimal_places=2)
    Total = serializers.DecimalField(max_digits=20, decimal_places=2)
    PartyID = serializers.IntegerField()
    PartyName = serializers.CharField(max_length=500)



