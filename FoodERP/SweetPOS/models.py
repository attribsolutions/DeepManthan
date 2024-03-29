from django.db import models


# Create your models here.
class M_SweetPOSRoleAccess(models.Model):
    
    CreatedBy = models.IntegerField()
    CreatedOn = models.DateTimeField(auto_now_add=True)
    UpdatedBy = models.IntegerField()
    UpdatedOn = models.DateTimeField(auto_now=True)
    DivisionID = models.IntegerField()
    DivName =  models.CharField(max_length=500)
    Party = models.IntegerField()
    IsAddNewItem = models.BooleanField(default=False)
    IsImportItems = models.BooleanField(default=False)
    IsImportGroups = models.BooleanField(default=False)
    IsUpdateItem = models.BooleanField(default=False)
    IsCItemId = models.BooleanField(default=False)
    IsItemName = models.BooleanField(default=False)
    IsSalesModify = models.BooleanField(default=False)
    IsSalesDelete = models.BooleanField(default=False)
    IsUnitModify = models.BooleanField(default=False)
    TopRows = models.IntegerField()
    Query = models.CharField(max_length=500, blank=True)
    IsShowVoucherButton = models.BooleanField(default=False)
    IsGiveSweetPOSUpdate = models.BooleanField(default=False)
    IsSweetPOSAutoUpdate = models.BooleanField(default=False)
    IsSweetPOSServiceAutoUpdate = models.BooleanField(default=False)
    TouchSaleHistoryRows = models.IntegerField()
    LicenseValidTill =  models.DateField()
    IsEWayBillUploadExist = models.BooleanField(default=False)      
        
    class Meta:
        db_table = "M_SweetPOSRoleAccess"       
        
        
    
class M_SweetPOSLogin(models.Model):
        UserName=models.CharField(max_length=50)
        DivisionID=models.IntegerField()
        ClientID=models.IntegerField()  
        MacID   =models.CharField(max_length=200)
        ExePath=models.CharField(max_length=200)  
        ExeVersion=models.CharField(max_length=30)
        CreatedOn=models.DateTimeField(auto_now_add=True)
        
        class Meta:
            db_table="M_SweetPOSLogin"
        
    
class T_SPOSInvoices(models.Model):
    SaleID  = models.IntegerField()
    ClientID = models.IntegerField()
    ClientSaleID = models.IntegerField()
    InvoiceDate = models.DateField()
    InvoiceNumber = models.IntegerField()
    FullInvoiceNumber = models.CharField(max_length=500)
    GrandTotal = models.DecimalField(max_digits=20, decimal_places=2)
    RoundOffAmount = models.DecimalField(max_digits=15, decimal_places=2)
    CreatedBy = models.IntegerField()
    CreatedOn = models.DateTimeField(auto_now_add=True)
    UpdatedBy = models.IntegerField()
    UpdatedOn = models.DateTimeField(auto_now=True)
    Customer = models.IntegerField()
    Driver = models.IntegerField()
    Party = models.IntegerField()
    Vehicle = models.IntegerField()
    TCSAmount = models.DecimalField(max_digits=20, decimal_places=2)
    DiscountPercentage = models.DecimalField(max_digits=20, decimal_places=2,blank=True, null=True)
    DiscountAmount = models.DecimalField(max_digits=20, decimal_places=2,blank=True, null=True)
    
    # Hide Flag is temporary 
    Hide = models.BooleanField(default=False)
    ImportFromExcel= models.BooleanField(default=False)
    DeletedFromSAP = models.BooleanField(default=False)
    class Meta:
        db_table = "T_SPOSInvoices"


class TC_SPOSInvoiceItems(models.Model):
    SaleItemID = models.IntegerField()
    ClientID = models.IntegerField()
    ClientSaleItemID = models.IntegerField()
    ClientSaleID = models.IntegerField()
    ERPItemID = models.IntegerField()
    POSItemID = models.IntegerField()
    Quantity = models.DecimalField(max_digits=20, decimal_places=3)
    BaseUnitQuantity = models.DecimalField(max_digits=20, decimal_places=3)
    MRPValue =  models.DecimalField(max_digits=20, decimal_places=2,null=True,blank=True)
    Rate = models.DecimalField(max_digits=20, decimal_places=2)
    BasicAmount = models.DecimalField(max_digits=20, decimal_places=2)
    TaxType = models.CharField(max_length=500)
    GSTPercentage = models.DecimalField(max_digits=20, decimal_places=2)
    GSTAmount = models.DecimalField(max_digits=20, decimal_places=2)
    Amount = models.DecimalField(max_digits=20, decimal_places=2)
    DiscountType = models.CharField(max_length=500,blank=True, null=True)
    Discount = models.DecimalField(max_digits=20, decimal_places=2,blank=True, null=True)
    DiscountAmount = models.DecimalField(max_digits=20, decimal_places=2,blank=True, null=True)
    CGST = models.DecimalField(max_digits=20, decimal_places=2)
    SGST = models.DecimalField(max_digits=20, decimal_places=2)
    IGST = models.DecimalField(max_digits=20, decimal_places=2)
    CGSTPercentage = models.DecimalField(max_digits=20, decimal_places=2)
    SGSTPercentage = models.DecimalField(max_digits=20, decimal_places=2)
    IGSTPercentage = models.DecimalField(max_digits=20, decimal_places=2)
    BatchDate = models.DateField(blank=True, null=True)
    BatchCode = models.CharField(max_length=500)
    CreatedOn = models.DateTimeField(auto_now_add=True)
    # GST = models.ForeignKey(M_GSTHSNCode, related_name='InvoiceItemGST',null=True,on_delete=models.PROTECT)
    Invoice = models.ForeignKey(T_SPOSInvoices, related_name='SaleItems', on_delete=models.CASCADE)
    Item = models.IntegerField()
    # LiveBatch=models.ForeignKey(O_LiveBatches, on_delete=models.PROTECT,null=True,blank=True)
    # MRP = models.ForeignKey(M_MRPMaster, related_name='InvoiceItemMRP', on_delete=models.PROTECT,null=True,blank=True)
    Unit = models.IntegerField()
    QtyInNo = models.DecimalField(max_digits=30, decimal_places=20)
    QtyInKg = models.DecimalField(max_digits=30, decimal_places=20)
    QtyInBox = models.DecimalField(max_digits=30, decimal_places=20)

    class Meta:
        db_table = "TC_SPOSInvoiceItems"    