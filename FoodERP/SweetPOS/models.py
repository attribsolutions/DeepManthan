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
        
    