from django.db import models
from django.db.models import UniqueConstraint
from FoodERPApp.models import M_Scheme


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
    AdvanceAmount=models.DecimalField(max_digits=20, decimal_places=2,blank=True, null=True)
    VoucherCode = models.CharField(max_length=50 ,blank=True, null=True)
    class Meta:
        db_table = "T_SPOSInvoices"
        indexes = [
            models.Index(fields=['SaleID']),
            models.Index(fields=['ClientID']),
            models.Index(fields=['InvoiceNumber']),
            models.Index(fields=['InvoiceDate']),
            models.Index(fields=['Customer']),
            models.Index(fields=['Party']),
            # models.Index(fields=['NetAmount']),
            models.Index(fields=['CreatedBy']),
            # If you need to speed up queries on multiple fields, consider composite indexes
            models.Index(fields=['Party', 'InvoiceDate','IsDeleted']),
            models.Index(fields=['Customer', 'InvoiceDate']),
            models.Index(fields=['ClientID', 'Party']),
            models.Index(fields=['Party', 'InvoiceDate','FullInvoiceNumber']),
        ]


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
    IsMixItem = models.BooleanField(default=False)
    MixItemId = models.IntegerField(blank=True, null=True)

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
    POSRateType = models.IntegerField(blank=True, null=True)
    
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
    ClientID =models.IntegerField()
   
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
    Quantity=models.DecimalField(max_digits=15,decimal_places=5)
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
    DeletedBy = models.IntegerField(blank=True,null=True)
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
    IsDeleted = models.BooleanField(default=False)

    class Meta:
        db_table="M_SPOSRateMaster"


# class M_ConsumerMobile(models.Model):    
#     Mobile = models.CharField(max_length=100)
#     IsLinkToBill = models.BooleanField(default=False)
    

#     class Meta:
#         db_table = "M_ConsumerMobile"

class M_ConsumerMobile(models.Model):    
    Mobile = models.CharField(max_length=100)
    IsLinkToBill = models.BooleanField(default=False)
    MacID   = models.CharField(max_length=200)
    Party = models.IntegerField()
    CreatedOn = models.DateTimeField(auto_now_add=True)
    class Meta:  
        db_table = "M_ConsumerMobile"        

class M_SweetPOSMachine(models.Model):
    Party = models.IntegerField()
    MacID = models.CharField(max_length=200)
    MachineType = models.CharField(max_length=200,null=True,blank=True )
    IsServer = models.BooleanField(default=False)
    ClientID =  models.IntegerField()
    ServerSequence = models.IntegerField(null=True,blank=True)
    MachineName = models.CharField(max_length=200,null=True,blank=True)
    Validity = models.DateField(null=True,blank=True)
    UploadSaleRecordCount  = models.IntegerField(null=True,blank=True)
    IsService  = models.BooleanField(default=False)
    Version = models.CharField(max_length=200 ,null=True,blank=True)
    IsGiveUpdate = models.BooleanField(default=False)
    IsAutoUpdate = models.BooleanField(default=False)
    SeverName = models.CharField(max_length=100,null=True,blank=True)
    ServerHost = models.CharField(max_length=100,null=True,blank=True)
    ServerUser = models.CharField(max_length=100,null=True,blank=True)
    ServerPassWord = models.CharField(max_length=100,null=True,blank=True)
    ServerDatabase = models.CharField(max_length=100,null=True,blank=True)
    Invoiceprefix = models.CharField(max_length=100 ,null=True,blank=True)
    ServiceTimeInterval = models.TimeField(null=True,blank=True)
    PrimaryUser =   models.IntegerField(null=True,blank=True)

    class Meta:
        constraints = [
            UniqueConstraint(fields=['Party', 'MacID'], name='unique_Party_MacID')
        ]
        db_table = "M_SweetPOSMachine"        

    # class Meta:
    #     constraints = [
    #         UniqueConstraint(fields=['Party', 'MacID', 'SeverName', 'ServerHost', 'Invoiceprefix'], name='unique_Party_MacID_SeverName_ServerHost_Invoiceprefix')
    #     ]
    #     db_table = "M_SweetPOSMachine"    

class TC_SPOSInvoicesReferences(models.Model):
    Invoice = models.ForeignKey(T_SPOSInvoices, related_name='SPOSInvoicesReferences', on_delete=models.CASCADE)
    Order = models.IntegerField()
    class Meta:
        db_table = "TC_SPOSInvoicesReferences" 

class M_ServiceSettings(models.Model):
    Party = models.IntegerField()    
    ServiceSettingsID=models.IntegerField()
    Flag=models.BooleanField(default=False)
    Value=models.CharField(max_length=50,null=True,blank=True )
    Access=models.BooleanField(default=False)
    CreatedOn=models.DateTimeField(auto_now_add=True)
    UpdatedOn=models.DateTimeField(auto_now=True)
    class Meta:
        db_table="M_ServiceSettings"

# class M_SchemeMaster(models.Model):
#     QRData=  models.CharField(max_length=100 )      
#     SchemeType=models.IntegerField()
#     Item=models.IntegerField(null=True,blank=True)
#     Party=models.IntegerField(null=True,blank=True)
#     IsActive=models.BooleanField(default=False)

class TC_InvoicesSchemes(models.Model):
    Invoice = models.ForeignKey(T_SPOSInvoices, related_name= 'SPOSInvoicesScheme', on_delete=models.CASCADE)
    # Scheme = models.ForeignKey('FoodERP.M_Scheme', related_name='SPOSSchemes', on_delete=models.CASCADE )
    scheme = models.IntegerField()    
    VoucherCode = models.CharField(max_length=50 ,blank=True, null=True)
    class Meta:
        db_table = "TC_InvoicesSchemes"

class M_PosSettings(models.Model):
    Setting_Key    = models.CharField(max_length=255)
    Setting_Value  = models.CharField(max_length=255)
    Description    = models.CharField(max_length=400)
    Setting_Type   = models.BooleanField(default= False)
    Is_Disabled    = models.BooleanField(default= False)
    CreatedOn      = models.DateTimeField(auto_now_add=True)
    UpdatedOn      = models.DateTimeField(auto_now=True)
   
    class Meta:
        db_table = "M_PosSettings"
       
 
class MC_PosSettingDetails(models.Model):
    PosSetting = models.ForeignKey(M_PosSettings, related_name='PosSettingDetails', on_delete=models.CASCADE)
    Setting_Value = models.CharField(max_length=255)
    PartyId         = models.IntegerField()
    Is_Disabled    = models.BooleanField(default= False)
 
    class Meta:
        db_table = 'MC_PosSettingDetails'   

class M_PhonePeSettings(models.Model):
       
    client_id = models.IntegerField()
    party_id  = models.IntegerField()
    user_id = models.IntegerField()
    base_url = models.CharField(max_length=255)
    merchant_id = models.BinaryField(max_length=255)
    provider_id = models.BinaryField(max_length=255)
    salt_key   = models.BinaryField(max_length=255)
    key_index = models.CharField(max_length=255)
    store_id = models.CharField(max_length=100)
    store_name = models.CharField(max_length=255)
    terminal_id =models.CharField(max_length=100)
    merchant_name =models.CharField(max_length=255)
    x_callback_url = models.CharField(max_length=400)
    is_active  = models.BooleanField(default=True)
    CreatedOn      = models.DateTimeField(auto_now_add=True)
    UpdatedOn      = models.DateTimeField(auto_now=True)             

    class Meta:
        db_table = 'M_PhonePeSettings'  

class M_PaymentModes(models.Model):
    Payment_Mode = models.CharField(max_length=50)
    TenderCode =models.CharField(max_length=50,blank=True, null=True)
    class Meta:
        db_table = 'M_PaymentModes'
 
class MC_PaymentModeDetails(models.Model):
    Paymentmodes = models.ForeignKey(M_PaymentModes, on_delete=models.CASCADE)
    PartyId      = models.IntegerField()
 
    class Meta:
        db_table = 'MC_PaymentModeDetails'       

class M_ERPUrls(models.Model):
    Name = models.CharField(max_length=150)
    Urls = models.CharField(max_length=400)

    class Meta:
        db_table = "M_ERPUrls"

class MC_ERPUrlsDetails(models.Model):
    PartyId = models.IntegerField()
    ERPUrls = models.ForeignKey(M_ERPUrls,on_delete=models.CASCADE)
    Urls    = models.CharField(max_length=400)

    class Meta:
        db_table = 'MC_ERPUrlsDetails'
