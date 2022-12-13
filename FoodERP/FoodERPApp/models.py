from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from activity_log.models import UserMixin

# Create your models here.

def make_extra_data(request, response):
    return str(request.META)
   
class M_PartyType(models.Model):
    Name = models.CharField(max_length=100)
    IsSCM =models.BooleanField(default=False)
    IsDivision = models.BooleanField(default=False) 
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
        

class M_PriceList(models.Model):
    Name = models.CharField(max_length=100)
    '''PLPartyType means PriceListPartyType'''
    PLPartyType = models.ForeignKey(M_PartyType, related_name='PriceListPartyType', on_delete=models.DO_NOTHING)
    BasePriceListID = models.IntegerField()
    Company = models.ForeignKey(C_Companies, related_name='PriceListCompany', on_delete=models.DO_NOTHING)
    MkUpMkDn = models.BooleanField(default=False)
    CreatedBy = models.IntegerField()
    CreatedOn = models.DateTimeField(auto_now_add=True)
    UpdatedBy = models.IntegerField()
    UpdatedOn = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'M_PriceList'        

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

class M_AddressTypes(models.Model):
    Name = models.CharField(max_length=500)
    class Meta:
        db_table = "M_AddressTypes"
    
class M_Parties(models.Model):

    Name = models.CharField(max_length=500)
    PriceList = models.ForeignKey(M_PriceList, related_name='PartyPriceList', on_delete=models.DO_NOTHING,null=True)
    PartyType = models.ForeignKey(M_PartyType, related_name='PartyType', on_delete=models.PROTECT,blank=True)
    Company = models.ForeignKey(C_Companies, related_name='PartiesCompany', on_delete=models.PROTECT)
    Email = models.EmailField(max_length=200)
    MobileNo = models.BigIntegerField()
    AlternateContactNo = models.CharField(max_length=500, null=True, blank=True)
    State = models.ForeignKey(
        M_States, related_name='PartiesState', on_delete=models.DO_NOTHING)
    District = models.ForeignKey(
        M_Districts, related_name='PartiesDistrict', on_delete=models.DO_NOTHING)
    Taluka = models.IntegerField()
    City = models.IntegerField()
    GSTIN = models.CharField(max_length=500)
    PAN = models.CharField(max_length=500)
    '''IsDivison this Flag depends on Partytypes if PartyTypes's IsDivision Flag is Set M_Parties IsDivision also set '''
    IsDivision = models.BooleanField(default=False)
    MkUpMkDn = models.BooleanField(default=False)
    isActive = models.BooleanField(default=False)
    CreatedBy = models.IntegerField()
    CreatedOn = models.DateTimeField(auto_now_add=True)
    UpdatedBy = models.IntegerField()
    UpdatedOn = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'M_Parties'
        
class MC_PartyAddress(models.Model):
    
    Party = models.ForeignKey(M_Parties, related_name='PartyAddress', on_delete=models.CASCADE)
    AddressType = models.ForeignKey(M_AddressTypes, related_name='AddressType', on_delete=models.DO_NOTHING ,blank=True,null=True)
    Address = models.CharField(max_length=500)
    FSSAINo = models.CharField(max_length=500)
    FSSAIExipry = models.DateField(blank=True)
    PIN = models.CharField(max_length=500)
    IsDefault = models.BooleanField(default=False) 
    class Meta:
        db_table = 'MC_PartyAddress'
     
     

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


class M_Users(AbstractBaseUser, UserMixin):

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

    verbose_name = 'M_Users'    

    def __str__(self):
        return self.LoginName

    def __str__(self):
        return self.ID

def make_extra_data(request,response,body):
    a=str(body) +'!'+str(response)
    return a
    # return str(request.META)

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

class M_ControlTypeMaster(models.Model):
    
    Name = models.CharField(max_length=300)
    class Meta:
        db_table = "M_ControlTypeMaster"


class M_FieldValidations(models.Model):
    ControlType = models.ForeignKey(M_ControlTypeMaster, related_name='FieldControlType', on_delete=models.DO_NOTHING)
    Name = models.CharField(max_length=300)
    RegularExpression = models.CharField(max_length=300)
    
    class Meta:
        db_table = "M_FieldValidations"
         

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
    IsDivisionRequired = models.BooleanField(default=False)
    ''' IsEditPopuporComponent if flag set edit option open in Popup else go to component'''
    IsEditPopuporComponent = models.BooleanField(default=False)
    PageType = models.IntegerField()
    RelatedPageID = models.IntegerField()
    CreatedBy = models.IntegerField()
    CreatedOn = models.DateTimeField(auto_now_add=True)
    UpdatedBy = models.IntegerField()
    UpdatedOn = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "M_Pages"

class MC_PageFieldMaster(models.Model):
    
    ControlID = models.CharField(max_length=300)
    ControlType = models.ForeignKey(M_ControlTypeMaster, related_name='ControlType', on_delete=models.DO_NOTHING)
    FieldLabel = models.CharField(max_length=300,null=True,blank=True)
    DefaultSort = models.IntegerField()   
    IsCompulsory = models.BooleanField(default=False)      
    FieldValidation = models.ForeignKey(M_FieldValidations, related_name='FieldValidation', on_delete=models.DO_NOTHING)        
    ListPageSeq = models.IntegerField()
    ShowInListPage = models.BooleanField(default=False) 
    ShowInDownload = models.BooleanField(default=False)
    DownloadDefaultSelect = models.BooleanField(default=False) 
    InValidMsg = models.CharField(max_length=300,null=True,blank=True)
    Page = models.ForeignKey(M_Pages, related_name='PageFieldMaster', on_delete=models.CASCADE,null=True,blank=True)

    class Meta:
        db_table = "MC_PageFieldMaster"
        
class M_Roles(models.Model):

    Name = models.CharField(max_length=100)
    Description = models.CharField(max_length=100)
    isActive = models.BooleanField(default=False)
    isSCMRole = models.BooleanField(default=False)
    IsPartyConnection = models.BooleanField(default=False)
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
        C_Companies, related_name='RoleAccessCompany', on_delete=models.DO_NOTHING ,null=True,blank=True)
    Division = models.ForeignKey(
        M_Parties, related_name='RoleAccessDividion', on_delete=models.DO_NOTHING,null=True,blank=True)
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

class MC_RolesEmployeeTypes(models.Model):
    Role = models.ForeignKey(M_Roles, related_name='RoleEmployeeTypes', on_delete=models.CASCADE)
    EmployeeType = models.ForeignKey(M_EmployeeTypes, on_delete=models.DO_NOTHING)
    class Meta:
        db_table = "MC_RolesEmployeeTypes"
    

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

    Page = models.ForeignKey(M_Pages, related_name='PagePageAccess', on_delete=models.CASCADE)
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

class M_ImageTypes(models.Model):
    Name = models.CharField(max_length=500)
    CreatedBy = models.IntegerField(default=False)
    CreatedOn = models.DateTimeField(auto_now_add=True)
    UpdatedBy = models.IntegerField(default=False)
    UpdatedOn = models.DateTimeField(auto_now=True)
    class Meta:
        db_table = "M_ImageTypes"
        
            
class M_CategoryType(models.Model):
    Name = models.CharField(max_length=500)
    CreatedBy = models.IntegerField(default=False)
    CreatedOn = models.DateTimeField(auto_now_add=True)
    UpdatedBy = models.IntegerField(default=False)
    UpdatedOn = models.DateTimeField(auto_now=True)
    class Meta:
        db_table = "M_CategoryType"

class M_Category(models.Model):
    Name = models.CharField(max_length=500)
    CategoryType = models.ForeignKey(M_CategoryType, related_name='CategoryType', on_delete=models.DO_NOTHING)
    CreatedBy = models.IntegerField(default=False)
    CreatedOn = models.DateTimeField(auto_now_add=True)
    UpdatedBy = models.IntegerField(default=False)
    UpdatedOn = models.DateTimeField(auto_now=True)
    class Meta:
        db_table = "M_Category"
        
class M_GroupType(models.Model):
    Name = models.CharField(max_length=500)
    CreatedBy = models.IntegerField(default=False)
    CreatedOn = models.DateTimeField(auto_now_add=True)
    UpdatedBy = models.IntegerField(default=False)
    UpdatedOn = models.DateTimeField(auto_now=True)
    IsReserved = models.BooleanField(default=False)
    class Meta:
        db_table = "M_GroupType"

class M_Group(models.Model):
    Name = models.CharField(max_length=500)
    GroupType = models.ForeignKey(M_GroupType, related_name='GroupType', on_delete=models.DO_NOTHING)
    CreatedBy = models.IntegerField(default=False)
    CreatedOn = models.DateTimeField(auto_now_add=True)
    UpdatedBy = models.IntegerField(default=False)
    UpdatedOn = models.DateTimeField(auto_now=True)    
    class Meta:
        db_table = "M_Group"

class MC_SubGroup(models.Model):
    Name = models.CharField(max_length=500)
    Group = models.ForeignKey(M_Group, related_name='Group', on_delete=models.DO_NOTHING)
    CreatedBy = models.IntegerField(default=False)
    CreatedOn = models.DateTimeField(auto_now_add=True)
    UpdatedBy = models.IntegerField(default=False)
    UpdatedOn = models.DateTimeField(auto_now=True)    
    class Meta:
        db_table = "MC_SubGroup"                             

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
    Sequence = models.DecimalField(max_digits=5, decimal_places=2,null=True,blank=True)
    Company = models.ForeignKey(
        C_Companies, related_name='ItemCompany', on_delete=models.DO_NOTHING)
    BaseUnitID = models.ForeignKey(
        M_Units, related_name='BaseUnitID', on_delete=models.DO_NOTHING)
    BarCode = models.CharField(max_length=500,null=True,blank=True) 
    isActive = models.BooleanField(default=False)
    CanBeSold = models.BooleanField(default=False)
    CanBePurchase = models.BooleanField(default=False)
    CreatedBy = models.IntegerField(default=False)
    CreatedOn = models.DateTimeField(auto_now_add=True)
    UpdatedBy = models.IntegerField(default=False)
    UpdatedOn = models.DateTimeField(auto_now=True)
    class Meta:
        db_table = "M_Items"
        
        
class MC_ItemCategoryDetails(models.Model):
    Item = models.ForeignKey(M_Items, related_name='ItemCategoryDetails', on_delete=models.CASCADE)  
    CategoryType = models.ForeignKey(M_CategoryType, related_name='ItemCategoryType', on_delete=models.DO_NOTHING)
    Category = models.ForeignKey(M_Category, related_name='ItemCategory', on_delete=models.DO_NOTHING)
    CreatedOn = models.DateTimeField(auto_now_add=True)
    UpdatedOn = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = "MC_ItemCategoryDetails"

class MC_ItemGroupDetails(models.Model):
    Item = models.ForeignKey(M_Items, related_name='ItemGroupDetails', on_delete=models.CASCADE)  
    GroupType = models.ForeignKey(M_GroupType, related_name='ItemGroupType', on_delete=models.DO_NOTHING)
    Group = models.ForeignKey(M_Group, related_name='ItemGroup', on_delete=models.DO_NOTHING)
    SubGroup = models.ForeignKey(MC_SubGroup, related_name='ItemSubGroup',null=True, on_delete=models.DO_NOTHING)
    CreatedOn = models.DateTimeField(auto_now_add=True)
    UpdatedOn = models.DateTimeField(auto_now=True)
    class Meta:
        db_table = "MC_ItemGroupDetails"

     
class MC_ItemUnits(models.Model):
    Item = models.ForeignKey(
        M_Items, related_name='ItemUnitDetails', on_delete=models.CASCADE)
    UnitID = models.ForeignKey(
        M_Units, related_name='UnitID', on_delete=models.DO_NOTHING)
    BaseUnitQuantity = models.DecimalField(max_digits=5, decimal_places=3)
    IsDeleted = models.BooleanField(default=False)
    IsBase = models.BooleanField(default=False)
    class Meta:
        db_table = "MC_ItemUnits"                


class MC_ItemImages(models.Model):
    ImageType= models.ForeignKey(M_ImageTypes, related_name='ImageType', on_delete=models.DO_NOTHING)
    Item = models.ForeignKey(M_Items, related_name='ItemImagesDetails', on_delete=models.CASCADE,null=True,blank=True)
    Item_pic = models.TextField()
    class Meta:
        db_table = "MC_ItemImages" 

class MC_ItemDivisions(models.Model):
    Item = models.ForeignKey(M_Items, related_name='ItemDivisionDetails', on_delete=models.CASCADE)
    Division = models.ForeignKey(M_Parties, related_name='Division', on_delete=models.DO_NOTHING)
    class Meta:
        db_table = "MC_ItemDivisions"

class M_GSTHSNCode(models.Model):
    EffectiveDate = models.DateField()
    Item = models.ForeignKey(M_Items, related_name='ItemGSTHSNDetails', on_delete=models.CASCADE)
    GSTPercentage = models.DecimalField(max_digits=10, decimal_places=2)
    HSNCode = models.CharField(max_length=500)
    CommonID = models.IntegerField(null=True,blank=True)
    Company = models.ForeignKey(C_Companies, related_name='GstCompany', on_delete=models.DO_NOTHING)
    IsDeleted = models.BooleanField(default=False)
    CreatedBy = models.IntegerField()
    CreatedOn = models.DateTimeField(auto_now_add=True)
    UpdatedBy = models.IntegerField()
    UpdatedOn = models.DateTimeField(auto_now=True)
    class Meta:
        db_table = "M_GSTHSNCode"          
                   
class M_ItemShelfLife(models.Model):
    Name = models.CharField(max_length=500)
    Days = models.IntegerField(default=False)
    class Meta:
        db_table = "M_ItemShelfLife"

class M_MRPMaster(models.Model):
    '''Party(DivisionID) means M_Parties ID Where IsDivison Flag check'''
    Division =models.ForeignKey(M_Parties, related_name='MRPDivision', on_delete=models.DO_NOTHING,null=True,blank=True)
    'Customer means M_Parties ID'
    Party =models.ForeignKey(M_Parties, related_name='MRPParty', on_delete=models.DO_NOTHING,null=True,blank=True)
    EffectiveDate = models.DateField()
    Item = models.ForeignKey(M_Items, related_name='ItemMRPDetails', on_delete=models.CASCADE)
    MRP = models.DecimalField(max_digits=20, decimal_places=2)
    Company = models.ForeignKey(C_Companies, related_name='MRPCompany', on_delete=models.DO_NOTHING)
    CommonID = models.IntegerField(null=True,blank=True)
    IsDeleted = models.BooleanField(default=False)
    CreatedBy = models.IntegerField()
    CreatedOn = models.DateTimeField(auto_now_add=True)
    UpdatedBy = models.IntegerField()
    UpdatedOn = models.DateTimeField(auto_now=True)
     
    class Meta:
        db_table = "M_MRPMaster"

class M_MarginMaster(models.Model):
    CommonID = models.IntegerField(null=True,blank=True)
    PriceList =models.ForeignKey(M_PriceList, related_name='PriceList', on_delete=models.DO_NOTHING)
    Party =models.ForeignKey(M_Parties, related_name='MarginParty', on_delete=models.DO_NOTHING,null=True,blank=True)
    EffectiveDate = models.DateField()
    Item = models.ForeignKey(M_Items,related_name='ItemMarginDetails', on_delete=models.CASCADE)
    Margin = models.DecimalField(max_digits=20, decimal_places=2)
    Company = models.ForeignKey(C_Companies, related_name='MarginCompany', on_delete=models.DO_NOTHING)
    IsDeleted = models.BooleanField(default=False)
    CreatedBy = models.IntegerField()
    CreatedOn = models.DateTimeField(auto_now_add=True)
    UpdatedBy = models.IntegerField()
    UpdatedOn = models.DateTimeField(auto_now=True)
    class Meta:
        db_table = "M_MarginMaster"        


class M_TermsAndConditions(models.Model):
    Name = models.CharField(max_length=500)
    class Meta:
        db_table = "M_TermsAndConditions"
        
class MC_PartyItems(models.Model):
    Party =models.ForeignKey(M_Parties, related_name='Party', on_delete=models.DO_NOTHING)
    Item = models.ForeignKey(M_Items,related_name='PartyItem', on_delete=models.DO_NOTHING) 
    class Meta:
        db_table = "MC_PartyItems"

class MC_PartyPrefixs(models.Model):
    Party =models.ForeignKey(M_Parties, related_name='PartyPrefix', on_delete=models.CASCADE)
    Orderprefix = models.CharField(max_length=500 ,null=True,blank=True)
    Invoiceprefix = models.CharField(max_length=500 ,null=True,blank=True)
    Grnprefix = models.CharField(max_length=500 ,null=True,blank=True)
    Receiptprefix = models.CharField(max_length=500 ,null=True,blank=True)
    Challanprefix = models.CharField(max_length=500 ,null=True,blank=True)
    class Meta:
        db_table = "MC_PartyPrefixs"        
            

       
class T_Orders(models.Model):
    OrderDate = models.DateField()
    DeliveryDate = models.DateField()
    Customer = models.ForeignKey(M_Parties, related_name='OrderCustomer', on_delete=models.DO_NOTHING)
    Supplier = models.ForeignKey(M_Parties, related_name='OrderSupplier', on_delete=models.DO_NOTHING)
    OrderNo = models.IntegerField()
    FullOrderNumber = models.CharField(max_length=500)
    OrderAmount = models.DecimalField(max_digits=20, decimal_places=2)
    Description = models.CharField(max_length=500 ,null=True,blank=True)
    OrderType=models.IntegerField()  #1.SalesOrder OR 2.PurchesOrder
    POType=models.IntegerField()     #1.OpenOrder OR 2.RegulerOrder
    Division=models.ForeignKey(M_Parties, related_name='OrderDivision', on_delete=models.DO_NOTHING)
    BillingAddress=models.ForeignKey(MC_PartyAddress, related_name='OrderBillingAddress', on_delete=models.PROTECT)
    ShippingAddress=models.ForeignKey(MC_PartyAddress, related_name='OrderShippingAddress', on_delete=models.PROTECT)
    CreatedBy = models.IntegerField()
    CreatedOn = models.DateTimeField(auto_now_add=True)
    UpdatedBy = models.IntegerField()
    UpdatedOn = models.DateTimeField(auto_now=True)
    Inward = models.PositiveSmallIntegerField(default=0)
    class Meta:
        db_table = "T_Orders"


class TC_OrderItems(models.Model):
    Order = models.ForeignKey(T_Orders, related_name='OrderItem', on_delete=models.CASCADE)
    Item = models.ForeignKey(M_Items, related_name='Item', on_delete=models.DO_NOTHING)
    Quantity = models.DecimalField(max_digits=10, decimal_places=2)
    MRP = models.ForeignKey(M_MRPMaster, related_name='OrderItemMRP', on_delete=models.DO_NOTHING,null=True,blank=True)
    Rate = models.DecimalField(max_digits=10, decimal_places=2)
    Unit = models.ForeignKey(MC_ItemUnits, related_name='OrderUnitID', on_delete=models.PROTECT)
    BaseUnitQuantity = models.DecimalField(max_digits=5, decimal_places=3)
    GST = models.ForeignKey(M_GSTHSNCode, related_name='OrderItemGst', on_delete=models.PROTECT)
    Margin = models.ForeignKey(M_MarginMaster, related_name='OrderItemMargin', on_delete=models.DO_NOTHING,null=True,blank=True)
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
    IsDeleted = models.BooleanField(default=False)

    class Meta:
        db_table = "TC_OrderItems"

class TC_OrderTermsAndConditions(models.Model):
    Order = models.ForeignKey(T_Orders, related_name='OrderTermsAndConditions', on_delete=models.CASCADE)
    TermsAndCondition=models.ForeignKey(M_TermsAndConditions, related_name='TermsAndCondition', on_delete=models.DO_NOTHING)
    IsDeleted = models.BooleanField(default=False)
    CreatedOn = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "TC_OrderTermsAndConditions"


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


class M_Drivers(models.Model):
    Name =  models.CharField(max_length=300)
    DOB = models.DateField()
    Address = models.CharField(max_length=500)
    UID = models.CharField(max_length=500)
    class Meta:
        db_table = "M_Drivers"
    
    
class M_VehicleTypes(models.Model):
    Name= models.CharField(max_length=300)
    class Meta:
        db_table = "M_VehicleTypes" 

        
class M_Vehicles(models.Model):
    VehicleNumber= models.CharField(max_length=300)
    Description = models.CharField(max_length=300)
    Driver =models.ForeignKey(
        M_Drivers, related_name='DriverName', on_delete=models.DO_NOTHING) 
    VehicleType = models.ForeignKey(
        M_VehicleTypes, related_name='VehicleType', on_delete=models.DO_NOTHING) 
    class Meta:
        db_table = "M_Vehicles"

class MC_VehiclesDivisions(models.Model):
    Vehicle = models.ForeignKey(M_Vehicles, related_name='VehicleDivisions', on_delete=models.DO_NOTHING) 
    Division = models.ForeignKey(M_Parties, related_name='VDivision', on_delete=models.DO_NOTHING) 
    class Meta:
        db_table = "MC_VehiclesDivisions"

class  MC_PartySubParty(models.Model):
    Party = models.ForeignKey(M_Parties, related_name='MCParty', on_delete=models.CASCADE)
    SubParty = models.ForeignKey(M_Parties, related_name='MCSubParty', on_delete=models.CASCADE)
    CreatedBy = models.IntegerField(blank=True, null=True)
    CreatedOn = models.DateTimeField(auto_now_add=True)
    UpdatedBy = models.IntegerField(blank=True, null=True)
    UpdatedOn = models.DateTimeField(auto_now=True)
    class Meta:
        db_table = "MC_PartySubParty"
   
                                    
# class Abc(models.Model):
   
#   file = models.FileField(blank=False, null=False)
#   remark = models.CharField(max_length=20)
#   picture = models.ImageField(upload_to='ItemMaster',blank=True)

#   class Meta:
#         db_table = "Abc"
        

class T_GRNs(models.Model):
    
    GRNDate = models.DateField()
    Customer = models.ForeignKey(M_Parties, related_name='GRNCustomer', on_delete=models.PROTECT)
    GRNNumber = models.IntegerField()
    FullGRNNumber = models.CharField(max_length=500)
    GrandTotal = models.DecimalField(max_digits=15, decimal_places=2)
    Party = models.ForeignKey(M_Parties, related_name='GRNParty', on_delete=models.PROTECT)
    CreatedBy = models.IntegerField()
    CreatedOn = models.DateTimeField(auto_now_add=True)
    UpdatedBy = models.IntegerField()
    UpdatedOn = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "T_GRNs"

class TC_GRNReferences(models.Model):
    GRN = models.ForeignKey(
        T_GRNs, related_name='GRNReferences', on_delete=models.CASCADE)
    Order = models.ForeignKey(T_Orders, on_delete=models.DO_NOTHING ,null=True) 
    Invoice = models.ForeignKey(T_Invoices, on_delete=models.DO_NOTHING ,null=True)
    ChallanNo = models.CharField(max_length=500 ,null=True)
    class Meta:
        db_table = "TC_GRNReferences"    

class TC_GRNItems(models.Model):
    GRN = models.ForeignKey(T_GRNs, related_name='GRNItems', on_delete=models.CASCADE)
    Item = models.ForeignKey(M_Items, related_name='GItem', on_delete=models.DO_NOTHING)
    Quantity = models.DecimalField(max_digits=5, decimal_places=3)
    Unit = models.ForeignKey(MC_ItemUnits, related_name='GRNUnitID', on_delete=models.PROTECT)
    BaseUnitQuantity = models.DecimalField(max_digits=15, decimal_places=3)
    MRP = models.DecimalField(max_digits=15, decimal_places=2, null=True)
    ReferenceRate = models.DecimalField(max_digits=15, decimal_places=2, null=True)
    Rate = models.DecimalField(max_digits=15, decimal_places=2)
    BasicAmount = models.DecimalField(max_digits=15, decimal_places=2)
    TaxType = models.CharField(max_length=500)
    GST = models.ForeignKey(M_GSTHSNCode, related_name='GRNItemGst', on_delete=models.PROTECT)
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
    BatchDate = models.DateField(blank=True, null=True)
    BatchCode = models.CharField(max_length=500,blank=True, null=True)
    SystemBatchDate  = models.DateField()
    SystemBatchCode = models.CharField(max_length=500)
    CreatedOn = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "TC_GRNItems"

class O_BatchWiseLiveStock(models.Model):
    Item = models.ForeignKey(M_Items, on_delete=models.PROTECT)
    BatchDate = models.DateField(blank=True, null=True)
    BatchCode = models.CharField(max_length=500)
    SystemBatchDate = models.DateField()
    SystemBatchCode = models.CharField(max_length=500)
    Quantity = models.DecimalField(max_digits=5, decimal_places=3)
    Unit = models.ForeignKey(MC_ItemUnits, related_name='BatchWiseLiveStockUnitID', on_delete=models.PROTECT)
    BaseUnitQuantity = models.DecimalField(max_digits=15, decimal_places=3)
    MRP = models.DecimalField(max_digits=15, decimal_places=2,null=True)
    GST = models.ForeignKey(M_GSTHSNCode, related_name='ObatchwiseItemGst', on_delete=models.PROTECT)
    Rate = models.DecimalField(max_digits=15, decimal_places=2)
    Party = models.ForeignKey(M_Parties, related_name='BatchWiseLiveStockParty', on_delete=models.PROTECT)
    CreatedBy = models.IntegerField()
    CreatedOn = models.DateTimeField(auto_now_add=True)
   
    class Meta:
        db_table = "O_BatchWiseLiveStock"

class M_BillOfMaterial(models.Model):
    BomDate = models.DateField()
    Item = models.ForeignKey(M_Items, on_delete=models.PROTECT) 
    EstimatedOutputQty = models.DecimalField(max_digits=15, decimal_places=2)
    Unit = models.ForeignKey(MC_ItemUnits, related_name='BOMUnitID', on_delete=models.PROTECT)
    Comment = models.CharField(max_length=500 ,null=True,blank=True)
    IsActive = models.BooleanField(default=False)
    IsDelete = models.BooleanField(default=False)
    Company = models.ForeignKey(C_Companies, on_delete=models.PROTECT)
    CreatedBy = models.IntegerField()
    CreatedOn = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = "M_BillOfMaterial"
      
class MC_BillOfMaterialItems(models.Model): 
    BOM = models.ForeignKey(M_BillOfMaterial, related_name='BOMItems', on_delete=models.CASCADE) 
    Item = models.ForeignKey(M_Items, on_delete=models.PROTECT) 
    Quantity = models.DecimalField(max_digits=10, decimal_places=3)
    Unit = models.ForeignKey(MC_ItemUnits, related_name='BOMItemUnitID', on_delete=models.PROTECT)
    
    class Meta:
        db_table = "MC_BillOfMaterialItems"

class T_WorkOrder(models.Model):
    WorkOrderDate = models.DateField()
    Item = models.ForeignKey(M_Items, on_delete=models.PROTECT)
    Unit = models.ForeignKey(MC_ItemUnits, related_name='WorkOrderUnitID', on_delete=models.PROTECT)
    Bom = models.ForeignKey(M_BillOfMaterial, related_name='BomID', on_delete=models.PROTECT)
    NumberOfLot = models.IntegerField()
    Quantity = models.DecimalField(max_digits=10, decimal_places=3)
    Company = models.ForeignKey(C_Companies, on_delete=models.PROTECT)
    Party = models.ForeignKey(M_Parties, on_delete=models.PROTECT)
    CreatedBy = models.IntegerField()
    CreatedOn = models.DateTimeField(auto_now_add=True)
    UpdatedBy = models.IntegerField()
    UpdatedOn = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = "T_WorkOrder"

class TC_WorkOrderItems(models.Model):
    WorkOrder = models.ForeignKey(T_WorkOrder, related_name='WorkOrderItems', on_delete=models.CASCADE)
    Item = models.ForeignKey(M_Items, on_delete=models.PROTECT)
    BomQuantity = models.DecimalField(max_digits=10, decimal_places=3) 
    Quantity = models.DecimalField(max_digits=10, decimal_places=3) 
    Unit = models.ForeignKey(MC_ItemUnits, related_name='WorkOrderItemUnitID', on_delete=models.PROTECT)
    
    class Meta:
        db_table = "TC_WorkOrderItems"   
                    
class T_MaterialIssue(models.Model):
    MaterialIssueDate = models.DateField()
    Item = models.ForeignKey(M_Items, on_delete=models.PROTECT)
    NumberOfLot = models.IntegerField()
    LotQuantity = models.DecimalField(max_digits=10, decimal_places=3)
    Status=models.IntegerField()
    ReIssueID = models.IntegerField()
    IsReIssueID = models.BooleanField(default=False)
    Company = models.ForeignKey(C_Companies, on_delete=models.PROTECT)
    Party = models.ForeignKey(M_Parties, on_delete=models.PROTECT)
    CreatedBy = models.IntegerField()
    CreatedOn = models.DateTimeField(auto_now_add=True)
    UpdatedBy = models.IntegerField()
    UpdatedOn = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = "T_MaterialIssue"

class TC_MaterialIssueItems(models.Model):
    MaterialIssue = models.ForeignKey(T_MaterialIssue, related_name='MaterialIssueItems', on_delete=models.CASCADE)
    Item = models.ForeignKey(M_Items, on_delete=models.PROTECT)
    WorkOrderQuantity = models.DecimalField(max_digits=10, decimal_places=3) 
    IssueQuantity = models.DecimalField(max_digits=10, decimal_places=3) 
    Unit = models.ForeignKey(MC_ItemUnits, related_name='MaterialIssueUnitID', on_delete=models.PROTECT)
    BatchDate = models.DateField()
    BatchCode = models.CharField(max_length=500)
    BatchCodeQuantity = models.DecimalField(max_digits=10, decimal_places=3)
    SystemBatchDate = models.DateField()
    SupplierBatchCode = models.CharField(max_length=500)
    
    class Meta:
        db_table = "TC_MaterialIssueItems"
        
class TC_MaterialIssueWorkOrders(models.Model):
    WorkOrder = models.ForeignKey(T_WorkOrder, related_name='MaterialIssueWorkOrder', on_delete=models.CASCADE)
    MaterialIssue = models.ForeignKey(T_MaterialIssue,  on_delete=models.CASCADE)

    class Meta:
        db_table = "TC_MaterialIssueWorkOrders"   
         
class T_DeliveryChallans(models.Model):
    ChallanDate = models.DateField()
    Customer = models.ForeignKey(M_Parties, related_name='DeliveryCustomer', on_delete=models.PROTECT)
    ChallanNumber = models.IntegerField()
    FullChallanNumber = models.CharField(max_length=500)
    GrandTotal = models.DecimalField(max_digits=15, decimal_places=2)
    Party = models.ForeignKey(M_Parties, related_name='DeliveryParty', on_delete=models.PROTECT)
    CreatedBy = models.IntegerField()
    CreatedOn = models.DateTimeField(auto_now_add=True)
    UpdatedBy = models.IntegerField()
    UpdatedOn = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "T_DeliveryChallans"

class TC_DeliveryChallanReferences(models.Model):
    DeliveryChallan = models.ForeignKey(T_DeliveryChallans, related_name='DeliveryChallanReferences', on_delete=models.CASCADE)
    GRN = models.ForeignKey(T_GRNs, on_delete=models.PROTECT) 
  
    class Meta:
        db_table = "TC_DeliveryChallanReferences"    

class TC_DeliveryChallanItems(models.Model):
    DeliveryChallan = models.ForeignKey(T_DeliveryChallans, related_name='DeliveryChallanItems', on_delete=models.CASCADE)
    Item = models.ForeignKey(M_Items, on_delete=models.PROTECT)
    Quantity = models.DecimalField(max_digits=5, decimal_places=3)
    Unit = models.ForeignKey(MC_ItemUnits, related_name='DeliveryChallanUnitID', on_delete=models.PROTECT)
    BaseUnitQuantity = models.DecimalField(max_digits=15, decimal_places=3)
    MRP = models.DecimalField(max_digits=15, decimal_places=2)
    ReferenceRate = models.DecimalField(max_digits=15, decimal_places=2, null=True)
    Rate = models.DecimalField(max_digits=15, decimal_places=2, null=True)
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
    BatchDate = models.DateField(blank=True, null=True)
    BatchCode = models.CharField(max_length=500)
    CreatedOn = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "TC_DeliveryChallanItems"

     