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
    RoundOffAmount = models.DecimalField(max_digits=20, decimal_places=2)
    CreatedBy = models.IntegerField()
    CreatedOn = models.DateTimeField(auto_now_add=False)
    UpdatedBy = models.IntegerField()
    UpdatedOn = models.DateTimeField(auto_now=False)
    Customer = models.IntegerField()
    Driver = models.IntegerField(null=True)
    Party = models.IntegerField()
    Vehicle = models.IntegerField(null=True)
    TCSAmount = models.DecimalField(max_digits=20, decimal_places=2)
    DiscountPercentage = models.DecimalField(max_digits=20, decimal_places=2,blank=True, null=True)
    DiscountAmount = models.DecimalField(max_digits=20, decimal_places=2,blank=True, null=True) #Discount amount of all items
    PaymentType = models.CharField(max_length=500)
    TotalAmount = models.DecimalField(max_digits=20, decimal_places=2)  #All Items total without discount
    NetAmount = models.DecimalField(max_digits=20, decimal_places=2)    #TotalAmount+(-DiscountAmount)
    MobileNo  = models.CharField(max_length=15, blank=True, null=True)
    CustomerGSTIN = models.CharField(max_length=20, blank=True, null=True)
    # Hide Flag is temporary 
    Hide = models.BooleanField(default=False)
    # ImportFromExcel= models.BooleanField(default=False)
    # DeletedFromSAP = models.BooleanField(default=False)
    UploadedOn = models.DateTimeField(auto_now=True)
    Description = models.CharField(max_length=500,null=True,blank=True)
    IsDeleted = models.BooleanField(default=False)
    ReferenceInvoiceID = models.IntegerField(null=True,blank=True)
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
    TaxType = models.CharField(max_length=10)
    GSTPercentage = models.DecimalField(max_digits=20, decimal_places=2)
    GSTAmount = models.DecimalField(max_digits=20, decimal_places=2)
    Amount = models.DecimalField(max_digits=20, decimal_places=2)
    DiscountType = models.CharField(max_length=10,blank=True, null=True)
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
    HSNCode = models.CharField(max_length=20)
    InvoiceDate = models.DateField()
    Party = models.IntegerField()

    class Meta:
        db_table = "TC_SPOSInvoiceItems"    


class M_SweetPOSUser(models.Model):
    CompanyID=models.IntegerField()
    DivisionID=models.IntegerField()
    LoginName=models.CharField(max_length=100)
    Password=models.CharField(max_length=50)
    RoleID=models.IntegerField()  
    IsActive =models.BooleanField(default=False)
    CreatedBy = models.IntegerField()
    CreatedOn = models.DateTimeField(auto_now_add=True)
    UpdatedBy = models.IntegerField()
    UpdatedOn = models.DateTimeField(auto_now=True)
    POSRateType = models.IntegerField()
    
    class Meta:
        db_table="M_SweetPOSUser"

class M_SweetPOSRoles(models.Model):
    Name=models.CharField(max_length=100)
    CreatedBy = models.IntegerField()
    CreatedOn = models.DateTimeField(auto_now_add=True)
    UpdatedBy = models.IntegerField()
    UpdatedOn = models.DateTimeField(auto_now=True)

    class Meta:
            db_table="M_SweetPOSRoles"

class T_SPOSStock(models.Model):
    StockDate=models.DateField()
    Item= models.IntegerField()#ForeignKey(M_Items,related_name='stockItem', on_delete=models.PROTECT)
    BaseUnitQuantity=models.DecimalField(max_digits=20,decimal_places=10)
    Quantity=models.DecimalField(max_digits=20,decimal_places=10)
    Unit = models.IntegerField()#ForeignKey(MC_ItemUnits, related_name='StockUnit', on_delete=models.PROTECT)
    MRP = models.IntegerField()#ForeignKey(M_MRPMaster, related_name='StockItemMRP', on_delete=models.PROTECT)
    MRPValue =  models.DecimalField(max_digits=20, decimal_places=2)
    Party = models.IntegerField()#ForeignKey(M_Parties, related_name='StockParty', on_delete=models.PROTECT)
    CreatedBy = models.IntegerField()
    CreatedOn = models.DateTimeField(auto_now_add=True)
    IsSaleable= models.BooleanField(default=False)
    BatchCode = models.CharField(max_length=500,blank=True,null=True)
    BatchCodeID = models.CharField(max_length=500,blank=True,null=True)
    Difference = models.DecimalField(max_digits=20, decimal_places=3,blank=True,null=True)
    IsStockAdjustment = models.BooleanField(default=False)
   
    class Meta:
        db_table="T_SPOSStock" 

class O_SPOSDateWiseLiveStock(models.Model):
    
    StockDate=models.DateField()
    Item= models.IntegerField()#ForeignKey(M_Items,related_name='DStockItem', on_delete=models.PROTECT)
    OpeningBalance=models.DecimalField(max_digits=20,decimal_places=10)
    GRN = models.DecimalField(max_digits=20,decimal_places=10)
    Sale=models.DecimalField(max_digits=20,decimal_places=10)
    PurchaseReturn = models.DecimalField(max_digits=20,decimal_places=10)
    SalesReturn = models.DecimalField(max_digits=20,decimal_places=10)
    ClosingBalance=models.DecimalField(max_digits=20,decimal_places=10)
    ActualStock = models.DecimalField(max_digits=20,decimal_places=10)
    Unit = models.IntegerField()#ForeignKey(MC_ItemUnits, related_name='DStockUnit', on_delete=models.PROTECT) 
    Party = models.IntegerField()#ForeignKey(M_Parties, related_name='DStockParty', on_delete=models.PROTECT)
    IsAdjusted = models.BooleanField(default=False)
    CreatedBy = models.IntegerField()
    CreatedOn = models.DateTimeField(auto_now_add=True)
    MRPValue = models.DecimalField(max_digits=20,decimal_places=10)
    StockAdjustment = models.DecimalField(max_digits=20,decimal_places=10)

    class Meta:
        db_table="O_SPOSDateWiseLiveStock"                      

class T_SPOSStockOut(models.Model):
    StockDate=models.DateField()
    Item= models.IntegerField()#ForeignKey(M_Items,related_name='stockItem', on_delete=models.PROTECT)
    # BaseUnitQuantity=models.DecimalField(max_digits=20,decimal_places=10)
    # Quantity=models.DecimalField(max_digits=20,decimal_places=10)
    # Unit = models.IntegerField()#ForeignKey(MC_ItemUnits, related_name='StockUnit', on_delete=models.PROTECT)
    # MRP = models.IntegerField()#ForeignKey(M_MRPMaster, related_name='StockItemMRP', on_delete=models.PROTECT)
    # MRPValue =  models.DecimalField(max_digits=20, decimal_places=2)
    Party = models.IntegerField()#ForeignKey(M_Parties, related_name='StockParty', on_delete=models.PROTECT)
    CreatedBy = models.IntegerField()
    CreatedOn = models.DateTimeField(auto_now_add=True)
    # IsSaleable= models.BooleanField(default=False)
    # BatchCode = models.CharField(max_length=500,blank=True,null=True)
    # BatchCodeID = models.CharField(max_length=500,blank=True,null=True)
    # Difference = models.DecimalField(max_digits=20, decimal_places=3,blank=True,null=True)
    # IsStockAdjustment = models.BooleanField(default=False)
    # IsDeleted = models.BooleanField(default=False)
    class Meta:
        db_table="T_SPOSStockOut"        

class TC_SPOSInvoiceUploads(models.Model):
    Invoice = models.ForeignKey(T_SPOSInvoices,related_name='SPOSInvoiceUploads', on_delete=models.CASCADE) 
    AckNo =  models.CharField(max_length=500,null=True)  
    Irn =  models.CharField(max_length=500,null=True)
    QRCodeUrl =models.CharField(max_length=500,null=True)
    EInvoicePdf = models.CharField(max_length=500,null=True)
    EwayBillNo = models.CharField(max_length=500,null=True)
    EwayBillUrl = models.CharField(max_length=500,null=True)
    EInvoiceCreatedBy = models.IntegerField(null=True)
    EInvoiceCreatedOn = models.DateTimeField(null=True)
    EwayBillCreatedBy = models.IntegerField(null=True)
    EwayBillCreatedOn = models.DateTimeField(null=True)
    EInvoiceCanceledBy = models.IntegerField(null=True)
    EInvoiceCanceledOn = models.DateTimeField(null=True)
    EwayBillCanceledBy = models.IntegerField(null=True)
    EwayBillCanceledOn = models.DateTimeField(null=True)
    EInvoiceIsCancel = models.BooleanField(default=False)
    EwayBillIsCancel = models.BooleanField(default=False)
    user_gstin = models.CharField(max_length=500)  
    
    class Meta:
        db_table="TC_SPOSInvoiceUploads" 


class T_SPOSDeletedInvoices(models.Model):
    DeletedTableAutoID  = models.IntegerField()               
    ClientID = models.IntegerField()
    ClientSaleID = models.IntegerField()
    InvoiceDate = models.DateField()    
    Party = models.IntegerField()
    DeletedBy = models.IntegerField()
    DeletedOn = models.DateTimeField(auto_now_add=True)
    ReferenceInvoiceID =models.IntegerField(null=True)
    Invoice = models.ForeignKey(T_SPOSInvoices,related_name='SPOSDeletedInvoiceUploads', on_delete=models.CASCADE) 
    class Meta:
        db_table="T_SPOSDeletedInvoices" 

class M_SPOSRateMaster(models.Model):
    POSRateType = models.IntegerField()   
    IsChangeRateToDefault =  models.BooleanField(default=False)
    EffectiveFrom = models.DateField()
    Rate = models.DecimalField(max_digits=15,decimal_places=2)
    ItemID = models.IntegerField()

    class Meta:
        db_table="M_SPOSRateMaster"