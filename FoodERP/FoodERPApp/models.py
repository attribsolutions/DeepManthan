from django.db import models
from django.core.validators import MaxValueValidator,MinValueValidator
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.utils.translation import gettext_lazy as _
# from activity_log.models import UserMixin

# Create your models here.

# def make_extra_data(request, response):
#     return str(request.META)

def upload_to(instance,filename):
    return 'post/{filename}'.format(filename=filename) 
 
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
    IsSCM =models.BooleanField(default=False)
    CreatedBy = models.IntegerField()
    CreatedOn = models.DateTimeField(auto_now_add=True)
    UpdatedBy = models.IntegerField()
    UpdatedOn = models.DateTimeField(auto_now=True)
    CompanyGroup = models.ForeignKey(
        C_CompanyGroups, related_name='CompanyGroup', on_delete=models.PROTECT)

    class Meta:
        db_table = "C_Companies"
        
class M_PartyType(models.Model):
    Name = models.CharField(max_length=100)
    IsVendor =models.BooleanField(default=False)
    IsSCM =models.BooleanField(default=False)
    IsDivision = models.BooleanField(default=False) 
    IsAdminDivision = models.BooleanField(default=False) 
    CreatedBy = models.IntegerField()
    CreatedOn = models.DateTimeField(auto_now_add=True)
    UpdatedBy = models.IntegerField()
    UpdatedOn = models.DateTimeField(auto_now=True)
    IsRetailer = models.BooleanField(default=False)
    Company = models.ForeignKey(C_Companies, related_name='PartyTypeCompany',on_delete=models.PROTECT)
 
    class Meta:
        db_table = 'M_PartyType'
        

class M_GeneralMaster(models.Model):
    TypeID = models.IntegerField()
    Name = models.CharField(max_length=200)
    IsActive =models.BooleanField(default=False)
    CreatedBy = models.IntegerField()
    CreatedOn = models.DateTimeField(auto_now_add=True)
    UpdatedBy = models.IntegerField()
    UpdatedOn = models.DateTimeField(auto_now=True)
    Company = models.ForeignKey(C_Companies, related_name='Company', on_delete=models.PROTECT)


    class Meta:
        db_table = "M_GeneralMaster"
        
class M_ImportExcelTypes(models.Model):
    Name = models.CharField(max_length=200)
    IsPartyRequired= models.BooleanField(default=False)
    CreatedBy = models.IntegerField()
    CreatedOn = models.DateTimeField(auto_now_add=True)
    UpdatedBy = models.IntegerField()
    UpdatedOn = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = "M_ImportExcelTypes"

class M_PriceList(models.Model):
    Name = models.CharField(max_length=100)
    '''PLPartyType means PriceListPartyType'''
    BasePriceListID = models.IntegerField()
    MkUpMkDn = models.BooleanField(default=False)
    CalculationPath=models.CharField(max_length=200,null=True, blank=True)
    CreatedBy = models.IntegerField()
    CreatedOn = models.DateTimeField(auto_now_add=True)
    UpdatedBy = models.IntegerField()
    UpdatedOn = models.DateTimeField(auto_now=True)
    Company = models.ForeignKey(C_Companies, related_name='PriceListCompany', on_delete=models.PROTECT)
    PLPartyType = models.ForeignKey(M_PartyType, related_name='PriceListPartyType', on_delete=models.PROTECT)


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
    CreatedBy = models.IntegerField()
    CreatedOn = models.DateTimeField(auto_now_add=True)
    UpdatedBy = models.IntegerField()
    UpdatedOn = models.DateTimeField(auto_now=True)
    State = models.ForeignKey(
        M_States, related_name='DistrictState', on_delete=models.PROTECT)

    class Meta:
        db_table = "M_Districts"

class M_Cities(models.Model):
    Name = models.CharField(max_length=100)
    CreatedBy = models.IntegerField()
    CreatedOn = models.DateTimeField(auto_now_add=True)
    UpdatedBy = models.IntegerField()
    District = models.ForeignKey(M_Districts, related_name='CityDistrict', on_delete=models.PROTECT)

    class Meta:
        db_table="M_Cities"        
        
    
class M_Parties(models.Model):

    Name = models.CharField(max_length=500)
    Email = models.EmailField(max_length=200,null=True, blank=True)
    MobileNo = models.CharField(max_length=100, null=True, blank=True)
    AlternateContactNo = models.CharField(max_length=500, null=True, blank=True)
    SAPPartyCode = models.CharField(max_length=100, null=True, blank=True,unique=True)
    GSTIN = models.CharField(max_length=500,null=True, blank=True)
    PAN = models.CharField(max_length=500,null=True, blank=True)
    '''IsDivison this Flag depends on Partytypes if PartyTypes's IsDivision Flag is Set M_Parties IsDivision also set '''
    IsDivision = models.BooleanField(default=False)
    MkUpMkDn = models.BooleanField(default=False)
    isActive = models.BooleanField(default=False)
    CreatedBy = models.IntegerField()
    CreatedOn = models.DateTimeField(auto_now_add=True)
    UpdatedBy = models.IntegerField()
    UpdatedOn = models.DateTimeField(auto_now=True)
    Company = models.ForeignKey(C_Companies, related_name='PartiesCompany', on_delete=models.PROTECT)
    District = models.ForeignKey(M_Districts, related_name='PartiesDistrict', on_delete=models.PROTECT)
    PartyType = models.ForeignKey(M_PartyType, related_name='PartyType', on_delete=models.PROTECT,blank=True)
    PriceList = models.ForeignKey(M_PriceList, related_name='PartyPriceList', on_delete=models.PROTECT,null=True,blank=True)
    State = models.ForeignKey(M_States, related_name='PartiesState', on_delete=models.PROTECT)
    City = models.ForeignKey(M_Cities, related_name='PartiesCities', on_delete=models.PROTECT,null=True,blank=True)
    Latitude = models.CharField(max_length=500,null=True, blank=True)
    Longitude = models.CharField(max_length=500,null=True, blank=True)
    class Meta:
        db_table = 'M_Parties'
        
class MC_PartyAddress(models.Model): 
    Address = models.CharField(max_length=500)
    FSSAINo = models.CharField(max_length=500,null=True,blank=True)
    FSSAIExipry = models.DateField(null=True,blank=True)
    PIN = models.CharField(max_length=500)
    IsDefault = models.BooleanField(default=False) 
    fssaidocument=models.TextField(null=True,blank=True)
    Party = models.ForeignKey(M_Parties, related_name='PartyAddress', on_delete=models.CASCADE,null=True,blank=True)

    class Meta:
        db_table = 'MC_PartyAddress'
     
     

class M_EmployeeTypes(models.Model):
    Name = models.CharField(max_length=100)
    ''' If IsPartyConnection Flag is True then we are able to assign multipal Parties from Employee Master  '''
    IsSalesTeamMember =models.BooleanField(default=False)
    Description= models.CharField(max_length=100,blank=True,null=True)
    CreatedBy = models.IntegerField()
    CreatedOn = models.DateTimeField(auto_now_add=True)
    UpdatedBy = models.IntegerField()
    UpdatedOn = models.DateTimeField(auto_now=True)
    Company = models.ForeignKey(C_Companies,related_name='Emp_Company',on_delete=models.PROTECT)

    class Meta:
        db_table = "M_EmployeeTypes"


class M_Employees(models.Model):
    Name = models.CharField(max_length=100)
    Address = models.CharField(max_length=500)
    Mobile = models.CharField(max_length=100)
    email = models.EmailField(max_length=255,blank=True, null=True)
    DOB = models.CharField(max_length=100,blank=True, null=True)
    PAN = models.CharField(max_length=100,blank=True, null=True)
    AadharNo = models.CharField(max_length=100,blank=True, null=True)
    CreatedBy = models.IntegerField()
    CreatedOn = models.DateTimeField(auto_now_add=True)
    UpdatedBy = models.IntegerField()
    UpdatedOn = models.DateTimeField(auto_now=True)
    Company = models.ForeignKey(C_Companies, related_name='EmployeesCompany', on_delete=models.PROTECT)
    District = models.ForeignKey(M_Districts, related_name='EmployeesDistrict', on_delete=models.PROTECT)
    EmployeeType = models.ForeignKey(M_EmployeeTypes, related_name='EmployeeType', on_delete=models.PROTECT)
    State = models.ForeignKey(M_States, related_name='EmployeesState', on_delete=models.PROTECT)
    City = models.ForeignKey(M_Cities, related_name='EmployeesCity', on_delete=models.PROTECT)
    PIN = models.CharField(max_length=500,null=True,blank=True)
  
    class Meta:
        db_table = "M_Employees"

class M_Routes(models.Model):
    Name = models.CharField(max_length=500)
    Sunday = models.BooleanField(default=False,blank=True, null=True)
    Monday = models.BooleanField(default=False,blank=True, null=True)
    Tuesday = models.BooleanField(default=False,blank=True, null=True)
    Wednesday = models.BooleanField(default=False,blank=True, null=True)
    Thursday = models.BooleanField(default=False,blank=True, null=True)
    Friday = models.BooleanField(default=False,blank=True, null=True)
    Saturday = models.BooleanField(default=False,blank=True, null=True)
    IsActive =models.BooleanField(default=False)
    CreatedBy = models.IntegerField()
    CreatedOn = models.DateTimeField(auto_now_add=True)
    UpdatedBy = models.IntegerField()
    UpdatedOn = models.DateTimeField(auto_now=True)
    Company = models.ForeignKey(C_Companies, related_name='RCompany', on_delete=models.PROTECT)
    Party = models.ForeignKey(M_Parties, related_name='RParty', on_delete=models.PROTECT)

    class Meta:
        db_table = "M_Routes"
        
class M_Salesman(models.Model):
    Name = models.CharField(max_length=500)
    MobileNo = models.BigIntegerField()
    IsActive =models.BooleanField(default=False)
    CreatedBy = models.IntegerField()
    CreatedOn = models.DateTimeField(auto_now_add=True)
    UpdatedBy = models.IntegerField()
    UpdatedOn = models.DateTimeField(auto_now=True)
    Company = models.ForeignKey(C_Companies, related_name='SCompany', on_delete=models.PROTECT)
    Party = models.ForeignKey(M_Parties, related_name='SParty', on_delete=models.PROTECT)

    class Meta:
        db_table = "M_Salesman"
        
class MC_EmployeeParties(models.Model):
    Employee = models.ForeignKey(M_Employees, related_name='EmployeeParties', on_delete=models.CASCADE)
    Party = models.ForeignKey(M_Parties, related_name='Employeeparty',  on_delete=models.PROTECT ,null=True)

    class Meta:
        db_table = "MC_EmployeeParties"

class MC_ManagementParties(models.Model):
    Employee = models.ForeignKey(M_Employees, related_name='ManagementEmployee', on_delete=models.PROTECT)
    Party = models.ForeignKey(M_Parties, related_name='ManagementEmpparty',  on_delete=models.PROTECT)

    class Meta:
        db_table = "MC_ManagementParties"        

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


# class M_Users(AbstractBaseUser, UserMixin):
class M_Users(AbstractBaseUser):
    LoginName = models.CharField(max_length=100, unique=True)
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
    Employee = models.ForeignKey(M_Employees, related_name='UserEmployee', on_delete=models.PROTECT)


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
    Name = models.CharField(max_length=300)
    RegularExpression = models.CharField(max_length=300)
    ControlType = models.ForeignKey(M_ControlTypeMaster, related_name='FieldControlType', on_delete=models.PROTECT)

    class Meta:
        db_table = "M_FieldValidations"
        
         
class M_PageType(models.Model):
    Name = models.CharField(max_length=500, blank=True)
    ''' IsAvailableForAccess if flag true this page show on role access page dropdown'''
    IsAvailableForAccess = models.BooleanField(default=False)
    CreatedBy = models.IntegerField()
    CreatedOn = models.DateTimeField(auto_now_add=True)
    UpdatedBy = models.IntegerField()
    UpdatedOn = models.DateTimeField(auto_now=True)
    class Meta:
        db_table = "M_PageType"
    
class M_Pages(models.Model):
    PageHeading = models.CharField(max_length=500, blank=True)
    Name = models.CharField(max_length=100)
    PageDescription = models.CharField(max_length=500, blank=True)
    PageDescriptionDetails = models.CharField(max_length=500, blank=True)
    isActive = models.BooleanField(default=False)
    DisplayIndex = models.IntegerField()
    Icon = models.CharField(max_length=100)
    ActualPagePath = models.CharField(max_length=100)
    IsDivisionRequired = models.BooleanField(default=False)
    ''' IsEditPopuporComponent if flag set edit option open in Popup else go to component'''
    IsEditPopuporComponent = models.BooleanField(default=False)
    PageType = models.IntegerField()
    RelatedPageID = models.IntegerField()
    CountLabel = models.BooleanField(default=False)
    ShowCountLabel = models.CharField(max_length=200,null=True,blank=True)
    CreatedBy = models.IntegerField()
    CreatedOn = models.DateTimeField(auto_now_add=True)
    UpdatedBy = models.IntegerField()
    UpdatedOn = models.DateTimeField(auto_now=True)
    Module = models.ForeignKey(H_Modules, related_name='PagesModule', on_delete=models.PROTECT)

    class Meta:
        db_table = "M_Pages"

class MC_PageFieldMaster(models.Model):
    
    ControlID = models.CharField(max_length=300)
    FieldLabel = models.CharField(max_length=300,null=True,blank=True)
    DefaultSort = models.IntegerField()   
    IsCompulsory = models.BooleanField(default=False)      
    ListPageSeq = models.IntegerField()
    ShowInListPage = models.BooleanField(default=False) 
    ShowInDownload = models.BooleanField(default=False)
    DownloadDefaultSelect = models.BooleanField(default=False) 
    InValidMsg = models.CharField(max_length=300,null=True,blank=True)
    Alignment = models.CharField(max_length=300,null=True,blank=True)
    ControlType = models.ForeignKey(M_ControlTypeMaster, related_name='ControlType', on_delete=models.PROTECT)
    FieldValidation = models.ForeignKey(M_FieldValidations, related_name='FieldValidation', on_delete=models.PROTECT)        
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
    Company = models.ForeignKey(C_Companies, related_name='RoleCompany', on_delete=models.PROTECT)

    class Meta:
        db_table = "M_Roles"

        def __str__(self):
            return self.Name


class MC_UserRoles(models.Model):

    Party = models.ForeignKey(M_Parties, related_name='userparty',  on_delete=models.PROTECT, null=True)
    Role = models.ForeignKey(M_Roles, related_name='Role',on_delete=models.PROTECT)
    User = models.ForeignKey(M_Users, related_name='UserRole',  on_delete=models.CASCADE)

    class Meta:
        db_table = "MC_UserRoles"


class M_RoleAccess(models.Model):

    CreatedBy = models.IntegerField()
    CreatedOn = models.DateTimeField(auto_now_add=True)
    UpdatedBy = models.IntegerField()
    UpdatedOn = models.DateTimeField(auto_now=True)
    Company = models.ForeignKey(C_Companies, related_name='RoleAccessCompany', on_delete=models.PROTECT ,null=True,blank=True)
    Division = models.ForeignKey(M_Parties, related_name='RoleAccessDividion', on_delete=models.PROTECT,null=True,blank=True)
    Modules = models.ForeignKey(H_Modules, related_name='RoleAccessModules', on_delete=models.PROTECT)
    Pages = models.ForeignKey(M_Pages, related_name='RoleAccessPages', on_delete=models.PROTECT)
    Role = models.ForeignKey(M_Roles, related_name='RoleAccessRole', on_delete=models.PROTECT)
    
    class Meta:
        db_table = "M_RoleAccess"

class MC_RolesEmployeeTypes(models.Model):
    EmployeeType = models.ForeignKey(M_EmployeeTypes, on_delete=models.PROTECT)
    Role = models.ForeignKey(M_Roles, related_name='RoleEmployeeTypes', on_delete=models.CASCADE)

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

    Access = models.ForeignKey(H_PageAccess, on_delete=models.PROTECT)
    Page = models.ForeignKey(M_Pages, related_name='PagePageAccess', on_delete=models.CASCADE)

    class Meta:
        db_table = "MC_PagePageAccess"

# RoleAccess child table

class MC_RolePageAccess(models.Model):
    PageAccess = models.ForeignKey(H_PageAccess, related_name='RolePageAccess', on_delete=models.PROTECT)
    RoleAccess = models.ForeignKey(M_RoleAccess, related_name='RoleAccess', on_delete=models.CASCADE)

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
    CreatedBy = models.IntegerField(default=False)
    CreatedOn = models.DateTimeField(auto_now_add=True)
    UpdatedBy = models.IntegerField(default=False)
    UpdatedOn = models.DateTimeField(auto_now=True)
    CategoryType = models.ForeignKey(M_CategoryType, related_name='CategoryType', on_delete=models.PROTECT)

    class Meta:
        db_table = "M_Category"
        
class M_GroupType(models.Model):
    Name = models.CharField(max_length=500)
    CreatedBy = models.IntegerField(default=False)
    CreatedOn = models.DateTimeField(auto_now_add=True)
    UpdatedBy = models.IntegerField(default=False)
    UpdatedOn = models.DateTimeField(auto_now=True)
    IsReserved = models.BooleanField(default=False)
    Sequence = models.DecimalField(max_digits=5, decimal_places=2,null=True,blank=True)
    class Meta:
        db_table = "M_GroupType"

class M_Group(models.Model):
    Name = models.CharField(max_length=500)
    CreatedBy = models.IntegerField(default=False)
    CreatedOn = models.DateTimeField(auto_now_add=True)
    UpdatedBy = models.IntegerField(default=False)
    UpdatedOn = models.DateTimeField(auto_now=True)    
    GroupType = models.ForeignKey(M_GroupType, related_name='GroupType', on_delete=models.PROTECT)
    Sequence = models.DecimalField(max_digits=5, decimal_places=2,null=True,blank=True)
    class Meta:
        db_table = "M_Group"

class MC_SubGroup(models.Model):
    Name = models.CharField(max_length=500)
    CreatedBy = models.IntegerField(default=False)
    CreatedOn = models.DateTimeField(auto_now_add=True)
    UpdatedBy = models.IntegerField(default=False)
    UpdatedOn = models.DateTimeField(auto_now=True)    
    Group = models.ForeignKey(M_Group, related_name='Group', on_delete=models.PROTECT)
    Sequence = models.DecimalField(max_digits=5, decimal_places=2,null=True,blank=True)
    class Meta:
        db_table = "MC_SubGroup"                             

class M_Units(models.Model):
    Name = models.CharField(max_length=500)
    SAPUnit =models.CharField(max_length=500)
    EwayBillUnit =models.CharField(max_length=500,null=True,blank=True)
    CreatedBy = models.IntegerField()
    CreatedOn = models.DateTimeField(auto_now_add=True)
    UpdatedBy = models.IntegerField()
    UpdatedOn = models.DateTimeField(auto_now=True)
    class Meta:
        db_table = "M_Units"


class M_Drivers(models.Model):
    Name =  models.CharField(max_length=300)
    DOB = models.DateField()
    Address = models.CharField(max_length=500)
    CreatedBy = models.IntegerField()
    CreatedOn = models.DateTimeField(auto_now_add=True)
    UpdatedBy = models.IntegerField()
    UpdatedOn = models.DateTimeField(auto_now=True)
    Company = models.ForeignKey(C_Companies, related_name='DCompany', on_delete=models.PROTECT)
    Party = models.ForeignKey(M_Parties, related_name='DParty', on_delete=models.PROTECT)
 
    class Meta:
        db_table = "M_Drivers"
    
class M_VehicleTypes(models.Model):
    Name= models.CharField(max_length=300)
    Company = models.ForeignKey(C_Companies, related_name='VTCompany', on_delete=models.PROTECT)
    class Meta:
        db_table = "M_VehicleTypes" 
    
class M_Vehicles(models.Model):
    VehicleNumber= models.CharField(max_length=300)
    Description = models.CharField(max_length=300)
    CreatedBy = models.IntegerField()
    CreatedOn = models.DateTimeField(auto_now_add=True)
    UpdatedBy = models.IntegerField()
    UpdatedOn = models.DateTimeField(auto_now=True)
    Company = models.ForeignKey(C_Companies, related_name='VCompany', on_delete=models.PROTECT)
    Party = models.ForeignKey(M_Parties, related_name='VParty', on_delete=models.PROTECT)
    VehicleType = models.ForeignKey(M_VehicleTypes, related_name='VehicleType', on_delete=models.PROTECT)

    class Meta:
        db_table = "M_Vehicles"
              
class M_Items(models.Model):
    Name = models.CharField(max_length=500)
    ShortName = models.CharField(max_length=500)
    Sequence = models.DecimalField(max_digits=5, decimal_places=2,null=True,blank=True)
    BarCode = models.CharField(max_length=500,null=True,blank=True) 
    SAPItemCode = models.CharField(max_length=100,unique=True)
    isActive = models.BooleanField(default=False)
    IsSCM = models.BooleanField(default=False)
    CanBeSold = models.BooleanField(default=False)
    CanBePurchase = models.BooleanField(default=False)
    BrandName = models.CharField(max_length=500,null=True,blank=True)
    Tag = models.CharField(max_length=1000,null=True,blank=True)
    CreatedBy = models.IntegerField(default=False)
    CreatedOn = models.DateTimeField(auto_now_add=True)
    UpdatedBy = models.IntegerField(default=False)
    UpdatedOn = models.DateTimeField(auto_now=True)
    BaseUnitID = models.ForeignKey(M_Units, related_name='BaseUnitID', on_delete=models.PROTECT)
    Company = models.ForeignKey(C_Companies, related_name='ItemCompany', on_delete=models.PROTECT)
    Breadth = models.CharField(max_length=200,null=True,blank=True)
    Grammage = models.CharField(max_length=200,null=True,blank=True)
    Height = models.CharField(max_length=200,null=True,blank=True)
    Length = models.CharField(max_length=200,null=True,blank=True)
    StoringCondition = models.CharField(max_length=200,null=True,blank=True)
    Budget = models.DecimalField(max_digits=20, decimal_places=2,null=True,blank=True)
    class Meta:
        db_table = "M_Items"
        
        
class MC_ItemCategoryDetails(models.Model):
    CreatedOn = models.DateTimeField(auto_now_add=True)
    UpdatedOn = models.DateTimeField(auto_now=True)
    Category = models.ForeignKey(M_Category, related_name='ItemCategory', on_delete=models.PROTECT)
    CategoryType = models.ForeignKey(M_CategoryType, related_name='ItemCategoryType', on_delete=models.PROTECT)
    Item = models.ForeignKey(M_Items, related_name='ItemCategoryDetails', on_delete=models.CASCADE)  
    
    class Meta:
        db_table = "MC_ItemCategoryDetails"

class MC_ItemGroupDetails(models.Model):
    CreatedOn = models.DateTimeField(auto_now_add=True)
    UpdatedOn = models.DateTimeField(auto_now=True)
    Group = models.ForeignKey(M_Group, related_name='ItemGroup', on_delete=models.PROTECT)
    GroupType = models.ForeignKey(M_GroupType, related_name='ItemGroupType', on_delete=models.PROTECT)
    Item = models.ForeignKey(M_Items, related_name='ItemGroupDetails', on_delete=models.CASCADE)  
    SubGroup = models.ForeignKey(MC_SubGroup, related_name='ItemSubGroup',null=True, on_delete=models.PROTECT)
    class Meta:
        db_table = "MC_ItemGroupDetails"

class MC_ItemUnits(models.Model):
    BaseUnitQuantity = models.DecimalField(max_digits=15, decimal_places=3)
    IsDeleted = models.BooleanField(default=False)
    IsBase = models.BooleanField(default=False)
    PODefaultUnit = models.BooleanField(default=False)
    SODefaultUnit = models.BooleanField(default=False)
    BaseUnitConversion = models.CharField(max_length=500)
    Item = models.ForeignKey(M_Items, related_name='ItemUnitDetails', on_delete=models.CASCADE)
    UnitID = models.ForeignKey(M_Units, related_name='UnitID', on_delete=models.PROTECT)

    class Meta:
        db_table = "MC_ItemUnits"                


class MC_ItemImages(models.Model):
    Item_pic = models.TextField()
    ImageType= models.ForeignKey(M_ImageTypes, related_name='ImageType', on_delete=models.PROTECT)
    Item = models.ForeignKey(M_Items, related_name='ItemImagesDetails', on_delete=models.CASCADE,null=True,blank=True)
    class Meta:
        db_table = "MC_ItemImages" 

class M_GSTHSNCode(models.Model):
    EffectiveDate = models.DateField()
    GSTPercentage = models.DecimalField(max_digits=10, decimal_places=2)
    HSNCode = models.CharField(max_length=500)
    CommonID = models.IntegerField(null=True,blank=True)
    IsDeleted = models.BooleanField(default=False)
    CreatedBy = models.IntegerField()
    CreatedOn = models.DateTimeField(auto_now_add=True)
    UpdatedBy = models.IntegerField()
    UpdatedOn = models.DateTimeField(auto_now=True)
    Company = models.ForeignKey(C_Companies, related_name='GstCompany', on_delete=models.PROTECT)
    Item = models.ForeignKey(M_Items, related_name='ItemGSTHSNDetails', on_delete=models.CASCADE)

    class Meta:
        db_table = "M_GSTHSNCode"          
                   
class MC_ItemShelfLife(models.Model):
    Days = models.IntegerField(default=False)
    IsDeleted = models.BooleanField(default=False)
    CreatedBy = models.IntegerField()
    CreatedOn = models.DateTimeField(auto_now_add=True)
    UpdatedBy = models.IntegerField()
    UpdatedOn = models.DateTimeField(auto_now=True)
    Item = models.ForeignKey(M_Items, related_name='ItemShelfLife', on_delete=models.CASCADE)

    class Meta:
        db_table = "MC_ItemShelfLife"

class M_MRPMaster(models.Model):
    EffectiveDate = models.DateField()
    MRP = models.DecimalField(max_digits=20, decimal_places=2)
    CommonID = models.IntegerField(null=True,blank=True)
    IsDeleted = models.BooleanField(default=False)
    CreatedBy = models.IntegerField()
    CreatedOn = models.DateTimeField(auto_now_add=True)
    UpdatedBy = models.IntegerField()
    UpdatedOn = models.DateTimeField(auto_now=True)
    Company = models.ForeignKey(C_Companies, related_name='MRPCompany', on_delete=models.PROTECT)
    '''Party(DivisionID) means M_Parties ID Where IsDivison Flag check'''
    Division =models.ForeignKey(M_Parties, related_name='MRPDivision', on_delete=models.PROTECT,null=True,blank=True)
    Item = models.ForeignKey(M_Items, related_name='ItemMRPDetails', on_delete=models.CASCADE)
    'Customer means M_Parties ID'
    Party =models.ForeignKey(M_Parties, related_name='MRPParty', on_delete=models.PROTECT,null=True,blank=True)

    class Meta:
        db_table = "M_MRPMaster"

class M_MarginMaster(models.Model):
    CommonID = models.IntegerField(null=True,blank=True)
    EffectiveDate = models.DateField()
    Margin = models.DecimalField(max_digits=20, decimal_places=2)
    IsDeleted = models.BooleanField(default=False)
    CreatedBy = models.IntegerField()
    CreatedOn = models.DateTimeField(auto_now_add=True)
    UpdatedBy = models.IntegerField()
    UpdatedOn = models.DateTimeField(auto_now=True)
    Company = models.ForeignKey(C_Companies, related_name='MarginCompany', on_delete=models.PROTECT)
    Item = models.ForeignKey(M_Items,related_name='ItemMarginDetails', on_delete=models.CASCADE)
    Party =models.ForeignKey(M_Parties, related_name='MarginParty', on_delete=models.PROTECT,null=True,blank=True)
    PriceList =models.ForeignKey(M_PriceList, related_name='PriceList', on_delete=models.PROTECT)

    class Meta:
        db_table = "M_MarginMaster" 
               
class M_POType(models.Model): 
    Name = models.CharField(max_length=500)
    CreatedBy = models.IntegerField()
    CreatedOn = models.DateTimeField(auto_now_add=True)
    UpdatedBy = models.IntegerField()
    UpdatedOn = models.DateTimeField(auto_now=True)
    Company=models.ForeignKey(C_Companies,  on_delete=models.PROTECT)		
    Division=models.ForeignKey(M_Parties, on_delete=models.PROTECT)

    class Meta:
        db_table = "M_POType"


class M_TermsAndConditions(models.Model):
    Name = models.CharField(max_length=500)
    IsDefault = models.BooleanField(default=False)
    CreatedBy = models.IntegerField(blank=True, null=True)
    CreatedOn = models.DateTimeField(auto_now_add=True)
    UpdatedBy = models.IntegerField(blank=True, null=True)
    UpdatedOn = models.DateTimeField(auto_now=True)
    class Meta:
        db_table = "M_TermsAndConditions"
        
class MC_PartyItems(models.Model):
    Item = models.ForeignKey(M_Items,related_name='ItemDivisionDetails', on_delete=models.PROTECT) 
    Party =models.ForeignKey(M_Parties, related_name='Party', on_delete=models.PROTECT)

    class Meta:
        db_table = "MC_PartyItems"

class MC_PartyPrefixs(models.Model):
    Orderprefix = models.CharField(max_length=500 ,null=True,blank=True)
    Demandprefix = models.CharField(max_length=500 ,null=True,blank=True)
    Invoiceprefix = models.CharField(max_length=500 ,null=True,blank=True)
    Grnprefix = models.CharField(max_length=500 ,null=True,blank=True)
    Receiptprefix = models.CharField(max_length=500 ,null=True,blank=True)
    Creditprefix = models.CharField(max_length=500 ,null=True,blank=True)
    Debitprefix = models.CharField(max_length=500 ,null=True,blank=True)
    Challanprefix = models.CharField(max_length=500 ,null=True,blank=True)
    WorkOrderprefix = models.CharField(max_length=500 ,null=True,blank=True)
    MaterialIssueprefix = models.CharField(max_length=500 ,null=True,blank=True)
    IBChallanprefix = models.CharField(max_length=500 ,null=True,blank=True)
    IBInwardprefix = models.CharField(max_length=500 ,null=True,blank=True)
    PurchaseReturnprefix = models.CharField(max_length=500 ,null=True,blank=True)
    Party =models.ForeignKey(M_Parties, related_name='PartyPrefix', on_delete=models.CASCADE)

    class Meta:
        db_table = "MC_PartyPrefixs"        
            
       
class T_Orders(models.Model):
    OrderDate = models.DateField()
    DeliveryDate = models.DateField()
    OrderNo = models.IntegerField()
    FullOrderNumber = models.CharField(max_length=500)
    OrderAmount = models.DecimalField(max_digits=20, decimal_places=2)
    Description = models.CharField(max_length=500 ,null=True,blank=True)
    OrderType=models.IntegerField()  #1.SalesOrder OR 2.PurchesOrder
    POFromDate = models.DateField(null=True,blank=True)
    POToDate = models.DateField(null=True,blank=True)
    CreatedBy = models.IntegerField()
    CreatedOn = models.DateTimeField(auto_now_add=True)
    UpdatedBy = models.IntegerField()
    UpdatedOn = models.DateTimeField(auto_now=True)
    BillingAddress=models.ForeignKey(MC_PartyAddress, related_name='OrderBillingAddress', on_delete=models.PROTECT)
    Customer = models.ForeignKey(M_Parties, related_name='OrderCustomer', on_delete=models.PROTECT)
    Division=models.ForeignKey(M_Parties, related_name='OrderDivision', on_delete=models.PROTECT)
    POType=models.ForeignKey(M_POType, related_name='OrderPOType', on_delete=models.PROTECT) #1.OpenOrder OR 2.RegulerOrder
    ShippingAddress=models.ForeignKey(MC_PartyAddress, related_name='OrderShippingAddress', on_delete=models.PROTECT)
    Supplier = models.ForeignKey(M_Parties, related_name='OrderSupplier', on_delete=models.PROTECT)
    SAPResponse =models.CharField(max_length=500 ,null=True)
    IsConfirm = models.BooleanField(default=False) 

    # Inward = models.PositiveSmallIntegerField(default=0)
    class Meta:
        db_table = "T_Orders"


class TC_OrderItems(models.Model):
    Comment= models.CharField(max_length=300,blank=True,null=True)
    Quantity = models.DecimalField(max_digits=15, decimal_places=3)
    MRPValue = models.DecimalField(max_digits=20, decimal_places=2)
    Rate = models.DecimalField(max_digits=10, decimal_places=2)
    BaseUnitQuantity = models.DecimalField(max_digits=15, decimal_places=3)
    GSTPercentage = models.DecimalField(max_digits=10, decimal_places=2)
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
    DeletedOn = models.DateTimeField(auto_now=True)
    GST = models.ForeignKey(M_GSTHSNCode, related_name='OrderItemGst', on_delete=models.PROTECT)
    Item = models.ForeignKey(M_Items, related_name='Item', on_delete=models.PROTECT)
    MRP = models.ForeignKey(M_MRPMaster, related_name='OrderItemMRP', on_delete=models.PROTECT,null=True,blank=True)
    Margin = models.ForeignKey(M_MarginMaster, related_name='OrderItemMargin', on_delete=models.PROTECT,null=True,blank=True)
    Order = models.ForeignKey(T_Orders, related_name='OrderItem', on_delete=models.CASCADE)
    Unit = models.ForeignKey(MC_ItemUnits, related_name='OrderUnitID', on_delete=models.PROTECT)
    QtyInNo = models.DecimalField(max_digits=30, decimal_places=20)
    QtyInKg = models.DecimalField(max_digits=30, decimal_places=20)
    QtyInBox = models.DecimalField(max_digits=30, decimal_places=20)
    DiscountType = models.CharField(max_length=500,blank=True, null=True)
    Discount = models.DecimalField(max_digits=20, decimal_places=2,blank=True, null=True)
    DiscountAmount = models.DecimalField(max_digits=20, decimal_places=2,blank=True, null=True)

    class Meta:
        db_table = "TC_OrderItems"

class TC_OrderTermsAndConditions(models.Model):
    IsDeleted = models.BooleanField(default=False)
    CreatedOn = models.DateTimeField(auto_now_add=True)
    Order = models.ForeignKey(T_Orders, related_name='OrderTermsAndConditions', on_delete=models.CASCADE)
    TermsAndCondition=models.ForeignKey(M_TermsAndConditions, related_name='TermsAndCondition', on_delete=models.PROTECT,blank=True,null=True)

    class Meta:
        db_table = "TC_OrderTermsAndConditions"

class O_LiveBatches(models.Model):
    BatchDate = models.DateField(blank=True, null=True)
    BatchCode = models.CharField(max_length=500)
    SystemBatchDate = models.DateField()
    SystemBatchCode = models.CharField(max_length=500)
    Rate = models.DecimalField(max_digits=20, decimal_places=2,null=True)
    ItemExpiryDate=models.DateField()
    OriginalBatchBaseUnitQuantity = models.DecimalField(max_digits=15, decimal_places=3)
    GST = models.ForeignKey(M_GSTHSNCode, related_name='ObatchwiseItemGst',null=True,on_delete=models.PROTECT)
    MRP = models.ForeignKey(M_MRPMaster, related_name='ObatchwiseItemMrp', on_delete=models.PROTECT,null=True,blank=True)
    MRPValue =  models.DecimalField(max_digits=20, decimal_places=2)
    GSTPercentage = models.DecimalField(max_digits=20, decimal_places=2)
    
    class Meta:
        db_table = "O_LiveBatches"        

class T_Invoices(models.Model):
    InvoiceDate = models.DateField()
    InvoiceNumber = models.IntegerField()
    FullInvoiceNumber = models.CharField(max_length=500)
    GrandTotal = models.DecimalField(max_digits=20, decimal_places=2)
    RoundOffAmount = models.DecimalField(max_digits=15, decimal_places=2)
    CreatedBy = models.IntegerField()
    CreatedOn = models.DateTimeField(auto_now_add=True)
    UpdatedBy = models.IntegerField()
    UpdatedOn = models.DateTimeField(auto_now=True)
    Customer = models.ForeignKey(M_Parties, related_name='InvoicesCustomer', on_delete=models.PROTECT)
    Driver = models.ForeignKey(M_Drivers, related_name='InvoiceDriver',on_delete=models.PROTECT,null=True,blank=True)
    Party = models.ForeignKey(M_Parties, related_name='InvoicesParty', on_delete=models.PROTECT)
    Vehicle = models.ForeignKey(M_Vehicles, related_name='InvoiceVehicle',on_delete=models.PROTECT,null=True,blank=True)
    TCSAmount = models.DecimalField(max_digits=20, decimal_places=2)
    # Hide Flag is temporary 
    Hide = models.BooleanField(default=False)

    class Meta:
        db_table = "T_Invoices"


class TC_InvoiceItems(models.Model):
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
    GST = models.ForeignKey(M_GSTHSNCode, related_name='InvoiceItemGST',null=True,on_delete=models.PROTECT)
    Invoice = models.ForeignKey(T_Invoices, related_name='InvoiceItems', on_delete=models.CASCADE)
    Item = models.ForeignKey(M_Items, on_delete=models.PROTECT)
    LiveBatch=models.ForeignKey(O_LiveBatches, on_delete=models.PROTECT,null=True,blank=True)
    MRP = models.ForeignKey(M_MRPMaster, related_name='InvoiceItemMRP', on_delete=models.PROTECT,null=True,blank=True)
    Unit = models.ForeignKey(MC_ItemUnits, related_name='InvoiceUnitID', on_delete=models.PROTECT)
    QtyInNo = models.DecimalField(max_digits=30, decimal_places=20)
    QtyInKg = models.DecimalField(max_digits=30, decimal_places=20)
    QtyInBox = models.DecimalField(max_digits=30, decimal_places=20)

    class Meta:
        db_table = "TC_InvoiceItems"

class TC_InvoicesReferences(models.Model):
    Invoice = models.ForeignKey(T_Invoices, related_name='InvoicesReferences', on_delete=models.CASCADE)
    Order = models.ForeignKey(T_Orders, related_name='InvoiceOrderReferences', on_delete=models.PROTECT)
    class Meta:
        db_table = "TC_InvoicesReferences"        



class  MC_PartySubParty(models.Model):
    Creditlimit =  models.DecimalField(blank=True, null=True,max_digits=15, decimal_places=2)
    CreatedBy = models.IntegerField(blank=True, null=True)
    CreatedOn = models.DateTimeField(auto_now_add=True)
    UpdatedBy = models.IntegerField(blank=True, null=True)
    UpdatedOn = models.DateTimeField(auto_now=True)
    Party = models.ForeignKey(M_Parties, related_name='MCParty', on_delete=models.PROTECT)
    Route = models.ForeignKey(M_Routes, related_name='MCSubPartyRoute', on_delete=models.PROTECT, blank=True,null=True)
    SubParty = models.ForeignKey(M_Parties, related_name='MCSubParty', on_delete=models.CASCADE)
    Distance = models.DecimalField(blank=True, null=True,max_digits=15, decimal_places=2)
    IsTCSParty = models.BooleanField(default=False)

    class Meta:
        db_table = "MC_PartySubParty"
        
class  MC_PartySubPartyOpeningBalance(models.Model):
    Year = models.CharField(max_length=50,blank=True, null=True)
    OpeningBalanceAmount = models.DecimalField(blank=True, null=True,max_digits=15, decimal_places=3)
    CreatedBy = models.IntegerField(blank=True, null=True)
    CreatedOn = models.DateTimeField(auto_now_add=True)
    UpdatedBy = models.IntegerField(blank=True, null=True)
    UpdatedOn = models.DateTimeField(auto_now=True)
    Party = models.ForeignKey(M_Parties, related_name='MParty', on_delete=models.PROTECT)
    SubParty = models.ForeignKey(M_Parties, related_name='MSubParty', on_delete=models.CASCADE)

    class Meta:
        db_table = "MC_PartySubPartyOpeningBalance"        
                                     

class T_GRNs(models.Model):
    
    GRNDate = models.DateField()
    GRNNumber = models.IntegerField()
    FullGRNNumber = models.CharField(max_length=500)
    InvoiceNumber = models.CharField(max_length=300) # This Invoice Number  - Vendors Invoice Number
    GrandTotal = models.DecimalField(max_digits=20, decimal_places=2)
    CreatedBy = models.IntegerField()
    CreatedOn = models.DateTimeField(auto_now_add=True)
    UpdatedBy = models.IntegerField()
    UpdatedOn = models.DateTimeField(auto_now=True)
    Customer = models.ForeignKey(M_Parties, related_name='GRNCustomer', on_delete=models.PROTECT)
    Party = models.ForeignKey(M_Parties, related_name='GRNParty', on_delete=models.PROTECT)
    Comment = models.CharField(max_length=500 ,null=True,blank=True)
    Reason = models.ForeignKey(M_GeneralMaster, related_name='GRNReason', on_delete=models.PROTECT)

    class Meta:
        db_table = "T_GRNs"

    

class TC_GRNItems(models.Model):
    Quantity = models.DecimalField(max_digits=20, decimal_places=3)
    BaseUnitQuantity = models.DecimalField(max_digits=20, decimal_places=3,validators=[MaxValueValidator(9999999999.999),MinValueValidator(-9999999999.999)])
    MRP = models.ForeignKey(M_MRPMaster, related_name='GRNItemMRP', on_delete=models.PROTECT,null=True,blank=True)
    ReferenceRate = models.DecimalField(max_digits=15, decimal_places=2, null=True)
    Rate = models.DecimalField(max_digits=20, decimal_places=2)
    BasicAmount = models.DecimalField(max_digits=20, decimal_places=2)
    TaxType = models.CharField(max_length=500)
    GSTAmount = models.DecimalField(max_digits=20, decimal_places=2)
    Amount = models.DecimalField(max_digits=20, decimal_places=2)
    DiscountType = models.CharField(max_length=500)
    Discount = models.DecimalField(max_digits=10, decimal_places=2)
    DiscountAmount = models.DecimalField(max_digits=10, decimal_places=2)
    CGST = models.DecimalField(max_digits=10, decimal_places=2)
    SGST = models.DecimalField(max_digits=10, decimal_places=2)
    IGST = models.DecimalField(max_digits=10, decimal_places=2)
    CGSTPercentage = models.DecimalField(max_digits=10, decimal_places=2)
    SGSTPercentage = models.DecimalField(max_digits=10, decimal_places=2)
    IGSTPercentage = models.DecimalField(max_digits=10, decimal_places=2)
    BatchDate = models.DateField(blank=True, null=True)
    BatchCode = models.CharField(max_length=500,blank=True, null=True)
    SystemBatchDate  = models.DateField()
    SystemBatchCode = models.CharField(max_length=500)
    CreatedOn = models.DateTimeField(auto_now_add=True)
    GRN = models.ForeignKey(T_GRNs, related_name='GRNItems', on_delete=models.CASCADE)
    GST = models.ForeignKey(M_GSTHSNCode, related_name='GRNItemGst', on_delete=models.PROTECT,null=True,blank=True)
    Item = models.ForeignKey(M_Items, related_name='GItem', on_delete=models.PROTECT)
    Unit = models.ForeignKey(MC_ItemUnits, related_name='GRNUnitID', on_delete=models.PROTECT)
    MRPValue =  models.DecimalField(max_digits=20, decimal_places=2)
    GSTPercentage = models.DecimalField(max_digits=20, decimal_places=2)
    QtyInNo = models.DecimalField(max_digits=30, decimal_places=20)
    QtyInKg = models.DecimalField(max_digits=30, decimal_places=20)
    QtyInBox = models.DecimalField(max_digits=30, decimal_places=20)
    ActualQuantity=models.DecimalField(max_digits=20, decimal_places=3,null=True,blank=True)

    class Meta:
        db_table = "TC_GRNItems"
             
        
class T_Challan(models.Model):
    ChallanDate = models.DateField()
    ChallanNumber = models.IntegerField()
    FullChallanNumber = models.CharField(max_length=500)
    GrandTotal = models.DecimalField(max_digits=15, decimal_places=2)
    CreatedBy = models.IntegerField()
    CreatedOn = models.DateTimeField(auto_now_add=True)
    UpdatedBy = models.IntegerField()
    UpdatedOn = models.DateTimeField(auto_now=True)
    Customer = models.ForeignKey(M_Parties, related_name='ChallanCustomer', on_delete=models.PROTECT)
    GRN = models.ForeignKey(T_GRNs, on_delete=models.PROTECT,blank=True, null=True)
    Party = models.ForeignKey(M_Parties, related_name='ChallanParty', on_delete=models.PROTECT)

    class Meta:
        db_table = "T_Challan"


class TC_ChallanItems(models.Model):
    Quantity = models.DecimalField(max_digits=15, decimal_places=3,null=True,blank=True)
    BaseUnitQuantity = models.DecimalField(max_digits=15, decimal_places=3)
    Rate = models.DecimalField(max_digits=15, decimal_places=2,null=True,blank=True)
    BasicAmount = models.DecimalField(max_digits=15, decimal_places=2,null=True,blank=True)
    TaxType = models.CharField(max_length=500,null=True,blank=True)
    GSTAmount = models.DecimalField(max_digits=15, decimal_places=2,null=True,blank=True)
    Amount = models.DecimalField(max_digits=15, decimal_places=2,null=True,blank=True)
    DiscountType = models.CharField(max_length=500,blank=True, null=True)
    Discount = models.DecimalField(max_digits=15, decimal_places=2,null=True,blank=True)
    DiscountAmount = models.DecimalField(max_digits=15, decimal_places=2,null=True,blank=True)
    CGST = models.DecimalField(max_digits=15, decimal_places=2,null=True,blank=True)
    SGST = models.DecimalField(max_digits=15, decimal_places=2,null=True,blank=True)
    IGST = models.DecimalField(max_digits=15, decimal_places=2,null=True,blank=True)
    CGSTPercentage = models.DecimalField(max_digits=15, decimal_places=2,null=True,blank=True)
    SGSTPercentage = models.DecimalField(max_digits=15, decimal_places=2,null=True,blank=True)
    IGSTPercentage = models.DecimalField(max_digits=15, decimal_places=2,null=True,blank=True)
    BatchDate = models.DateField(blank=True, null=True)
    BatchCode = models.CharField(max_length=500,null=True,blank=True)
    CreatedOn = models.DateTimeField(auto_now_add=True)
    Challan = models.ForeignKey(T_Challan, related_name='ChallanItems', on_delete=models.CASCADE)
    GST = models.ForeignKey(M_GSTHSNCode, related_name='ChallanItemGST',on_delete=models.PROTECT,null=True,blank=True)
    Item = models.ForeignKey(M_Items, on_delete=models.PROTECT,null=True,blank=True)
    LiveBatch=models.ForeignKey(O_LiveBatches, on_delete=models.PROTECT, blank=True, null=True)
    MRP = models.ForeignKey(M_MRPMaster, related_name='ChallanItemMRP', on_delete=models.PROTECT,null=True,blank=True)
    Unit = models.ForeignKey(MC_ItemUnits, related_name='ChallanUnitID', on_delete=models.PROTECT,null=True,blank=True)

    class Meta:
        db_table = "TC_ChallanItems" 
        
        
class TC_GRNReferences(models.Model):
    ChallanNo = models.CharField(max_length=500 ,null=True)
    Inward = models.BooleanField(default=False)
    Challan = models.ForeignKey(T_Challan, on_delete=models.PROTECT ,null=True)
    GRN = models.ForeignKey(T_GRNs, related_name='GRNReferences', on_delete=models.CASCADE)
    Invoice = models.ForeignKey(T_Invoices, on_delete=models.PROTECT ,null=True)
    Order = models.ForeignKey(T_Orders, related_name='OrderReferences', on_delete=models.PROTECT ,null=True) 

    class Meta:
        db_table = "TC_GRNReferences"              
        
        
class M_BillOfMaterial(models.Model):
    BomDate = models.DateField()
    EstimatedOutputQty = models.DecimalField(max_digits=15, decimal_places=3)
    Comment = models.CharField(max_length=500 ,null=True,blank=True)
    IsActive = models.BooleanField(default=False)
    IsDelete = models.BooleanField(default=False)
    CreatedBy = models.IntegerField()
    CreatedOn = models.DateTimeField(auto_now_add=True)
    ReferenceBom = models.IntegerField(null=True,blank=True)
    IsVDCItem = models.BooleanField(default=False)
    Company = models.ForeignKey(C_Companies, on_delete=models.PROTECT)
    Item = models.ForeignKey(M_Items, on_delete=models.PROTECT) 
    Unit = models.ForeignKey(MC_ItemUnits, related_name='BOMUnitID', on_delete=models.PROTECT)
 
    class Meta:
        db_table = "M_BillOfMaterial"
      
class MC_BillOfMaterialItems(models.Model): 
    Quantity = models.DecimalField(max_digits=15, decimal_places=3)
    BOM = models.ForeignKey(M_BillOfMaterial, related_name='BOMItems', on_delete=models.CASCADE) 
    Item = models.ForeignKey(M_Items, on_delete=models.PROTECT) 
    Unit = models.ForeignKey(MC_ItemUnits, related_name='BOMItemUnitID', on_delete=models.PROTECT)
    
    class Meta:
        db_table = "MC_BillOfMaterialItems"

class T_WorkOrder(models.Model):
    WorkOrderDate = models.DateField()
    WorkOrderNumber = models.IntegerField()
    FullWorkOrderNumber = models.CharField(max_length=500)
    NumberOfLot = models.IntegerField()
    Quantity = models.DecimalField(max_digits=15, decimal_places=3)
    CreatedBy = models.IntegerField()
    CreatedOn = models.DateTimeField(auto_now_add=True)
    UpdatedBy = models.IntegerField()
    UpdatedOn = models.DateTimeField(auto_now=True)
    Bom = models.ForeignKey(M_BillOfMaterial, related_name='BomID', on_delete=models.PROTECT)
    Company = models.ForeignKey(C_Companies, on_delete=models.PROTECT)
    Item = models.ForeignKey(M_Items, on_delete=models.PROTECT)
    Party = models.ForeignKey(M_Parties, on_delete=models.PROTECT)
    Unit = models.ForeignKey(MC_ItemUnits, related_name='WorkOrderUnitID', on_delete=models.PROTECT)

    class Meta:
        db_table = "T_WorkOrder"

class TC_WorkOrderItems(models.Model):
    BomQuantity = models.DecimalField(max_digits=15, decimal_places=3) 
    Quantity = models.DecimalField(max_digits=15, decimal_places=3) 
    Item = models.ForeignKey(M_Items, on_delete=models.PROTECT)
    Unit = models.ForeignKey(MC_ItemUnits, related_name='WorkOrderItemUnitID', on_delete=models.PROTECT)
    WorkOrder = models.ForeignKey(T_WorkOrder, related_name='WorkOrderItems', on_delete=models.CASCADE)
   
    class Meta:
        db_table = "TC_WorkOrderItems"   
                    

class T_MaterialIssue(models.Model):
    MaterialIssueDate = models.DateField()
    MaterialIssueNumber = models.IntegerField()
    FullMaterialIssueNumber = models.CharField(max_length=500)
    NumberOfLot = models.IntegerField()
    LotQuantity = models.DecimalField(max_digits=15, decimal_places=3)
    CreatedBy = models.IntegerField()
    CreatedOn = models.DateTimeField(auto_now_add=True)
    UpdatedBy = models.IntegerField()
    UpdatedOn = models.DateTimeField(auto_now=True)
    Company = models.ForeignKey(C_Companies, on_delete=models.PROTECT)
    Item = models.ForeignKey(M_Items, on_delete=models.PROTECT)
    Party = models.ForeignKey(M_Parties, on_delete=models.PROTECT)
    Unit = models.ForeignKey(MC_ItemUnits, related_name='MaterialIssueUnitID', on_delete=models.PROTECT)

    class Meta:
        db_table = "T_MaterialIssue"

class TC_MaterialIssueItems(models.Model):
    WorkOrderQuantity = models.DecimalField(max_digits=15, decimal_places=3) 
    IssueQuantity = models.DecimalField(max_digits=15, decimal_places=3) 
    BatchDate = models.DateField()
    BatchCode = models.CharField(max_length=500)
    SystemBatchDate = models.DateField()
    SystemBatchCode = models.CharField(max_length=500)
    Item = models.ForeignKey(M_Items, on_delete=models.PROTECT)
    LiveBatchID=models.ForeignKey(O_LiveBatches, on_delete=models.PROTECT)
    MaterialIssue = models.ForeignKey(T_MaterialIssue, related_name='MaterialIssueItems', on_delete=models.CASCADE)
    Unit = models.ForeignKey(MC_ItemUnits, related_name='MaterialIssueItemUnitID', on_delete=models.PROTECT)


    class Meta:
        db_table = "TC_MaterialIssueItems"
        
class TC_MaterialIssueWorkOrders(models.Model):
    Bom = models.ForeignKey(M_BillOfMaterial, related_name='Bom', on_delete=models.PROTECT)
    MaterialIssue = models.ForeignKey(T_MaterialIssue,  on_delete=models.CASCADE)
    WorkOrder = models.ForeignKey(T_WorkOrder, related_name='MaterialIssueWorkOrder', on_delete=models.PROTECT)

    class Meta:
        db_table = "TC_MaterialIssueWorkOrders"   
 
class T_Production(models.Model): 
        ProductionDate = models.DateField()  
        EstimatedQuantity = models.DecimalField(max_digits=15, decimal_places=3)	
        NumberOfLot = models.IntegerField()
        ActualQuantity = models.DecimalField(max_digits=15, decimal_places=3)	
        BatchDate = models.DateField()
        BatchCode = models.CharField(max_length=500)		
        StoreLocation = models.CharField(max_length=500)
        PrintedBatchCode = models.CharField(max_length=500)		
        BestBefore = models.DateField()  
        Remark = models.CharField(max_length=500)	
        CreatedBy = models.IntegerField()
        CreatedOn = models.DateTimeField(auto_now_add=True)
        UpdatedBy = models.IntegerField()
        UpdatedOn = models.DateTimeField(auto_now=True)
        Company = models.ForeignKey(C_Companies,  on_delete=models.PROTECT)		
        Division = models.ForeignKey(M_Parties, on_delete=models.PROTECT)
        Item = models.ForeignKey(M_Items, on_delete=models.PROTECT)
        Unit = models.ForeignKey(MC_ItemUnits, related_name='ProductionUnitID', on_delete=models.PROTECT)

        class Meta:
            db_table = "T_Production"

class TC_ProductionMaterialIssue(models.Model):
        MaterialIssue= models.ForeignKey(T_MaterialIssue, related_name='MaterialIssue', on_delete=models.CASCADE)
        Production= models.ForeignKey(T_Production, related_name='ProductionMaterialIssue', on_delete=models.CASCADE)
    
        class Meta:
            db_table = "TC_ProductionMaterialIssue"
                 
class T_Demands(models.Model):
    DemandDate = models.DateField()
    DemandNo = models.IntegerField()
    FullDemandNumber = models.CharField(max_length=500)
    DemandAmount = models.DecimalField(max_digits=20, decimal_places=2)
    Comment = models.CharField(max_length=500 ,null=True,blank=True)
    CreatedBy = models.IntegerField()
    CreatedOn = models.DateTimeField(auto_now_add=True)
    UpdatedBy = models.IntegerField()
    UpdatedOn = models.DateTimeField(auto_now=True)
    DemandClose = models.PositiveSmallIntegerField(default=0)
    BillingAddress=models.ForeignKey(MC_PartyAddress, related_name='DemandBillingAddress', on_delete=models.PROTECT,null=True,blank=True)
    Customer = models.ForeignKey(M_Parties, related_name='DemandCustomer', on_delete=models.PROTECT)
    Division=models.ForeignKey(M_Parties, related_name='DemandDivision', on_delete=models.PROTECT)
    MaterialIssue=models.ForeignKey(T_MaterialIssue, related_name='DemandMaterialIssue', on_delete=models.PROTECT,null=True,blank=True)
    ShippingAddress=models.ForeignKey(MC_PartyAddress, related_name='DemandShippingAddress', on_delete=models.PROTECT,null=True,blank=True)
    Supplier = models.ForeignKey(M_Parties, related_name='DemandSupplier', on_delete=models.PROTECT)

    class Meta:
        db_table = "T_Demands"        
        
class TC_DemandItems(models.Model):
    Quantity = models.DecimalField(max_digits=15, decimal_places=3)
    Rate = models.DecimalField(max_digits=10, decimal_places=2,null=True,blank=True)
    BaseUnitQuantity = models.DecimalField(max_digits=15, decimal_places=3)
    BasicAmount = models.DecimalField(max_digits=20, decimal_places=2)
    GSTAmount = models.DecimalField(max_digits=10, decimal_places=2)
    Amount = models.DecimalField(max_digits=20, decimal_places=2)
    CGST = models.DecimalField(max_digits=20, decimal_places=2)
    SGST = models.DecimalField(max_digits=20, decimal_places=2)
    IGST = models.DecimalField(max_digits=20, decimal_places=2)
    CGSTPercentage = models.DecimalField(max_digits=20, decimal_places=2)
    SGSTPercentage = models.DecimalField(max_digits=20, decimal_places=2)
    IGSTPercentage = models.DecimalField(max_digits=20, decimal_places=2)
    IsDeleted = models.BooleanField(default=False)
    DeletedOn = models.DateTimeField(auto_now=True)
    Demand = models.ForeignKey(T_Demands, related_name='DemandItem', on_delete=models.CASCADE)
    GST = models.ForeignKey(M_GSTHSNCode, related_name='DemandItemGst', on_delete=models.PROTECT)
    Item = models.ForeignKey(M_Items, related_name='DItem', on_delete=models.PROTECT)
    MRP = models.ForeignKey(M_MRPMaster, related_name='DemandItemMRP', on_delete=models.PROTECT,null=True,blank=True)
    Margin = models.ForeignKey(M_MarginMaster, related_name='DemandItemMargin', on_delete=models.PROTECT,null=True,blank=True)
    Unit = models.ForeignKey(MC_ItemUnits, related_name='DemandUnitID', on_delete=models.PROTECT)
   
    class Meta:
        db_table = "TC_DemandItems"
        

class T_InterbranchChallan(models.Model):
    IBChallanDate = models.DateField()
    IBChallanNumber = models.IntegerField()
    FullIBChallanNumber = models.CharField(max_length=500)
    CustomerGSTTin = models.CharField(max_length=500)
    GrandTotal = models.DecimalField(max_digits=15, decimal_places=2)
    RoundOffAmount = models.DecimalField(max_digits=5, decimal_places=2)
    CreatedBy = models.IntegerField()
    CreatedOn = models.DateTimeField(auto_now_add=True)
    UpdatedBy = models.IntegerField()
    UpdatedOn = models.DateTimeField(auto_now=True)
    Customer = models.ForeignKey(M_Parties, related_name='IBChallanCustomer', on_delete=models.PROTECT)
    Party = models.ForeignKey(M_Parties, related_name='IBChallanParty', on_delete=models.PROTECT)

    class Meta:
        db_table = "T_InterbranchChallan"


class TC_InterbranchChallanItems(models.Model):
    Quantity = models.DecimalField(max_digits=15, decimal_places=3)
    BaseUnitQuantity = models.DecimalField(max_digits=15, decimal_places=3)
    MRP = models.DecimalField(max_digits=15, decimal_places=2,blank=True, null=True)
    Rate = models.DecimalField(max_digits=15, decimal_places=2)
    BasicAmount = models.DecimalField(max_digits=15, decimal_places=2)
    TaxType = models.CharField(max_length=500)
    GSTPercentage = models.DecimalField(max_digits=5, decimal_places=2)
    GSTAmount = models.DecimalField(max_digits=15, decimal_places=2)
    Amount = models.DecimalField(max_digits=15, decimal_places=2)
    DiscountType = models.CharField(max_length=500,blank=True, null=True)
    Discount = models.DecimalField(max_digits=10, decimal_places=2,blank=True, null=True)
    DiscountAmount = models.DecimalField(max_digits=10, decimal_places=2,blank=True, null=True)
    CGST = models.DecimalField(max_digits=5, decimal_places=2)
    SGST = models.DecimalField(max_digits=5, decimal_places=2)
    IGST = models.DecimalField(max_digits=5, decimal_places=2)
    CGSTPercentage = models.DecimalField(max_digits=5, decimal_places=2)
    SGSTPercentage = models.DecimalField(max_digits=5, decimal_places=2)
    IGSTPercentage = models.DecimalField(max_digits=5, decimal_places=2)
    BatchDate = models.DateField(blank=True, null=True)
    BatchCode = models.CharField(max_length=500)
    CreatedOn = models.DateTimeField(auto_now_add=True)
    IBChallan = models.ForeignKey(T_InterbranchChallan, related_name='IBChallanItems', on_delete=models.CASCADE)
    Item = models.ForeignKey(M_Items, on_delete=models.PROTECT)
    LiveBatch=models.ForeignKey(O_LiveBatches,related_name='LiveBatches', on_delete=models.PROTECT)
    Unit = models.ForeignKey(MC_ItemUnits, related_name='InterbranchChallanUnitID', on_delete=models.PROTECT)

    class Meta:
        db_table = "TC_InterbranchChallanItems"

class TC_InterbranchChallanReferences(models.Model):
    Demand = models.ForeignKey(T_Demands, on_delete=models.PROTECT)
    IBChallan = models.ForeignKey(T_InterbranchChallan, on_delete=models.CASCADE)

    class Meta:
        db_table = "TC_InterbranchChallanReferences"         


class T_InterBranchInward(models.Model):
    IBInwardDate = models.DateField()
    IBInwardNumber = models.IntegerField()
    FullIBInwardNumber = models.CharField(max_length=500)
    GrandTotal = models.DecimalField(max_digits=15, decimal_places=2)
    CreatedBy = models.IntegerField()
    CreatedOn = models.DateTimeField(auto_now_add=True)
    UpdatedBy = models.IntegerField()
    UpdatedOn = models.DateTimeField(auto_now=True)
    Customer = models.ForeignKey(M_Parties, related_name='InterBranchCustomer', on_delete=models.PROTECT)
    Supplier = models.ForeignKey(M_Parties, related_name='InterBranchSupplier', on_delete=models.PROTECT)

    class Meta:
        db_table = "T_InterBranchInward"

class TC_InterBranchInwardReferences(models.Model):
    IBChallan = models.ForeignKey(T_InterbranchChallan, on_delete=models.PROTECT ,null=True)
    IBInward = models.ForeignKey(T_InterBranchInward, related_name='InterBranchInwardReferences', on_delete=models.CASCADE)

    class Meta:
        db_table = "TC_InterBranchInwardReferences"    

class TC_InterBranchInwardItems(models.Model):
    Quantity = models.DecimalField(max_digits=15, decimal_places=3)
    BaseUnitQuantity = models.DecimalField(max_digits=15, decimal_places=3)
    MRP = models.DecimalField(max_digits=15, decimal_places=2, null=True)
    ReferenceRate = models.DecimalField(max_digits=15, decimal_places=2, null=True)
    Rate = models.DecimalField(max_digits=15, decimal_places=2)
    BasicAmount = models.DecimalField(max_digits=15, decimal_places=2)
    TaxType = models.CharField(max_length=500)
    GST = models.DecimalField(max_digits=5, decimal_places=2)
    GSTAmount = models.DecimalField(max_digits=15, decimal_places=2)
    Amount = models.DecimalField(max_digits=15, decimal_places=2)
    DiscountType = models.CharField(max_length=500, blank=True, null=True)
    Discount = models.DecimalField(max_digits=15, decimal_places=2,blank=True, null=True)
    DiscountAmount = models.DecimalField(max_digits=15, decimal_places=2,blank=True, null=True)
    CGST = models.DecimalField(max_digits=15, decimal_places=2)
    SGST = models.DecimalField(max_digits=15, decimal_places=2)
    IGST = models.DecimalField(max_digits=15, decimal_places=2)
    CGSTPercentage = models.DecimalField(max_digits=15, decimal_places=2)
    SGSTPercentage = models.DecimalField(max_digits=15, decimal_places=2)
    IGSTPercentage = models.DecimalField(max_digits=15, decimal_places=2)
    BatchDate = models.DateField(blank=True, null=True)
    BatchCode = models.CharField(max_length=500,blank=True, null=True)
    SystemBatchDate  = models.DateField()
    SystemBatchCode = models.CharField(max_length=500)
    CreatedOn = models.DateTimeField(auto_now_add=True)
    IBInward = models.ForeignKey(T_InterBranchInward, related_name='InterBranchInwardItems', on_delete=models.CASCADE)
    Item = models.ForeignKey(M_Items, related_name='IBInwardItem', on_delete=models.PROTECT)
    Unit = models.ForeignKey(MC_ItemUnits, related_name='IBInwardUnitID', on_delete=models.PROTECT)

    class Meta:
        db_table = "TC_InterBranchInwardItems"
                         
         

class T_ProductionReIssue(models.Model):
    Date = models.DateField()
    CreatedBy = models.IntegerField()
    CreatedOn = models.DateTimeField(auto_now_add=True)
    UpdatedBy = models.IntegerField()
    UpdatedOn = models.DateTimeField(auto_now=True) 
    ProductionID = models.ForeignKey(T_Production, related_name='Production', on_delete=models.PROTECT)
    ProductionItem = models.ForeignKey(M_Items, related_name='ProductionItem', on_delete=models.PROTECT)

    class Meta:
        db_table = "T_ProductionReIssue"           

class TC_ProductionReIssueItems(models.Model):
    IssueQuantity = models.DecimalField(max_digits=15, decimal_places=3) 
    BatchDate = models.DateField()
    BatchCode = models.CharField(max_length=500)
    SystemBatchDate = models.DateField()
    SystemBatchCode = models.CharField(max_length=500)
    Item = models.ForeignKey(M_Items, on_delete=models.PROTECT)
    LiveBatchID=models.ForeignKey(O_LiveBatches, on_delete=models.PROTECT)
    ProductionReIssue = models.ForeignKey(T_ProductionReIssue, related_name='ProductionReIssueItems', on_delete=models.CASCADE)
    Unit = models.ForeignKey(MC_ItemUnits, related_name='ProductionReIssueItemUnitID', on_delete=models.PROTECT)

    class Meta:
        db_table = "TC_ProductionReIssueItems"    
        
                
class T_PurchaseReturn(models.Model):
    ReturnDate = models.DateField()
    ReturnNo = models.CharField(max_length=500,blank=True, null=True)
    FullReturnNumber = models.CharField(max_length=500)
    GrandTotal = models.DecimalField(max_digits=20, decimal_places=2)
    RoundOffAmount = models.DecimalField(max_digits=20, decimal_places=2)
    Comment = models.CharField(max_length=500,blank=True, null=True)
    CreatedBy = models.IntegerField()
    CreatedOn = models.DateTimeField(auto_now_add=True)
    UpdatedBy = models.IntegerField()
    UpdatedOn = models.DateTimeField(auto_now=True)
    Customer = models.ForeignKey(M_Parties, related_name='ReturnCustomer', on_delete=models.PROTECT)
    Party = models.ForeignKey(M_Parties, related_name='ReturnParty', on_delete=models.PROTECT)
    ReturnReason = models.ForeignKey(M_GeneralMaster, related_name='ReturnReason', on_delete=models.PROTECT,null=True,blank=True)
    IsApproved=models.BooleanField(default=False)
    Mode = models.IntegerField() # 1- SalesReturn 2-PurchaseReturn 3- Salesconsoldatedpurchasereturn
    
    class Meta:
        db_table = "T_PurchaseReturn"
        

class TC_PurchaseReturnItems(models.Model):
    ItemComment = models.CharField(max_length=500,blank=True, null=True)
    Quantity = models.DecimalField(max_digits=30, decimal_places=3)
    BaseUnitQuantity = models.DecimalField(max_digits=30, decimal_places=3)
    MRPValue =  models.DecimalField(max_digits=20, decimal_places=2)
    Rate = models.DecimalField(max_digits=20, decimal_places=2)
    BasicAmount = models.DecimalField(max_digits=30, decimal_places=2)
    TaxType = models.CharField(max_length=500)
    GSTPercentage = models.DecimalField(max_digits=10, decimal_places=2)
    GSTAmount = models.DecimalField(max_digits=20, decimal_places=2)
    Amount = models.DecimalField(max_digits=30, decimal_places=2)
    CGST = models.DecimalField(max_digits=20, decimal_places=2)
    SGST = models.DecimalField(max_digits=20, decimal_places=2)
    IGST = models.DecimalField(max_digits=20, decimal_places=2)
    CGSTPercentage = models.DecimalField(max_digits=20, decimal_places=2)
    SGSTPercentage = models.DecimalField(max_digits=20, decimal_places=2)
    IGSTPercentage = models.DecimalField(max_digits=20, decimal_places=2)
    BatchDate = models.DateField(blank=True, null=True)
    BatchCode = models.CharField(max_length=500)
    CreatedOn = models.DateTimeField(auto_now_add=True)
    GST = models.ForeignKey(M_GSTHSNCode, related_name='ReturnItemGST',null=True,on_delete=models.PROTECT)
    Item = models.ForeignKey(M_Items, on_delete=models.PROTECT)
    MRP = models.ForeignKey(M_MRPMaster, related_name='ReturnItemMRP', on_delete=models.PROTECT,null=True,blank=True)
    PurchaseReturn = models.ForeignKey(T_PurchaseReturn, related_name='ReturnItems', on_delete=models.CASCADE)
    Unit = models.ForeignKey(MC_ItemUnits, related_name='ReturnUnitID', on_delete=models.PROTECT)
    ItemReason = models.ForeignKey(M_GeneralMaster,related_name= "ItemReason",on_delete=models.PROTECT) 
    Comment = models.CharField(max_length=500,null=True,blank=True)
    ApprovedQuantity= models.DecimalField(max_digits=30, decimal_places=3 ,null=True,blank=True)
    ApprovedBy = models.IntegerField(null=True,blank=True)
    ApprovedOn = models.DateTimeField(auto_now_add=True)
    ApproveComment = models.CharField(max_length=500,null=True,blank=True)
    SubReturn =  models.CharField(max_length=500,null=True,blank=True)
    DiscountType = models.CharField(max_length=500,blank=True, null=True)
    Discount = models.DecimalField(max_digits=20, decimal_places=2,blank=True, null=True)
    DiscountAmount = models.DecimalField(max_digits=20, decimal_places=2,blank=True, null=True)
    BatchID = models.CharField(max_length=500,null=True,blank=True) # O_BatchwiseLiveStock ID
    primarySourceID =models.IntegerField(blank=True, null=True)
    ApprovedByCompany=models.DecimalField(max_digits=20, decimal_places=2,blank=True, null=True)
    FinalApprovalDate=models.DateField(null=True)
    ApprovedRate = models.DecimalField(max_digits=20, decimal_places=2,blank=True, null=True)
    ApprovedBasicAmount = models.DecimalField(max_digits=30, decimal_places=2,blank=True, null=True)
    ApprovedGSTPercentage = models.DecimalField(max_digits=10, decimal_places=2,blank=True, null=True)
    ApprovedGSTAmount = models.DecimalField(max_digits=20, decimal_places=2,blank=True, null=True)
    ApprovedAmount = models.DecimalField(max_digits=30, decimal_places=2,blank=True, null=True)
    ApprovedCGST = models.DecimalField(max_digits=20, decimal_places=2,blank=True, null=True)
    ApprovedSGST = models.DecimalField(max_digits=20, decimal_places=2,blank=True, null=True)
    ApprovedIGST = models.DecimalField(max_digits=20, decimal_places=2,blank=True, null=True)
    ApprovedCGSTPercentage = models.DecimalField(max_digits=20, decimal_places=2,blank=True, null=True)
    ApprovedSGSTPercentage = models.DecimalField(max_digits=20, decimal_places=2,blank=True, null=True)
    ApprovedIGSTPercentage = models.DecimalField(max_digits=20, decimal_places=2,blank=True, null=True)
    ApprovedDiscountAmount = models.DecimalField(max_digits=20, decimal_places=2,blank=True, null=True)

    
    class Meta:
        db_table = "TC_PurchaseReturnItems"
        
class TC_PurchaseReturnItemImages(models.Model):
    Item_pic = models.TextField(null=True,blank=True)
    PurchaseReturnItem = models.ForeignKey(TC_PurchaseReturnItems, related_name='ReturnItemImages', on_delete=models.CASCADE,null=True,blank=True)
    Image = models.ImageField(upload_to="Images\ReturnImages",default="",null=True,blank=True)
    class Meta:
        db_table = "TC_PurchaseReturnItemImages"
        
        
class TC_PurchaseReturnReferences(models.Model):
    PurchaseReturn = models.ForeignKey(T_PurchaseReturn, related_name='Return', on_delete=models.CASCADE)
    SubReturn =  models.ForeignKey(T_PurchaseReturn, related_name='SubReturn', on_delete=models.PROTECT)

    class Meta:
        db_table = "TC_PurchaseReturnReferences"               


class T_LoadingSheet(models.Model):
    Date = models.DateField()
    No = models.CharField(max_length=500)
    InvoiceCount = models.IntegerField()
    TotalAmount = models.DecimalField(max_digits=15, decimal_places=2)
    CreatedBy = models.IntegerField()
    CreatedOn = models.DateTimeField(auto_now_add=True)
    UpdatedBy = models.IntegerField()
    UpdatedOn = models.DateTimeField(auto_now=True)
    Driver = models.ForeignKey(M_Drivers, related_name='LoadingSheetDriver',on_delete=models.PROTECT)
    Party = models.ForeignKey(M_Parties, related_name='LoadingSheetParty', on_delete=models.PROTECT)
    Route =  models.CharField(max_length=500)
    Vehicle = models.ForeignKey(M_Vehicles, related_name='LoadingSheetVehicle',on_delete=models.PROTECT)
   
   
    class Meta:
        db_table = "T_LoadingSheet"
        
class TC_LoadingSheetDetails(models.Model):
    Invoice = models.ForeignKey(T_Invoices, related_name='LoadingSheetInvoice', on_delete=models.PROTECT)
    LoadingSheet = models.ForeignKey(T_LoadingSheet, related_name='LoadingSheetDetails', on_delete=models.CASCADE)
   
    class Meta:
        db_table = "TC_LoadingSheetDetails"

class M_Bank(models.Model):
    Name = models.CharField(max_length=500) 
    CreatedBy = models.IntegerField()
    CreatedOn = models.DateTimeField(auto_now_add=True)
    UpdatedBy = models.IntegerField()
    UpdatedOn = models.DateTimeField(auto_now=True)
    class Meta:
        db_table = "M_Bank"

class MC_PartyBanks(models.Model):
    IFSC = models.CharField(max_length=500,blank=True, null=True)
    BranchName = models.CharField(max_length=500,blank=True, null=True)
    CustomerBank = models.BooleanField(default=False)
    AccountNo = models.CharField(max_length=500,blank=True, null=True)
    IsSelfDepositoryBank = models.BooleanField(default=False)
    IsDefault = models.BooleanField(default=False)
    CreatedBy = models.IntegerField()
    CreatedOn = models.DateTimeField(auto_now_add=True)
    UpdatedBy = models.IntegerField()
    UpdatedOn = models.DateTimeField(auto_now=True)
    Bank = models.ForeignKey(M_Bank, related_name='MCPartyBank', on_delete=models.PROTECT)
    Company = models.ForeignKey(C_Companies, related_name='PartyCompanyBank', on_delete=models.PROTECT)
    Party = models.ForeignKey(M_Parties, related_name='PartyBank', on_delete=models.PROTECT)

    class Meta:
        db_table = "MC_PartyBanks"

                    
class T_Receipts(models.Model):
    ReceiptDate = models.DateField()
    ReceiptNo = models.CharField(max_length=500,blank=True, null=True)
    FullReceiptNumber = models.CharField(max_length=500)
    Description = models.CharField(max_length=500,blank=True, null=True)
    AmountPaid =  models.DecimalField(max_digits=15, decimal_places=3)
    OpeningBalanceAdjusted =  models.DecimalField(max_digits=15, decimal_places=3,blank=True, null=True)
    BalanceAmount =  models.DecimalField(max_digits=15, decimal_places=3,blank=True, null=True)
    ChequeDate = models.CharField(max_length=500,blank=True, null=True)
    DocumentNo =models.CharField(max_length=500,blank=True, null=True)
    CreatedBy = models.IntegerField()
    CreatedOn = models.DateTimeField(auto_now_add=True)
    UpdatedBy = models.IntegerField()
    UpdatedOn = models.DateTimeField(auto_now=True)
    Bank =  models.ForeignKey(M_Bank, related_name='Bank', on_delete=models.PROTECT, blank=True, null=True)
    Customer = models.ForeignKey(M_Parties, related_name='ReceiptCustomer', on_delete=models.PROTECT)
    DepositorBank =  models.ForeignKey(M_Bank, related_name='DepositorBank', on_delete=models.PROTECT, blank=True, null=True)
    Party = models.ForeignKey(M_Parties, related_name='ReceiptParty', on_delete=models.PROTECT)
    ReceiptMode = models.ForeignKey(M_GeneralMaster, related_name='Receiptmode', on_delete=models.PROTECT, blank=True, null=True)
    ReceiptType = models.ForeignKey(M_GeneralMaster, related_name='ReceiptType', on_delete=models.PROTECT, blank=True, null=True)
   
    class Meta:
        db_table = "T_Receipts"
                  
class TC_PaymentReceipt(models.Model):
    Payment = models.ForeignKey(T_Receipts, on_delete=models.PROTECT)
    Receipt = models.ForeignKey(T_Receipts, related_name='PaymentReceipt', on_delete=models.CASCADE,blank=True, null=True)

    class Meta:
        db_table = "TC_PaymentReceipt"        
  
        
class T_CreditDebitNotes(models.Model):
   
    CRDRNoteDate = models.DateField()
    NoteNo = models.IntegerField()
    FullNoteNumber = models.CharField(max_length=500)
    GrandTotal = models.DecimalField(max_digits=20, decimal_places=3, blank=True,null=True)
    RoundOffAmount = models.DecimalField(max_digits=20, decimal_places=3, blank=True,null=True)
    Narration = models.CharField(max_length=500,blank=True, null=True)
    CreatedBy = models.IntegerField()
    CreatedOn = models.DateTimeField(auto_now_add=True)
    UpdatedBy = models.IntegerField()
    UpdatedOn = models.DateTimeField(auto_now=True)
    Customer = models.ForeignKey(M_Parties,related_name='NoteCustomer',on_delete=models.PROTECT)
    NoteReason = models.ForeignKey(M_GeneralMaster,related_name='NoteReason', on_delete=models.PROTECT,blank=True, null=True)
    NoteType = models.ForeignKey(M_GeneralMaster,on_delete=models.PROTECT,blank=True, null=True)
    Party = models.ForeignKey(M_Parties,related_name='NoteParty', on_delete=models.PROTECT)
    PurchaseReturn = models.ForeignKey(T_PurchaseReturn,on_delete=models.PROTECT,blank=True, null=True)
    Receipt = models.ForeignKey(T_Receipts,on_delete=models.PROTECT,blank=True, null=True)
    IsDeleted = models.BooleanField(default=False)
 
    class Meta:
        db_table = "T_CreditDebitNotes"
        
class TC_CreditDebitNoteItems(models.Model):
    
    Quantity = models.DecimalField(max_digits=15, decimal_places=3)
    BaseUnitQuantity = models.DecimalField(max_digits=15, decimal_places=3)
    Rate = models.DecimalField(max_digits=15, decimal_places=2)
    BasicAmount = models.DecimalField(max_digits=15, decimal_places=2)
    TaxType = models.CharField(max_length=500)
    GSTAmount = models.DecimalField(max_digits=15, decimal_places=2)
    Amount = models.DecimalField(max_digits=15, decimal_places=2)
    CGST = models.DecimalField(max_digits=15, decimal_places=2)
    SGST = models.DecimalField(max_digits=15, decimal_places=2)
    IGST = models.DecimalField(max_digits=15, decimal_places=2)
    CGSTPercentage = models.DecimalField(max_digits=15, decimal_places=2)
    SGSTPercentage = models.DecimalField(max_digits=15, decimal_places=2)
    IGSTPercentage = models.DecimalField(max_digits=15, decimal_places=2)
    BatchDate = models.DateField(blank=True, null=True)
    BatchCode = models.CharField(max_length=500)
    CRDRNote = models.ForeignKey(T_CreditDebitNotes,related_name='CRDRNoteItems',on_delete=models.CASCADE,null=True,blank=True)
    GST = models.ForeignKey(M_GSTHSNCode, related_name='CRDRItemGST',null=True,on_delete=models.PROTECT)
    Item = models.ForeignKey(M_Items, on_delete=models.PROTECT)
    MRP = models.ForeignKey(M_MRPMaster, related_name='CRDRMRP', on_delete=models.PROTECT,null=True,blank=True)
    Unit = models.ForeignKey(MC_ItemUnits, related_name='CRDRUnit', on_delete=models.PROTECT)
    GSTPercentage = models.DecimalField(max_digits=20, decimal_places=2,null=True,blank=True)
    MRPValue =  models.DecimalField(max_digits=20, decimal_places=2,null=True,blank=True)
    DiscountType = models.CharField(max_length=500,blank=True, null=True)
    Discount = models.DecimalField(max_digits=20, decimal_places=2,blank=True, null=True)
    DiscountAmount = models.DecimalField(max_digits=20, decimal_places=2,blank=True, null=True)
    QtyInNo = models.DecimalField(max_digits=30, decimal_places=20,null=True,blank=True)
    QtyInKg = models.DecimalField(max_digits=30, decimal_places=20,null=True,blank=True)
    QtyInBox = models.DecimalField(max_digits=30, decimal_places=20,null=True,blank=True)
    ItemComment = models.CharField(max_length=500,null=True,blank=True)

    class Meta:
        db_table = "TC_CreditDebitNoteItems" 

class TC_CreditDebitNoteUploads(models.Model):
    CRDRNote = models.ForeignKey(T_CreditDebitNotes,related_name='CRDRNoteUploads',on_delete=models.CASCADE,null=True,blank=True)
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
        db_table = "TC_CreditDebitNoteUploads"        


class TC_ReceiptInvoices(models.Model):
    GrandTotal =  models.DecimalField(max_digits=15, decimal_places=3,blank=True, null=True)
    PaidAmount =  models.DecimalField(max_digits=15, decimal_places=3,blank=True, null=True)
    AdvanceAmtAdjusted =  models.DecimalField(max_digits=15, decimal_places=3,blank=True, null=True)
    CRDRNote = models.ForeignKey(T_CreditDebitNotes, related_name='CRDRInvoices', on_delete=models.CASCADE,null=True)
    Invoice = models.ForeignKey(T_Invoices, related_name='RInvoice', on_delete=models.PROTECT,blank=True, null=True)
    Receipt = models.ForeignKey(T_Receipts, related_name='ReceiptInvoices', on_delete=models.CASCADE,null=True)

    class Meta:
        db_table = "TC_ReceiptInvoices"

class M_ImportFields(models.Model):
    FieldName = models.CharField(max_length=500)
    IsCompulsory = models.BooleanField(default=False)
    CreatedBy = models.IntegerField()
    CreatedOn = models.DateTimeField(auto_now_add=True)
    UpdatedBy = models.IntegerField()
    UpdatedOn = models.DateTimeField(auto_now=True)
    ControlType = models.ForeignKey(M_ControlTypeMaster, related_name='ImportFieldControlType', on_delete=models.PROTECT)
    FieldValidation = models.ForeignKey(M_FieldValidations, related_name='ImportFieldValidation', on_delete=models.PROTECT)
    ImportExcelType = models.ForeignKey(M_ImportExcelTypes,related_name='ImportFieldExcelType', on_delete=models.PROTECT)
    Company = models.ForeignKey(C_Companies,related_name='ImportFieldCompany', on_delete=models.PROTECT)

    class Meta:
        db_table = "M_ImportFields"
 
        
class MC_PartyImportFields(models.Model):
    Value =models.CharField(max_length=500)
    CreatedBy = models.IntegerField()
    CreatedOn = models.DateTimeField(auto_now_add=True)
    UpdatedBy = models.IntegerField()
    UpdatedOn = models.DateTimeField(auto_now=True)
    Company = models.ForeignKey(C_Companies,related_name='PartyImportFieldCompany', on_delete=models.PROTECT,blank=True, null=True)
    ImportField = models.ForeignKey(M_ImportFields, related_name='ImportFields',on_delete=models.CASCADE)
    Party = models.ForeignKey(M_Parties,related_name='PartyImport', on_delete=models.PROTECT,blank=True, null=True)
   
    class Meta:
        db_table = "MC_PartyImportFields"
                                
class M_PartyCustomerMappingMaster(models.Model):
    MapCustomer = models.CharField(max_length=500)
    CreatedBy = models.IntegerField()
    CreatedOn = models.DateTimeField(auto_now_add=True)
    Customer = models.ForeignKey(M_Parties,related_name='MappingPartiescustomer', on_delete=models.PROTECT)
    Party = models.ForeignKey(M_Parties,related_name='MappingParty', on_delete=models.PROTECT)
  
    class Meta:
        db_table = "M_PartyCustomerMappingMaster"

class M_ItemMappingMaster(models.Model):
    MapItem = models.CharField(max_length=500)
    CreatedBy = models.IntegerField()
    CreatedOn = models.DateTimeField(auto_now_add=True)
    Item = models.ForeignKey(M_Items,related_name='MappingItem', on_delete=models.PROTECT)
    Party = models.ForeignKey(M_Parties,related_name='ItemMappingParty', on_delete=models.PROTECT)

    class Meta:
        db_table = "M_ItemMappingMaster"

class M_UnitMappingMaster(models.Model):
    
    MapUnit = models.CharField(max_length=500)
    CreatedBy = models.IntegerField()
    CreatedOn = models.DateTimeField(auto_now_add=True)
    Party = models.ForeignKey(M_Parties,related_name='UnitMappingParty', on_delete=models.PROTECT)
    Unit = models.ForeignKey(M_Units, related_name='Unit', on_delete=models.PROTECT)
  
    class Meta:
        db_table = "M_UnitMappingMaster"
        
class T_Stock(models.Model):
    StockDate=models.DateField()
    Item= models.ForeignKey(M_Items,related_name='stockItem', on_delete=models.PROTECT)
    BaseUnitQuantity=models.DecimalField(max_digits=20,decimal_places=10)
    Quantity=models.DecimalField(max_digits=20,decimal_places=10)
    Unit = models.ForeignKey(MC_ItemUnits, related_name='StockUnit', on_delete=models.PROTECT)
    MRP = models.ForeignKey(M_MRPMaster, related_name='StockItemMRP', on_delete=models.PROTECT)
    MRPValue =  models.DecimalField(max_digits=20, decimal_places=2)
    Party = models.ForeignKey(M_Parties, related_name='StockParty', on_delete=models.PROTECT)
    CreatedBy = models.IntegerField()
    CreatedOn = models.DateTimeField(auto_now_add=True)
   
    class Meta:
        db_table="T_Stock"        
                
    
            
class O_BatchWiseLiveStock(models.Model):
       
    Quantity = models.DecimalField(max_digits=20, decimal_places=3)
    OriginalBaseUnitQuantity = models.DecimalField(max_digits=20, decimal_places=3)
    BaseUnitQuantity = models.DecimalField(max_digits=20, decimal_places=3)
    IsDamagePieces = models.BooleanField(default=False)
    CreatedBy = models.IntegerField()
    CreatedOn = models.DateTimeField(auto_now_add=True)
    GRN = models.ForeignKey(T_GRNs, related_name='BatchWiseLiveStockGRNID', on_delete=models.CASCADE,null=True)
    InterBranchInward = models.ForeignKey(T_InterBranchInward, related_name='BatchWiseLiveStockInterBranchInwardID', on_delete=models.CASCADE,null=True)
    Item = models.ForeignKey(M_Items, on_delete=models.PROTECT)
    LiveBatche=models.ForeignKey(O_LiveBatches, related_name='LiveBatcheID', on_delete=models.CASCADE)
    Party = models.ForeignKey(M_Parties, related_name='BatchWiseLiveStockParty', on_delete=models.PROTECT)
    Production = models.ForeignKey(T_Production, related_name='BatchWiseLiveStockProductionID', on_delete=models.CASCADE,null=True)
    PurchaseReturn = models.ForeignKey(T_PurchaseReturn, related_name='BatchWiseLiveStockPurchaseReturnID', on_delete=models.CASCADE,null=True)
    Unit = models.ForeignKey(MC_ItemUnits, related_name='BatchWiseLiveStockUnitID', on_delete=models.PROTECT)



    class Meta:
        db_table = "O_BatchWiseLiveStock"    
        
        
class MC_SalesManRoutes(models.Model):
    Route = models.ForeignKey(M_Routes,related_name='SRoute', on_delete=models.PROTECT)
    Salesman = models.ForeignKey(M_Salesman,related_name='SalesmanRoute', on_delete=models.CASCADE) 
 
    class Meta:
        db_table = "MC_SalesManRoutes"             
        
        
class M_Settings(models.Model):
    SystemSetting=models.CharField(max_length=500)
    Description=models.CharField(max_length=500)
    IsActive = models.BooleanField(default=False)
    IsPartyRelatedSetting = models.BooleanField(default=False)
    DefaultValue = models.CharField(max_length=500)
            
    class Meta:
        db_table = "M_Settings"

class MC_SettingsDetails(models.Model):
    Value=models.CharField(max_length=500)
    IsDeleted = models.BooleanField(default=False)
    CreatedBy = models.IntegerField()
    CreatedOn = models.DateTimeField(auto_now_add=True)
    UpdatedBy = models.IntegerField()
    UpdatedOn = models.DateTimeField(auto_now=True)
    Company = models.ForeignKey(C_Companies,related_name='SettingCompany', on_delete=models.PROTECT)
    SettingID=models.ForeignKey(M_Settings,related_name='SettingDetails',on_delete=models.CASCADE)         

    class Meta:
        db_table="MC_SettingsDetails"

class MC_SettingDependency(models.Model):
    DependentSetting=models.ForeignKey(M_Settings,related_name='DependentSettingID',on_delete=models.PROTECT) 
    Setting=models.ForeignKey(M_Settings,related_name='DependentSettingDetails',on_delete=models.CASCADE)  
  
    class Meta:
        db_table="MC_SettingDependency"

class M_TransactionType(models.Model):
    Name = models.CharField(max_length=500) 
    class Meta:
        db_table="M_TransactionType"           
        
 
class Transactionlog(models.Model):
    TranasactionDate =  models.DateField()
    Transactiontime = models.DateTimeField(auto_now_add=True)
    User = models.IntegerField()
    IPaddress = models.CharField(max_length=500)
    PartyID = models.IntegerField()
    TransactionDetails =  models.CharField(max_length=500)
    JsonData = models.TextField(blank = True)
    TransactionType =  models.IntegerField(default=1)
    TransactionID =  models.IntegerField(default=1)
    FromDate = models.DateField(blank=True, null=True)
    ToDate = models.DateField(blank=True, null=True)
    CustomerID = models.IntegerField(default=1)
    
    class Meta:
        db_table="Transactionlog"     
        
class TC_InvoiceUploads(models.Model):
    Invoice = models.ForeignKey(T_Invoices,related_name='InvoiceUploads', on_delete=models.CASCADE) 
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
        db_table="TC_InvoiceUploads"
        
        
class M_PartySettingsDetails(models.Model):
    Value=models.CharField(max_length=500)
    CreatedBy = models.IntegerField()
    CreatedOn = models.DateTimeField(auto_now_add=True)
    Setting=models.ForeignKey(M_Settings,related_name='Settingid',on_delete=models.CASCADE)  
    Company = models.ForeignKey(C_Companies,related_name='SetCompany', on_delete=models.PROTECT)
    Party = models.ForeignKey(M_Parties,related_name='SetParty', on_delete=models.CASCADE)
    
    class Meta:
        db_table="M_PartySettingsDetails"
           
              
class O_DateWiseLiveStock(models.Model):
    
    StockDate=models.DateField()
    Item= models.ForeignKey(M_Items,related_name='DStockItem', on_delete=models.PROTECT)
    OpeningBalance=models.DecimalField(max_digits=20,decimal_places=10)
    GRN = models.DecimalField(max_digits=20,decimal_places=10)
    Sale=models.DecimalField(max_digits=20,decimal_places=10)
    PurchaseReturn = models.DecimalField(max_digits=20,decimal_places=10)
    SalesReturn = models.DecimalField(max_digits=20,decimal_places=10)
    ClosingBalance=models.DecimalField(max_digits=20,decimal_places=10)
    ActualStock = models.DecimalField(max_digits=20,decimal_places=10)
    Unit = models.ForeignKey(MC_ItemUnits, related_name='DStockUnit', on_delete=models.PROTECT) 
    Party = models.ForeignKey(M_Parties, related_name='DStockParty', on_delete=models.PROTECT)
    IsAdjusted = models.BooleanField(default=False)
    CreatedBy = models.IntegerField()
    CreatedOn = models.DateTimeField(auto_now_add=True)
    MRPValue = models.DecimalField(max_digits=20,decimal_places=10)

    class Meta:
        db_table="O_DateWiseLiveStock"      
                
   
class M_DiscountMaster(models.Model):
    
    FromDate=models.DateField()
    ToDate=models.DateField()
    DiscountType = models.IntegerField()
    Discount = models.DecimalField(max_digits=15, decimal_places=2)
    CreatedBy = models.IntegerField()
    CreatedOn = models.DateTimeField(auto_now_add=True)
    UpdatedBy = models.IntegerField()
    UpdatedOn = models.DateTimeField(auto_now_add=True)
    PartyType = models.ForeignKey(M_PartyType, related_name='DiscountPartyType', on_delete=models.PROTECT)
    PriceList =models.ForeignKey(M_PriceList, related_name='DiscountPriceList', on_delete=models.PROTECT)
    Customer =  models.ForeignKey(M_Parties, related_name='DiscountCustomer', on_delete=models.PROTECT,blank=True, null=True)
    Party = models.ForeignKey(M_Parties, related_name='DiscountParty', on_delete=models.PROTECT)
    Item = models.ForeignKey(M_Items,related_name='DiscountItem', on_delete=models.PROTECT)
    IsDeleted = models.BooleanField(default=False)
    

    class Meta:
        db_table="M_DiscountMaster"
        
class M_Claim(models.Model):
    Date=models.DateField()
    FromDate=models.DateField()
    ToDate=models.DateField()
    Customer =  models.ForeignKey(M_Parties, related_name='ClaimCustomer', on_delete=models.PROTECT,blank=True, null=True)
    Party = models.ForeignKey(M_Parties, related_name='ClaimPParty', on_delete=models.PROTECT)
    CreatedBy = models.IntegerField()
    CreatedOn = models.DateTimeField(auto_now_add=True)
    PrimaryAmount = models.DecimalField(max_digits=20, decimal_places=2,blank=True, null=True)
    SecondaryAmount = models.DecimalField(max_digits=20, decimal_places=2,blank=True, null=True)
    ReturnAmount = models.DecimalField(max_digits=20, decimal_places=2,blank=True, null=True)

    class Meta:
        db_table="M_Claim"

class M_MasterClaim(models.Model):
    Claim = models.ForeignKey(M_Claim,related_name='Claim', on_delete=models.CASCADE ) 
    FromDate=models.DateField()
    ToDate=models.DateField()
    PrimaryAmount = models.DecimalField(max_digits=20, decimal_places=2,blank=True, null=True)
    SecondaryAmount = models.DecimalField(max_digits=20, decimal_places=2,blank=True, null=True)
    ReturnAmount = models.DecimalField(max_digits=20, decimal_places=2,blank=True, null=True)
    NetSaleValue = models.DecimalField(max_digits=20, decimal_places=2,blank=True, null=True)
    Budget = models.DecimalField(max_digits=20, decimal_places=2,blank=True, null=True)
    ClaimAmount = models.DecimalField(max_digits=20, decimal_places=2,blank=True, null=True)
    ClaimAgainstNetSale = models.DecimalField(max_digits=20, decimal_places=2,blank=True, null=True)
    Item = models.ForeignKey(M_Items,related_name='ClaimItem', on_delete=models.PROTECT)
    # Customer =  models.ForeignKey(M_Parties, related_name='ClaimCustomer', on_delete=models.PROTECT,blank=True, null=True)
    Party = models.ForeignKey(M_Parties, related_name='ClaimParty', on_delete=models.PROTECT)
    CreatedBy = models.IntegerField()
    CreatedOn = models.DateTimeField(auto_now_add=True)
   
    class Meta:
        db_table="M_MasterClaim"

class MC_ReturnReasonwiseMasterClaim(models.Model):
    Claim = models.ForeignKey(M_Claim,related_name='RClaim', on_delete=models.CASCADE) 
    FromDate=models.DateField()
    ToDate=models.DateField()
    PrimaryAmount = models.DecimalField(max_digits=20, decimal_places=2)
    SecondaryAmount = models.DecimalField(max_digits=20, decimal_places=2)
    ReturnAmount = models.DecimalField(max_digits=20, decimal_places=2)
    NetSaleValue = models.DecimalField(max_digits=20, decimal_places=2)
    Budget = models.DecimalField(max_digits=20, decimal_places=2)
    ClaimAmount = models.DecimalField(max_digits=20, decimal_places=2)
    ClaimAgainstNetSale = models.DecimalField(max_digits=20, decimal_places=2)
    ItemReason = models.ForeignKey(M_GeneralMaster,related_name= "ClaimmItemReason",on_delete=models.PROTECT)
    PartyType = models.IntegerField()
    Party = models.ForeignKey(M_Parties, related_name='ClaimmParty', on_delete=models.PROTECT)
    CreatedBy = models.IntegerField()
    CreatedOn = models.DateTimeField(auto_now_add=True)
   
    class Meta:
        db_table="MC_ReturnReasonwiseMasterClaim"




class ThirdPartyAPITransactionlog(models.Model):
    TranasactionDate =  models.DateField()
    Transactiontime = models.DateTimeField(auto_now_add=True)
    User = models.IntegerField()
    IPaddress = models.CharField(max_length=500)
    PartyID = models.IntegerField()
    TransactionDetails =  models.CharField(max_length=500)
    JsonData = models.TextField(blank = True)
    ThirdParytSource =  models.CharField(max_length=500)
    
    class Meta:
        db_table="ThirdPartyAPITransactionlog"
        
class T_DeletedInvoices(models.Model):
    Invoice = models.IntegerField(null=True)
    InvoiceDate = models.DateField()
    InvoiceNumber = models.IntegerField(null=True)
    FullInvoiceNumber = models.CharField(max_length=500)
    GrandTotal = models.DecimalField(max_digits=20, decimal_places=2)
    RoundOffAmount = models.DecimalField(max_digits=15, decimal_places=2)
    CreatedBy = models.IntegerField(null=True)
    CreatedOn = models.DateTimeField(auto_now_add=True)
    UpdatedBy = models.IntegerField(null=True)
    UpdatedOn = models.DateTimeField()
    Customer = models.IntegerField(null=True)
    Driver = models.IntegerField(null=True)
    Party = models.IntegerField(null=True)
    Vehicle = models.IntegerField(null=True)
    TCSAmount = models.DecimalField(max_digits=20, decimal_places=2)

    Hide = models.BooleanField()
    DeletedOn = models.DateTimeField(auto_now_add=True) 

    class Meta:
        db_table = "T_DeletedInvoices"        
        

class TC_DeletedInvoiceItems(models.Model):
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
    GST = models.IntegerField(null=True)
    Invoice = models.IntegerField(null=True)
    Item = models.IntegerField(null=True)
    LiveBatch= models.IntegerField(null=True)
    MRP = models.IntegerField(null=True)
    Unit = models.IntegerField(null=True)
    QtyInNo = models.DecimalField(max_digits=30, decimal_places=20)
    QtyInKg = models.DecimalField(max_digits=30, decimal_places=20)
    QtyInBox = models.DecimalField(max_digits=30, decimal_places=20)

    class Meta:
        db_table = "TC_DeletedInvoiceItems"
        
        
class TC_DeletedInvoiceUploads(models.Model):
    Invoice = models.IntegerField(null=True)
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
        db_table="TC_DeletedInvoiceUploads"  
        
         
class TC_DeletedInvoicesReferences(models.Model):
    Invoice =models.IntegerField(null=True)
    Order = models.IntegerField(null=True)
    class Meta:
        db_table = "TC_DeletedInvoicesReferences"
        
        
        
class M_ChannelWiseItems(models.Model):
    Item = models.ForeignKey(M_Items,related_name='ChannelItem', on_delete=models.PROTECT)
    PartyType =models.ForeignKey(M_PartyType, related_name='ChannelPartyType', on_delete=models.PROTECT) 


    class Meta:
        db_table = "M_ChannelWiseItems"        
        
        
                                      
   
                        
         
   
       

        
        
       


       