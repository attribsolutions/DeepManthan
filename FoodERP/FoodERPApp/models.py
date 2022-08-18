from datetime import datetime
from pickle import TRUE
from statistics import mode
from typing import Sequence
from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.


class M_DivisionType(models.Model):
    Name = models.CharField(max_length=100)
    IsSCM =models.BooleanField(default=False)  
    CreatedBy = models.IntegerField()
    CreatedOn = models.DateTimeField(auto_now_add=True)
    UpdatedBy = models.IntegerField()
    UpdatedOn = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'M_DivisionType'


class M_PartyType(models.Model):
    Name = models.CharField(max_length=100)
    DivisionType = models.ForeignKey(
        M_DivisionType, related_name='PartyTypeDivision', on_delete=models.DO_NOTHING)
    CreatedBy = models.IntegerField()
    CreatedOn = models.DateTimeField(auto_now_add=True)
    UpdatedBy = models.IntegerField()
    UpdatedOn = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'M_PartyType'


class C_CompanyGroups(models.Model):

    Name = models.CharField(max_length=100)
    ''' If IsSCM Flag is True then this compalny group work for Supply chain management else Not 
     and other Table's IsSCM flag Are depend on this Flag  '''
    IsSCM =models.BooleanField(default=False)   
    
    CreatedBy = models.IntegerField()
    CreatedOn = models.DateTimeField(auto_now_add=True)
    UpdatedBy = models.IntegerField()
    UpdatedOn = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "C_CompanyGroups"


class C_Companies(models.Model):

    Name = models.CharField(max_length=100)
    Address = models.CharField(max_length=100, null=True, blank=True)
    GSTIN = models.CharField(max_length=100)
    PhoneNo = models.CharField(max_length=100, null=True, blank=True)
    CompanyAbbreviation = models.CharField(max_length=100)
    EmailID = models.CharField(max_length=100, null=True, blank=True)
    CompanyGroup = models.ForeignKey(
        C_CompanyGroups, related_name='CompanyGroup', on_delete=models.DO_NOTHING)
    IsSCM =models.BooleanField(default=False)
    CreatedBy = models.IntegerField()
    CreatedOn = models.DateTimeField(auto_now_add=True)
    UpdatedBy = models.IntegerField()
    UpdatedOn = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "C_Companies"


class M_States(models.Model):
    Name = models.CharField(max_length=100)
    StateCode = models.CharField(max_length=100)
    CreatedBy = models.IntegerField()
    CreatedOn = models.DateTimeField(auto_now_add=True)
    UpdatedBy = models.IntegerField()
    UpdatedOn = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "M_States"


class M_Districts(models.Model):
    Name = models.CharField(max_length=100)
    State = models.ForeignKey(
        M_States, related_name='DistrictState', on_delete=models.DO_NOTHING)
    CreatedBy = models.IntegerField()
    CreatedOn = models.DateTimeField(auto_now_add=True)
    UpdatedBy = models.IntegerField()
    UpdatedOn = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "M_Districts"


class M_Parties(models.Model):

    Name = models.CharField(max_length=500)
    PartyType = models.ForeignKey(
        M_PartyType, related_name='PartiesPartyType', on_delete=models.DO_NOTHING, blank=True)
    DivisionType = models.ForeignKey(
        M_DivisionType, related_name='PartiesDivision', on_delete=models.DO_NOTHING)
    Company = models.ForeignKey(
        C_Companies, related_name='PartiesCompany', on_delete=models.DO_NOTHING)
    # IsSCM = models.ForeignKey(
    #     C_Companies, related_name='IsSCM', on_delete=models.DO_NOTHING, null=True)
    CustomerDivision = models.IntegerField()
    Email = models.EmailField(max_length=200)
    MobileNo = models.BigIntegerField()
    AlternateContactNo = models.CharField(
        max_length=500, null=True, blank=True)
    Address = models.CharField(max_length=500)
    PIN = models.CharField(max_length=500)
    State = models.ForeignKey(
        M_States, related_name='PartiesState', on_delete=models.DO_NOTHING)
    District = models.ForeignKey(
        M_Districts, related_name='PartiesDistrict', on_delete=models.DO_NOTHING)
    Taluka = models.IntegerField()
    City = models.IntegerField()
    GSTIN = models.CharField(max_length=500)
    PAN = models.CharField(max_length=500)
    FSSAINo = models.CharField(max_length=500)
    FSSAIExipry = models.DateField(blank=True)
    isActive = models.BooleanField(default=False)
    CreatedBy = models.IntegerField()
    CreatedOn = models.DateTimeField(auto_now_add=True)
    UpdatedBy = models.IntegerField()
    UpdatedOn = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'M_Parties'


class M_EmployeeTypes(models.Model):
    Name = models.CharField(max_length=100)
    ''' If IsPartyConnection Flag is True then we are able to assign multipal Parties from Employee Master  '''
    IsPartyConnection=models.BooleanField(default=False)
    IsSCM =models.BooleanField(default=False)
    Description= models.CharField(max_length=100,blank=True,null=True)
    CreatedBy = models.IntegerField()
    CreatedOn = models.DateTimeField(auto_now_add=True)
    UpdatedBy = models.IntegerField()
    UpdatedOn = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "M_EmployeeTypes"


class M_Designations(models.Model):
    Name = models.CharField(max_length=100)
    CreatedBy = models.IntegerField()
    CreatedOn = models.DateTimeField(auto_now_add=True)
    UpdatedBy = models.IntegerField()
    UpdatedOn = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "M_Designations"


class M_Employees(models.Model):
    Name = models.CharField(max_length=100)
    Address = models.CharField(max_length=500)
    Mobile = models.CharField(max_length=100)
    email = models.EmailField(max_length=255)
    DOB = models.CharField(max_length=100)
    PAN = models.CharField(max_length=100)
    AadharNo = models.CharField(max_length=100)
    working_hours = models.DecimalField(max_digits=15, decimal_places=2)

    Company = models.ForeignKey(
        C_Companies, related_name='EmployeesCompany', on_delete=models.DO_NOTHING)
    EmployeeType = models.ForeignKey(
        M_EmployeeTypes, related_name='EmployeeType', on_delete=models.DO_NOTHING)
    Designation = models.ForeignKey(
        M_Designations, related_name='EmployeesDesignation', on_delete=models.DO_NOTHING, null=True)
    State = models.ForeignKey(
        M_States, related_name='EmployeesState', on_delete=models.DO_NOTHING)
    District = models.ForeignKey(
        M_Districts, related_name='EmployeesDistrict', on_delete=models.DO_NOTHING)
    CreatedBy = models.IntegerField()
    CreatedOn = models.DateTimeField(auto_now_add=True)
    UpdatedBy = models.IntegerField()
    UpdatedOn = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "M_Employees"


class MC_EmployeeParties(models.Model):
    Employee = models.ForeignKey(
        M_Employees, related_name='EmployeeParties', on_delete=models.CASCADE)
    Party = models.ForeignKey(
        M_Parties, related_name='Employeeparty',  on_delete=models.DO_NOTHING ,null=True)

    class Meta:
        db_table = "MC_EmployeeParties"


class UserManager(BaseUserManager):
    '''
    creating a manager for a custom user model
    https://docs.djangoproject.com/en/3.0/topics/auth/customizing/#writing-a-manager-for-a-custom-user-model
    https://docs.djangoproject.com/en/3.0/topics/auth/customizing/#a-full-example
    '''

    def create_user(self,  LoginName, Employee, isActive, isSendOTP, AdminPassword, isLoginUsingMobile, isLoginUsingEmail, CreatedBy,  UpdatedBy, password=None):
        """
        Create and return a `User` with  username and password.
        """
        if not LoginName:
            raise ValueError('Users Must Have LoginName')

        user = self.model(

            LoginName=LoginName,
            Employee=Employee,
            isActive=isActive,
            AdminPassword=password,
            isSendOTP=isSendOTP,
            isLoginUsingEmail=isLoginUsingEmail,
            isLoginUsingMobile=isLoginUsingMobile,
            CreatedBy=CreatedBy,
            UpdatedBy=UpdatedBy,




        )

        user.set_password(password)
        user.save(using=self._db)
        return user


class M_Users(AbstractBaseUser):

    LoginName = models.CharField(max_length=100, unique=True)
    Employee = models.ForeignKey(
        M_Employees, related_name='UserEmployee', on_delete=models.DO_NOTHING)
    isActive = models.BooleanField(default=False)
    isSendOTP = models.BooleanField(default=False)
    isLoginUsingMobile = models.BooleanField(default=False)
    isLoginUsingEmail = models.BooleanField(default=False)
    AdminPassword = models.CharField(max_length=100)
    OTP = models.CharField(max_length=1002, null=True)
    CreatedBy = models.IntegerField()
    CreatedOn = models.DateTimeField(auto_now_add=True)
    UpdatedBy = models.IntegerField()
    UpdatedOn = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'LoginName'
    REQUIRED_FIELDS = []

    # Tells Django that the UserManager class defined above should manage
    # objects of this type.
    objects = UserManager()

    class Meta:
        db_table = "M_Users"

    def __str__(self):
        return self.LoginName

    def __str__(self):
        return self.ID


class H_Modules(models.Model):

    Name = models.CharField(max_length=100)
    DisplayIndex = models.IntegerField()
    isActive = models.BooleanField(default=False)
    Icon = models.CharField(max_length=100)
    CreatedBy = models.IntegerField(blank=True, null=True)
    CreatedOn = models.DateTimeField(auto_now_add=True,)
    UpdatedBy = models.IntegerField(blank=True, null=True)
    UpdatedOn = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "H_Modules"


class M_Pages(models.Model):
    PageHeading = models.CharField(max_length=500, blank=True)
    Name = models.CharField(max_length=100)
    PageDescription = models.CharField(max_length=500, blank=True)
    PageDescriptionDetails = models.CharField(max_length=500, blank=True)
    Module = models.ForeignKey(
        H_Modules, related_name='PagesModule', on_delete=models.DO_NOTHING)
    isActive = models.BooleanField(default=False)
    DisplayIndex = models.IntegerField()
    Icon = models.CharField(max_length=100)
    ActualPagePath = models.CharField(max_length=100)
    # isShowOnMenu = models.BooleanField(default=False)
    PageType = models.IntegerField()
    RelatedPageID = models.IntegerField()
    CreatedBy = models.IntegerField()
    CreatedOn = models.DateTimeField(auto_now_add=True)
    UpdatedBy = models.IntegerField()
    UpdatedOn = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "M_Pages"


class M_Roles(models.Model):

    Name = models.CharField(max_length=100)
    Description = models.CharField(max_length=100)
    isActive = models.BooleanField(default=False)
    isSCMRole = models.BooleanField(default=False)
    Dashboard = models.CharField(max_length=200)
    CreatedBy = models.IntegerField()
    CreatedOn = models.DateTimeField(auto_now_add=True)
    UpdatedBy = models.IntegerField()
    UpdatedOn = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "M_Roles"

        def __str__(self):
            return self.Name


class MC_UserRoles(models.Model):

    User = models.ForeignKey(
        M_Users, related_name='UserRole',  on_delete=models.CASCADE)
    Party = models.ForeignKey(
        M_Parties, related_name='userparty',  on_delete=models.DO_NOTHING, null=True)
    Role = models.ForeignKey(M_Roles, related_name='Role',
                             on_delete=models.DO_NOTHING)

    class Meta:
        db_table = "MC_UserRoles"


class M_RoleAccess(models.Model):

    Role = models.ForeignKey(
        M_Roles, related_name='RoleAccessRole', on_delete=models.DO_NOTHING)
    Company = models.ForeignKey(
        C_Companies, related_name='RoleAccessCompany', on_delete=models.DO_NOTHING)
    Division = models.ForeignKey(
        M_Parties, related_name='RoleAccessDividion', on_delete=models.DO_NOTHING)
    Modules = models.ForeignKey(
        H_Modules, related_name='RoleAccessModules', on_delete=models.DO_NOTHING)
    Pages = models.ForeignKey(
        M_Pages, related_name='RoleAccessPages', on_delete=models.DO_NOTHING)
    CreatedBy = models.IntegerField()
    CreatedOn = models.DateTimeField(auto_now_add=True)
    UpdatedBy = models.IntegerField()
    UpdatedOn = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "M_RoleAccess"


class H_PageAccess(models.Model):

    Name = models.CharField(max_length=100)
    CreatedBy = models.IntegerField()
    CreatedOn = models.DateTimeField(auto_now_add=True)
    UpdatedBy = models.IntegerField()
    UpdatedOn = models.DateTimeField(auto_now=True)
    Sequence = models.IntegerField()

    class Meta:
        db_table = 'H_PageAccess'

# M_Pages child table


class MC_PagePageAccess(models.Model):

    Page = models.ForeignKey(
        M_Pages, related_name='PagePageAccess', on_delete=models.CASCADE)
    Access = models.ForeignKey(H_PageAccess, on_delete=models.DO_NOTHING)

    class Meta:
        db_table = "MC_PagePageAccess"

# RoleAccess child table


class MC_RolePageAccess(models.Model):
    RoleAccess = models.ForeignKey(
        M_RoleAccess, related_name='RoleAccess', on_delete=models.CASCADE)
    PageAccess = models.ForeignKey(
        H_PageAccess, related_name='RolePageAccess', on_delete=models.DO_NOTHING)

    class Meta:
        db_table = "MC_RolePageAccess"


class M_ItemsGroup(models.Model):

    Name = models.CharField(max_length=500)
    Sequence = models.DecimalField(max_digits=5, decimal_places=2)
    isActive = models.BooleanField(default=False)
    CreatedBy = models.IntegerField()
    CreatedOn = models.DateTimeField(auto_now_add=True)
    UpdatedBy = models.IntegerField()
    UpdatedOn = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "M_ItemsGroup"


class M_Units(models.Model):
    Name = models.CharField(max_length=500)
    CreatedBy = models.IntegerField()
    CreatedOn = models.DateTimeField(auto_now_add=True)
    UpdatedBy = models.IntegerField()
    UpdatedOn = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "M_Units"


class M_Items(models.Model):

    Name = models.CharField(max_length=500)
    ShortName = models.CharField(max_length=500)
    Sequence = models.DecimalField(max_digits=5, decimal_places=2)
    Company = models.ForeignKey(
        C_Companies, related_name='ItemCompany', on_delete=models.DO_NOTHING)
    BaseUnitID = models.ForeignKey(
        M_Units, related_name='BaseUnitID', on_delete=models.DO_NOTHING)
    GSTPercentage = models.DecimalField(max_digits=10, decimal_places=2)
    MRP = models.DecimalField(max_digits=20, decimal_places=2)
    BarCode = models.CharField(max_length=500) 
    ItemGroup = models.ForeignKey(
        M_ItemsGroup, related_name='ItemGroup', on_delete=models.DO_NOTHING)
    Rate = models.DecimalField(max_digits=20, decimal_places=2)
    isActive = models.BooleanField(default=False)
    image = models.ImageField(upload_to='images')  
    CreatedBy = models.IntegerField(default=False)
    CreatedOn = models.DateTimeField(auto_now_add=True)
    UpdatedBy = models.IntegerField(default=False)
    UpdatedOn = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "M_Items"


class MC_ItemUnits(models.Model):
    Item = models.ForeignKey(
        M_Items, related_name='ItemUnitsItemID', on_delete=models.DO_NOTHING)
    UnitID = models.ForeignKey(
        M_Units, related_name='UnitID', on_delete=models.DO_NOTHING)
    BaseUnitQuantity = models.DecimalField(max_digits=5, decimal_places=3)
    IsBase = models.IntegerField()
    IsDefault = models.IntegerField()
    IsSSUnit = models.IntegerField()
    IsDeleted = models.BooleanField(default=False)

    class Meta:
        db_table = "MC_ItemUnits"

class M_ProductCategoryType(models.Model):
    Name = models.CharField(max_length=500)
    CreatedBy = models.IntegerField(default=False)
    CreatedOn = models.DateTimeField(auto_now_add=True)
    UpdatedBy = models.IntegerField(default=False)
    UpdatedOn = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "M_ProductCategoryType"

class M_ProductCategory(models.Model):
    Name = models.CharField(max_length=500)
    ProductCategoryType = models.ForeignKey(
        M_ProductCategoryType, related_name='ProductCategoryType', on_delete=models.DO_NOTHING)
    CreatedBy = models.IntegerField(default=False)
    CreatedOn = models.DateTimeField(auto_now_add=True)
    UpdatedBy = models.IntegerField(default=False)
    UpdatedOn = models.DateTimeField(auto_now_add=True)    
    class Meta:
        db_table = "M_ProductCategory"

class M_ProductSubCategory(models.Model):
    Name = models.CharField(max_length=500)
    ProductCategory = models.ForeignKey(
        M_ProductCategory, related_name='ProductCategory', on_delete=models.DO_NOTHING)
    CreatedBy = models.IntegerField(default=False)
    CreatedOn = models.DateTimeField(auto_now_add=True)
    UpdatedBy = models.IntegerField(default=False)
    UpdatedOn = models.DateTimeField(auto_now_add=True)    
    class Meta:
        db_table = "M_ProductSubCategory"


class M_Products(models.Model):
    Name = models.CharField(max_length=500)
    ProductCategory = models.ForeignKey(
        M_ProductCategory, related_name='MProductCategory', on_delete=models.DO_NOTHING)
    Item = models.ForeignKey(
        M_Items, related_name='ProductItem', on_delete=models.DO_NOTHING)     
    CreatedBy = models.IntegerField(default=False)
    CreatedOn = models.DateTimeField(auto_now_add=True)
    UpdatedBy = models.IntegerField(default=False)
    UpdatedOn = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table = "M_Products"


class T_Orders(models.Model):

    OrderDate = models.DateField()
    Customer = models.ForeignKey(
        M_Items, related_name='OrderCustomer', on_delete=models.DO_NOTHING)
    Party = models.ForeignKey(
        M_Items, related_name='OrderParty', on_delete=models.DO_NOTHING)
    OrderAmount = models.DecimalField(max_digits=20, decimal_places=2)
    Description = models.CharField(max_length=500)
    CreatedBy = models.IntegerField()
    CreatedOn = models.DateTimeField(auto_now_add=True)
    UpdatedBy = models.IntegerField()
    UpdatedOn = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "T_Orders"


class TC_OrderItems(models.Model):

    Order = models.ForeignKey(
        T_Orders, related_name='OrderItem', on_delete=models.CASCADE)
    Item = models.ForeignKey(
        M_Items, related_name='Items', on_delete=models.DO_NOTHING)
    Quantity = models.DecimalField(max_digits=10, decimal_places=2)
    MRP = models.DecimalField(max_digits=10, decimal_places=2)
    Rate = models.DecimalField(max_digits=10, decimal_places=2)
    Unit = models.ForeignKey(
        MC_ItemUnits, related_name='OrderUnitID', on_delete=models.CASCADE)
    BaseUnitQuantity = models.DecimalField(max_digits=5, decimal_places=2)
    GST = models.DecimalField(max_digits=5, decimal_places=2)
    BasicAmount = models.DecimalField(max_digits=20, decimal_places=2)
    GSTAmount = models.DecimalField(max_digits=10, decimal_places=2)
    Amount = models.DecimalField(max_digits=20, decimal_places=2)
    CGST = models.DecimalField(max_digits=20, decimal_places=2)
    SGST = models.DecimalField(max_digits=20, decimal_places=2)
    IGST = models.DecimalField(max_digits=20, decimal_places=2)
    CGSTPercentage = models.DecimalField(max_digits=20, decimal_places=2)
    SGSTPercentage = models.DecimalField(max_digits=20, decimal_places=2)
    IGSTPercentage = models.DecimalField(max_digits=20, decimal_places=2)
    CreatedOn = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "TC_OrderItems"


class T_Invoices(models.Model):

    Order = models.ForeignKey(T_Orders, on_delete=models.DO_NOTHING)
    InvoiceDate = models.DateField()
    Customer = models.ForeignKey(
        M_Parties, related_name='InvoicesCustomer', on_delete=models.DO_NOTHING)
    InvoiceNumber = models.IntegerField()
    FullInvoiceNumber = models.CharField(max_length=500)
    CustomerGSTTin = models.CharField(max_length=500)
    GrandTotal = models.DecimalField(max_digits=15, decimal_places=2)
    Party = models.ForeignKey(
        M_Parties, related_name='InvoicesParty', on_delete=models.DO_NOTHING)
    RoundOffAmount = models.DecimalField(max_digits=5, decimal_places=2)
    CreatedBy = models.IntegerField()
    CreatedOn = models.DateTimeField(auto_now_add=True)
    UpdatedBy = models.IntegerField()
    UpdatedOn = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "T_Invoices"


class TC_InvoiceItems(models.Model):
    Invoice = models.ForeignKey(
        T_Invoices, related_name='InvoiceItems', on_delete=models.CASCADE)
    Item = models.ForeignKey(M_Items, on_delete=models.DO_NOTHING)
    HSNCode = models.CharField(max_length=500)
    Quantity = models.DecimalField(max_digits=5, decimal_places=3)
    Unit = models.ForeignKey(
        MC_ItemUnits, related_name='InvoiceUnitID', on_delete=models.DO_NOTHING)
    BaseUnitQuantity = models.DecimalField(max_digits=15, decimal_places=3)
    QtyInKg = models.DecimalField(max_digits=10, decimal_places=3)
    QtyInNo = models.DecimalField(max_digits=10, decimal_places=3)
    QtyInBox = models.DecimalField(max_digits=10, decimal_places=3)
    MRP = models.DecimalField(max_digits=15, decimal_places=2)
    Rate = models.DecimalField(max_digits=15, decimal_places=2)
    BasicAmount = models.DecimalField(max_digits=15, decimal_places=2)
    TaxType = models.CharField(max_length=500)
    GSTPercentage = models.DecimalField(max_digits=5, decimal_places=2)
    GSTAmount = models.DecimalField(max_digits=15, decimal_places=2)
    Amount = models.DecimalField(max_digits=15, decimal_places=2)
    DiscountType = models.CharField(max_length=500)
    Discount = models.DecimalField(max_digits=10, decimal_places=2)
    DiscountAmount = models.DecimalField(max_digits=10, decimal_places=2)
    CGST = models.DecimalField(max_digits=5, decimal_places=2)
    SGST = models.DecimalField(max_digits=5, decimal_places=2)
    IGST = models.DecimalField(max_digits=5, decimal_places=2)
    CGSTPercentage = models.DecimalField(max_digits=5, decimal_places=2)
    SGSTPercentage = models.DecimalField(max_digits=5, decimal_places=2)
    IGSTPercentage = models.DecimalField(max_digits=5, decimal_places=2)
    CreatedOn = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "TC_InvoiceItems"


class TC_InvoiceItemBatches(models.Model):
    Invoice = models.ForeignKey(T_Invoices, on_delete=models.CASCADE)
    InvoiceItem = models.ForeignKey(
        TC_InvoiceItems, related_name='InvoiceItemBatches', on_delete=models.CASCADE)
    Item = models.ForeignKey(M_Items, on_delete=models.DO_NOTHING)
    BatchDate = models.DateField(blank=True, null=True)
    BatchCode = models.CharField(max_length=500)
    Quantity = models.DecimalField(max_digits=5, decimal_places=3)
    Unit = models.ForeignKey(
        MC_ItemUnits, related_name='InvoiceBatchUnitID', on_delete=models.DO_NOTHING)
    MRP = models.DecimalField(max_digits=15, decimal_places=2)
    CreatedOn = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "TC_InvoiceItemBatches"


class Abc(models.Model):
    phone_number = models.CharField(max_length=12, unique=True)
    otp = models.CharField(max_length=6, default=False)
    Name = models.CharField(max_length=100)
    SurName=models.CharField(max_length=100)
    pincode=models.IntegerField()
    class Meta:
        db_table = "Abc"
