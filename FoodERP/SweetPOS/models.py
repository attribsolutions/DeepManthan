from django.db import models


# Create your models here.
class M_SweetPOSRoleAccess(models.Model):
    
    CreatedBy = models.IntegerField()
    CreatedOn = models.DateTimeField(auto_now_add=True)
    UpdatedBy = models.IntegerField()
    UpdatedOn = models.DateTimeField(auto_now=True)
    Division = models.IntegerField()
    IsAddNewItem = models.BooleanField(default=False)
    IsImportItems = models.BooleanField(default=False)
    IsImportGroups = models.BooleanField(default=False)
    IsUpdateItem = models.BooleanField(default=False)
    IsCItemId = models.BooleanField(default=False)
    IsItemName = models.BooleanField(default=False)
    IsSalesModify = models.BooleanField(default=False)
    IsSalesDelete = models.BooleanField(default=False)
    IsUnitModify = models.BooleanField(default=False)
    IsShowVoucherButton = models.BooleanField(default=False)
    IsGiveSweetPOSUpdate = models.BooleanField(default=False)
    IsSweetPOSAutoUpdate = models.BooleanField(default=False)
    IsSweetPOSServiceAutoUpdate = models.BooleanField(default=False)
    IsEayBillUploadExist = models.BooleanField(default=False)
        
    
    
    class Meta:
        db_table = "M_SweetPOSRoleAccess"