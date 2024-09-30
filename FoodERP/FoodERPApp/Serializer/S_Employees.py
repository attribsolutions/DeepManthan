from ..models import *
from rest_framework import serializers


class M_EmployeesSerializer02(serializers.Serializer):
    id = serializers.IntegerField()
    Name = serializers.CharField(max_length=100)
    Address = serializers.CharField(max_length=500)
    Mobile = serializers.CharField(max_length=100)
    email = serializers.EmailField(max_length=255) 
    DOB = serializers.CharField(max_length=100)
    PAN = serializers.CharField(max_length=100)
    AadharNo = serializers.CharField(max_length=100)
    CreatedBy = serializers.IntegerField(default=False)
    CreatedOn = serializers.DateTimeField()
    UpdatedBy = serializers.IntegerField(default=False)
    UpdatedOn = serializers.DateTimeField()
    CompanyName = serializers.CharField(max_length=100)
    EmployeeTypeName = serializers.CharField(max_length=100)
    StateName = serializers.CharField(max_length=100)
    DistrictName = serializers.CharField(max_length=100)
    CityName = serializers.CharField(max_length=100)
    Company_id = serializers.IntegerField()
    EmployeeType_id = serializers.IntegerField()
    State_id = serializers.IntegerField()
    District_id =serializers.IntegerField()
    City_id =serializers.IntegerField()
    PIN = serializers.CharField(max_length=100)
    DesignationID = serializers.CharField(max_length=50)
    Designation = serializers.CharField(max_length=50)
    

class MC_EmployeePartiesSerializer(serializers.ModelSerializer):
    class Meta:
        model =  MC_EmployeeParties
        fields = ['Party']

class M_EmployeesSerializer(serializers.ModelSerializer):
    EmployeeParties=MC_EmployeePartiesSerializer(many=True)
    class Meta:
        model =  M_Employees
        fields = '__all__'   

    def create(self, validated_data):
        EmployeePartys_data = validated_data.pop('EmployeeParties')
        Employees = M_Employees.objects.create(**validated_data)
        for EmployeeParty_data in EmployeePartys_data:
            MC_EmployeeParties.objects.create(Employee=Employees, **EmployeeParty_data)
        return Employees         

    def update(self, instance, validated_data):
        
        instance.Name = validated_data.get(
            'Name', instance.Name)
        instance.Address = validated_data.get(
            'Address', instance.Address)    
        instance.Mobile = validated_data.get(
            'Mobile', instance.Mobile)
        instance.email = validated_data.get(
            'email', instance.email)
        instance.DOB = validated_data.get(
            'DOB', instance.DOB)
        instance.PAN = validated_data.get(
            'PAN', instance.PAN)
        instance.AadharNo = validated_data.get(
            'AadharNo', instance.AadharNo)
        # instance.Company = validated_data.get(
        #     'Company', instance.Company)
        instance.EmployeeType = validated_data.get(
            'EmployeeType', instance.EmployeeType)
        instance.State = validated_data.get(
            'State', instance.State)
        instance.District = validated_data.get(
            'District', instance.District) 
        instance.PIN = validated_data.get(
            'PIN', instance.PIN)
        instance.Designation = validated_data.get(
            'Designation', instance.Designation)
        instance.City = validated_data.get(
            'City', instance.City)                          
        instance.UpdatedBy = validated_data.get(
            'UpdatedBy', instance.UpdatedBy) 
        instance.UpdatedBy = validated_data.get(
            'UpdatedBy', instance.UpdatedBy)           
        
        instance.save()

        for items in instance.EmployeeParties.all():
            items.delete()

        for OrderItem_data in validated_data['EmployeeParties']:
            Items = MC_EmployeeParties.objects.create(Employee=instance, **OrderItem_data)
            instance.EmployeeParties.add(Items)
 
        return instance      

class EmployeepartiesDataSerializer(serializers.Serializer):
    id= serializers.IntegerField()
    Name = serializers.CharField(max_length=100)


class EmployeepartiesDataSerializer03(serializers.Serializer):
    # id= serializers.IntegerField()
    # Role_id= serializers.IntegerField()
    # Name = serializers.CharField(max_length=100)
    # RoleName= serializers.CharField(max_length=100)
    id = serializers.IntegerField()
    Party_id = serializers.IntegerField()
    Name=serializers.CharField(max_length=500)
    Role= serializers.IntegerField()
    RoleName=serializers.CharField(max_length=500)  

class M_EmployeesSerializerforgetdata(serializers.ModelSerializer):
    # Company_id =  serializers.IntegerField()
    class Meta:
        model =  M_Employees
        fields = ['Company']

class ManagementEmployeeParties(serializers.ModelSerializer):
    
    class Meta:
        model =  MC_ManagementParties
        fields = '__all__'
   


class PartyEmpDetailsSerializer(serializers.Serializer):
    EmpName = serializers.CharField(max_length=500)
    EmpAddress = serializers.CharField(max_length=500)
    EmpMobile = serializers.CharField(max_length=20) 
    EmpEmail = serializers.EmailField()
    DOB = serializers.DateField()
    EmpPAN = serializers.CharField(max_length=50) 
    AadharNo = serializers.CharField(max_length=20) 
    EmpPIN = serializers.CharField(max_length=10)  
    EmpDistrict = serializers.CharField(max_length=100)
    EmpState = serializers.CharField(max_length=100)
    EmpType = serializers.CharField(max_length=20)
    PartyID = serializers.IntegerField()
    PartyName = serializers.CharField(max_length=500)
    PartyType = serializers.CharField(max_length=500)
    PartyAddress = serializers.CharField(max_length=500)
    FSSAINo = serializers.CharField(max_length=200)
    FSSAIExipry =serializers.CharField(max_length=200)
    PartyPIN = serializers.IntegerField()
    PartyEmail = serializers.EmailField()
    MobileNo = serializers.CharField(max_length=20)  
    AlternateContactNo = serializers.CharField(max_length=20)  
    SAPPartyCode = serializers.CharField(max_length=20)  
    GSTIN = serializers.CharField(max_length=20)  
    PartyPAN = serializers.CharField(max_length=20) 
    PartyCity = serializers.CharField(max_length=100)
    PartyDistrict = serializers.CharField(max_length=50) 
    PartyState = serializers.CharField(max_length=100)
    IsDivision = serializers.BooleanField()
    MkUpMkDn = serializers.BooleanField()
    IsPartyActive = serializers.BooleanField()
    Latitude = serializers.CharField(max_length=100) 
    Longitude = serializers.CharField(max_length=100)
    LoginName = serializers.CharField(max_length=500)

        
                      