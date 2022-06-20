from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser

# Create your models here.

class UserManager(BaseUserManager):
    '''
    creating a manager for a custom user model
    https://docs.djangoproject.com/en/3.0/topics/auth/customizing/#writing-a-manager-for-a-custom-user-model
    https://docs.djangoproject.com/en/3.0/topics/auth/customizing/#a-full-example
    '''
    def create_user(self, email, LoginName,EmployeeID, isActive, isSendOTP, AdminPassword, password=None):
        """
        Create and return a `User` with an email, username and password.
        """
        if not LoginName:
            raise ValueError('Users Must Have LoginName')

        user = self.model(
             email=self.normalize_email(email),
             LoginName=LoginName,
             EmployeeID=EmployeeID,
             isActive=isActive,
             AdminPassword=password,
             isSendOTP=isSendOTP,
            
        )
        
        user.set_password(password)
        user.save(using=self._db)
        return user


class M_Users(AbstractBaseUser):
    ID = models.AutoField(primary_key=True)
    LoginName = models.CharField(max_length=100, unique=True)
    email = models.EmailField(
        verbose_name='email address',
        max_length=255)
    EmployeeID = models.IntegerField(default=False)
    isActive = models.BooleanField(default=False)
    isSendOTP = models.BooleanField(default=False)
    AdminPassword = models.CharField(max_length=100)
    CreatedBy = models.IntegerField(default=False)
    CreatedOn = models.DateTimeField(auto_now_add=True)
    UpdatedBy = models.IntegerField(default=False)
    UpdatedOn = models.DateTimeField(auto_now_add=True)
     

    USERNAME_FIELD = 'LoginName'
    REQUIRED_FIELDS = []

    # Tells Django that the UserManager class defined above should manage
    # objects of this type.
    objects = UserManager()

    class Meta :
        db_table = "M_Users"

    def __str__(self):
        return self.LoginName

    def __str__(self):
        return self.ID

        
class H_Modules(models.Model):
    ID = models.AutoField(primary_key=True)
    Name = models.CharField(max_length=100)
    DisplayIndex = models.IntegerField()
    IsActive = models.BooleanField(default=False)
    Icon = models.CharField(max_length=100)
    CreatedBy = models.IntegerField(blank=True, null=True)
    CreatedOn = models.DateTimeField(auto_now_add=True,blank=True)
    UpdatedBy = models.IntegerField(blank=True, null=True)
    UpdatedOn = models.DateTimeField(auto_now_add=True,blank=True)    
    
    class Meta:
        db_table = "H_Modules"   



class M_Pages(models.Model):
    ID = models.AutoField(primary_key=True)
    Name = models.CharField(max_length=100)
    Description = models.CharField(max_length=100)
    Module = models.ForeignKey(H_Modules, related_name = 'M_PagesModule', on_delete = models.CASCADE)
    isActive = models.BooleanField(default=False)
    DisplayIndex = models.IntegerField()
    Icon = models.CharField(max_length=100)
    ActualPagePath = models.CharField(max_length=100)
    isShowOnMenu = models.BooleanField(default=False)
    PageType = models.IntegerField()
    RelatedPageID =  models.IntegerField()
    CreatedBy = models.IntegerField()
    CreatedOn = models.DateTimeField(auto_now_add=True)
    UpdatedBy = models.IntegerField()
    UpdatedOn = models.DateTimeField(auto_now_add=True) 

    class Meta:
        db_table = "M_Pages"

class C_CompanyGroups(models.Model):
    ID = models.AutoField(primary_key=True)
    Name = models.CharField(max_length=100)
    CreatedBy = models.IntegerField(blank=True, null=True)
    CreatedOn = models.DateTimeField(auto_now_add=True)
    UpdatedBy = models.IntegerField(blank=True, null=True)
    UpdatedOn = models.DateTimeField(auto_now_add=True)

    class Meta:
         db_table = "C_CompanyGroups"

class C_Companies(models.Model):
    ID = models.AutoField(primary_key=True)
    Name = models.CharField(max_length=100)
    Address = models.CharField(max_length=100)
    GSTIN = models.CharField(max_length=100)
    PhoneNo = models.CharField(max_length=100)
    CompanyAbbreviation = models.CharField(max_length=100)
    EmailID = models.CharField(max_length=100) 
    CompanyGroup= models.ForeignKey(C_CompanyGroups, related_name='CompanyGroup', on_delete=models.DO_NOTHING)  
    CreatedBy = models.IntegerField(blank=True, null=True)
    CreatedOn = models.DateTimeField(auto_now_add=True)
    UpdatedBy = models.IntegerField(blank=True, null=True)
    UpdatedOn = models.DateTimeField(auto_now_add=True)

    class Meta:
         db_table = "C_Companies"

class M_Parties(models.Model):
    ID = models.AutoField(primary_key=True)
    Name = models.CharField(max_length=500)
    PartyTypeID = models.IntegerField( )
    DividionTypeID =  models.IntegerField()
    companyID =  models.IntegerField()
    CustomerDivision =  models.IntegerField()
    Email = models.EmailField(max_length=200)
    Address = models.CharField(max_length=500)
    PIN = models.CharField(max_length=500)
    State = models.IntegerField()
    District = models.IntegerField()
    Taluka = models.IntegerField ()
    City = models.IntegerField()
    GSTN =  models.CharField(max_length=500)
    FSSAINo = models.CharField(max_length=500)
    FSSAIExipry = models.DateField(blank=True)
    IsActive =  models.IntegerField()

    class Meta:
        db_table = 'M_Parties'

class M_Roles(models.Model):
    ID = models.AutoField(primary_key=True)
    Name = models.CharField(max_length=100)
    Description = models.CharField(max_length=100)
    isActive = models.BooleanField(default=False)
    Dashboard = models.CharField(max_length=200)
    CreatedBy = models.IntegerField(blank=True, null=True)
    CreatedOn = models.DateTimeField(auto_now_add=True)
    UpdatedBy = models.IntegerField(blank=True, null=True)
    UpdatedOn = models.DateTimeField(auto_now_add=True)   
    
    class Meta :
        db_table = "M_Roles"
        def __str__(self):
            return self.Name  

class MC_UserRoles(models.Model):
    ID = models.AutoField(primary_key=True)
    UserID = models.ForeignKey(M_Users,  on_delete=models.CASCADE)
    RoleID = models.ForeignKey(M_Roles,  on_delete=models.DO_NOTHING)   

    class Meta :
        db_table = "MC_UserRoles"
                      

class M_RoleAccess(models.Model):
    ID = models.AutoField(primary_key=True)
    Role = models.ForeignKey(M_Roles, related_name = 'Role' , on_delete = models.DO_NOTHING)
    Company = models.ForeignKey(C_Companies, related_name='Company',on_delete=models.DO_NOTHING)
    Division = models.ForeignKey(M_Parties, related_name='Dividion', on_delete =models.DO_NOTHING)
    Modules = models.ForeignKey(H_Modules, related_name='M_RoleAccessModules',on_delete=models.DO_NOTHING)
    Pages = models.ForeignKey(M_Pages, related_name='Pages',on_delete=models.DO_NOTHING)

    class Meta:
        db_table ="M_RoleAccess"


class H_PageAccess(models.Model):
    ID = models.AutoField(primary_key=True)
    Name = models.CharField(max_length=100)

    class Meta:
        db_table = 'H_PageAccess'

class MC_PagePageAccess(models.Model):
    ID = models.AutoField(primary_key=True)
    PageID = models.ForeignKey(M_Pages,related_name='PagePageAccess', on_delete=models.CASCADE, null=True)
    AccessID = models.ForeignKey(H_PageAccess ,on_delete=models.CASCADE, null=True)

    class Meta:
        db_table = "MC_PagePageAccess"   

class M_ItemsGroup(models.Model):
    ID = models.AutoField(primary_key=True)
    Name = models.CharField(max_length=500)
    Sequence = models.DecimalField(max_digits = 5,decimal_places=2)
    isActive = models.BooleanField(default=False)
    CreatedBy = models.IntegerField(default=False)
    CreatedOn = models.DateTimeField(auto_now_add=True)
    UpdatedBy = models.IntegerField(default=False)
    UpdatedOn = models.DateTimeField(auto_now_add=True)

    class Meta :
        db_table ="M_ItemsGroup"
    
class M_Items(models.Model):
    ID = models.AutoField(primary_key=True)
    Name = models.CharField(max_length=500)
    Sequence = models.DecimalField(max_digits = 5,decimal_places=2)
    BaseunitID = models.IntegerField()
    GSTPercentage = models.DecimalField(max_digits = 5,decimal_places=2)
    MRP = models.DecimalField(max_digits = 5,decimal_places=2)
    ItemGroup = models.ForeignKey(M_ItemsGroup, on_delete=models.CASCADE)
    Rate =models.DecimalField(max_digits = 5,decimal_places=2)
    isActive = models.BooleanField(default=False)
    CreatedBy = models.IntegerField(default=False)
    CreatedOn = models.DateTimeField(auto_now_add=True)
    UpdatedBy = models.IntegerField(default=False)
    UpdatedOn = models.DateTimeField(auto_now_add=True)

    class Meta :
        db_table ="M_Items"
    
class T_Orders(models.Model):
    
    OrderDate = models.DateField(auto_now_add=True)
    CustomerID = models.IntegerField()
    
    PartyID  =  models.IntegerField()
    OrderAmount = models.DecimalField(max_digits = 5,decimal_places=2)
    Discreption = models.CharField(max_length=500)
    CreatedBy = models.IntegerField(blank=True, null=True)
    CreatedOn = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "T_Orders"
  
class TC_OrderItems(models.Model):
    
    OrderID = models.ForeignKey(T_Orders, related_name='OrderItem', on_delete=models.CASCADE)
    ItemID = models.ForeignKey(M_Items, on_delete=models.CASCADE)
    Quantity  =  models.DecimalField(max_digits = 5,decimal_places=2)
    MRP =  models.DecimalField(max_digits = 5,decimal_places=2)
    Rate =models.DecimalField(max_digits = 5,decimal_places=2)
    UnitID = models.IntegerField( )
    BaseUnitQuantity = models.DecimalField(max_digits = 5,decimal_places=2)
    GST = models.DecimalField(max_digits = 5,decimal_places=2)

    class Meta :
        db_table = "TC_OrderItems"

class M_EmployeeType(models.Model):
    Name = models.CharField(max_length=100)
    CreatedBy = models.IntegerField(blank=True, null=True)
    CreatedOn = models.DateTimeField(auto_now_add=True)

    class Meta :
        db_table = "M_EmployeeType"

class M_Designations(models.Model):
    Name = models.CharField(max_length=100)
    CreatedBy = models.IntegerField(blank=True, null=True)
    CreatedOn = models.DateTimeField(auto_now_add=True)

    class Meta :
        db_table = "M_Designations"

class M_State(models.Model):
    Name = models.CharField(max_length=100)
    CreatedBy = models.IntegerField(blank=True, null=True)
    CreatedOn = models.DateTimeField(auto_now_add=True)

    class Meta :
        db_table = "M_State"


class M_Employees(models.Model):
    Name = models.CharField(max_length=100)
    Address = models.CharField(max_length=500)
    Mobile = models.IntegerField()
    email = models.EmailField(max_length=255) 
    DOB = models.CharField(max_length=100)
    PAN = models.CharField(max_length=100)
    AadharNo = models.IntegerField()
    Companies = models.ForeignKey(C_Companies, on_delete=models.CASCADE)
    EmployeeType = models.ForeignKey(M_EmployeeType, on_delete=models.CASCADE)
    Designations = models.ForeignKey(M_Designations, on_delete=models.CASCADE) 
    State = models.ForeignKey(M_State, on_delete=models.CASCADE)
    CreatedBy = models.IntegerField(blank=True, null=True)
    CreatedOn = models.DateTimeField(blank=True, null=True)
    UpdatedBy = models.IntegerField(blank=True, null=True)
    UpdatedOn = models.DateTimeField(blank=True, null=True)

    class Meta :
        db_table = "M_Employees"        


class T_Invoice(models.Model):

    OrderID = models.ForeignKey(T_Orders, on_delete=models.CASCADE)
    InvoiceDate = models.DateField(auto_now_add=True)
    CustomerID = models.IntegerField(blank=True, null=True)
    InvoiceNumber  =  models.IntegerField(blank=True, null=True)
    FullInvoiceNumber =  models.CharField(max_length=500)
    CustomerGSTTin = models.CharField(max_length=500)
    GrandTotal =  models.DecimalField(max_digits = 15,decimal_places=2)
    PartyID = models.IntegerField(blank=True, null=True)
    RoundOffAmount = models.DecimalField(max_digits = 5,decimal_places=2)
    CreatedBy  =  models.IntegerField(blank=True, null=True)
    CreatedOn =  models.DateTimeField(auto_now_add=True)
    UpdatedBy = models.IntegerField(blank=True, null=True)
    UpdatedOn = models.DateTimeField(auto_now_add=True)
    
    class Meta :
        db_table ="T_Invoice"
    
class  TC_InvoiceItems(models.Model):
    InvoiceID = models.ForeignKey(T_Invoice, related_name='InvoiceItems', on_delete=models.CASCADE)
    ItemID = models.ForeignKey(M_Items, on_delete=models.CASCADE)
    HSNCode = models.CharField(max_length=500)
    Quantity  =  models.DecimalField(max_digits = 5,decimal_places=2)
    UnitID = models.IntegerField( )
    BaseUnitQuantity = models.DecimalField(max_digits = 15,decimal_places=2)
    QtyInKg = models.DecimalField(max_digits = 10,decimal_places=2)
    QtyInNo = models.DecimalField(max_digits = 10,decimal_places=2)
    QtyInBox = models.DecimalField(max_digits = 10,decimal_places=2)
    MRP =  models.DecimalField(max_digits = 15,decimal_places=2)
    Rate =models.DecimalField(max_digits = 15,decimal_places=2)
    BasicAmount =  models.DecimalField(max_digits = 15,decimal_places=2)
    TaxType =models.CharField(max_length=500)
    GSTPercentage = models.DecimalField(max_digits = 5,decimal_places=2)
    GSTAmount = models.DecimalField(max_digits = 15,decimal_places=2)
    Amount = models.DecimalField(max_digits = 15,decimal_places=2)
    DiscountType = models.CharField(max_length=500)   
    Discount =  models.DecimalField(max_digits = 10,decimal_places=2)
    DiscountAmount = models.DecimalField(max_digits = 10,decimal_places=2)
    CGST = models.DecimalField(max_digits = 5,decimal_places=2)
    SGST = models.DecimalField(max_digits = 5,decimal_places=2)
    IGST = models.DecimalField(max_digits = 5,decimal_places=2)
    CGSTPercentage = models.DecimalField(max_digits = 5,decimal_places=2)
    SGSTPercentage = models.DecimalField(max_digits = 5,decimal_places=2)
    IGSTPercentage = models.DecimalField(max_digits = 5,decimal_places=2)
    CreatedOn =  models.DateTimeField(auto_now_add=True)
    
    class Meta :
        db_table ="TC_InvoiceItems"
        
        
class TC_InvoiceItemBatches(models.Model):
    InvoiceID = models.ForeignKey(T_Invoice, on_delete=models.CASCADE)
    InvoiceItemID = models.ForeignKey(TC_InvoiceItems, related_name='InvoiceItemBatches', on_delete=models.CASCADE)
    ItemID = models.ForeignKey(M_Items, on_delete=models.CASCADE)
    BatchDate = models.DateField(blank=True, null=True)
    BatchCode = models.CharField(max_length=500)
    Quantity  =  models.DecimalField(max_digits = 5,decimal_places=2)
    UnitID = models.IntegerField()
    MRP = models.DecimalField(max_digits = 15,decimal_places=2)
    CreatedOn =  models.DateTimeField(auto_now_add=True)
    
    class Meta :
        db_table ="TC_InvoiceItemBatches"

