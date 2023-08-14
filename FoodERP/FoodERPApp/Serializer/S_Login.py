from rest_framework import serializers
from django.contrib.auth import authenticate
# from rest_framework_jwt.settings import api_settings
from django.contrib.auth.models import update_last_login
from  ..models import C_CompanyGroups, M_Employees, M_Parties, M_Roles, M_Users, MC_UserRoles,C_Companies
from rest_framework import serializers
from ..models import M_Users
from rest_framework_simplejwt.tokens import RefreshToken
from django.http import JsonResponse

# JWT_PAYLOAD_HANDLER = api_settings.JWT_PAYLOAD_HANDLER
# JWT_ENCODE_HANDLER = api_settings.JWT_ENCODE_HANDLER

class MC_UserRolesSerializer(serializers.ModelSerializer):
    class Meta:
        model = MC_UserRoles
        fields =  ['Role','Party']
        

class UserRegistrationSerializer(serializers.ModelSerializer):
    UserRole=MC_UserRolesSerializer(many=True)
    class Meta:
        model = M_Users
        fields = '__all__'
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        Roles_data = validated_data.pop('UserRole')
        user = M_Users.objects.create_user(**validated_data)
        for Role_data in Roles_data:
            MC_UserRoles.objects.create(User=user, **Role_data)
        return user
    
    def update(self, instance, validated_data):
        
        # for (key, value) in validated_data.items():
        #     setattr(instance, key, value)

        instance.isActive = validated_data.get(
            'isActive', instance.isActive)  
        instance.isSendOTP = validated_data.get(
            'isSendOTP', instance.isSendOTP)  
        instance.isLoginUsingMobile = validated_data.get(
            'isLoginUsingMobile', instance.isLoginUsingMobile)
        instance.isLoginUsingEmail = validated_data.get(
            'isLoginUsingEmail', instance.isLoginUsingEmail)
        # instance.AdminPassword = validated_data.get(
        #     'password', instance.password)   
        instance.UpdatedBy = validated_data.get(
            'UpdatedBy', instance.UpdatedBy)
        instance.Employee_id = validated_data.get(
            'Employee_id', instance.Employee_id)                       
        
        # password = validated_data.pop('password', None)
        # if password is not None:
        #     instance.set_password(password)           
        # instance.save()

        for items in instance.UserRole.all():
            items.delete()

        for RoleID_data in validated_data['UserRole']:
            Items = MC_UserRoles.objects.create(User=instance, **RoleID_data)
        instance.UserRole.add(Items)
        return instance  

       



class UserRegistrationSerializer1(serializers.ModelSerializer):
    class Meta:
        model = M_Users
        fields = '__all__'
        # fields = ['LoginName','AdminPassword','isActive','Employee']
        
        # extra_kwargs = {'password': {'write_only': True}}
    
    

class FindUserSerializer(serializers.Serializer):
    id=serializers.IntegerField()
    EmployeeName=serializers.CharField(max_length=128) 
    UserID=serializers.IntegerField()
    LoginName=serializers.CharField(max_length=128)

class UserLoginSerializer(serializers.Serializer):
    
    LoginName = serializers.CharField(max_length=255)
    password = serializers.CharField(max_length=128, write_only=True)
    token = serializers.CharField(max_length=255, read_only=True)
    refreshtoken = serializers.CharField(max_length=255, read_only=True)
    EmployeeID = serializers.CharField(max_length=255, read_only=True)
    UserID= serializers.CharField(max_length=255, read_only=True)

    
    def validate(self, data):
        LoginName = data.get("LoginName", None)
        password = data.get("password", None)
        user = authenticate(LoginName=LoginName, password=password)
      
        if user is None:
            
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'A user with this LoginName and password is not found', 'Data':[]})
        try:
            
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)
            

            

            update_last_login(None, user)
        except M_Users.DoesNotExist:
            
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'User with given LoginName and password does not exists', 'Data':[]})
        return {
            'LoginName': user.LoginName,
            'EmployeeID':user.Employee_id,
            'token': access_token,
            'UserID' : user.id,
            'refreshtoken': refresh_token
        }


class RolesSerializer(serializers.ModelSerializer):
    class Meta:
        model = M_Roles
        fields= ['id','Name']

class PartySerializer(serializers.ModelSerializer):
    class Meta:
        model = M_Parties
        fields= ['id','Name']        

class UserRolesSerializer(serializers.ModelSerializer):
    Role=RolesSerializer()
    Party=PartySerializer()
   
    class Meta:
        model = MC_UserRoles
        fields= ['Role','Party']
        
    def to_representation(self, instance):
        # get representation from ModelSerializer
        ret = super(UserRolesSerializer, self).to_representation(instance)
        # if parent is None, overwrite
        if not ret.get("Role", None):
            ret["Role"] = {"id": None, "Name": None}
            
        if not ret.get("Party", None):
            ret["Party"] = {"id": None, "Name": None}    
        return ret     
        
class C_CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = C_Companies
        fields = '__all__'
        
class M_employeesSerializer(serializers.ModelSerializer): 
    Company = C_CompanySerializer(read_only=True)
    class Meta:
        model = M_Employees
        fields = '__all__' 
        
class UserListSerializer(serializers.ModelSerializer):
    UserRole = UserRolesSerializer(many=True, read_only=True)
    Employee = M_employeesSerializer(read_only=True)
    class Meta:
        model = M_Users
        fields = '__all__'
        # fields = ['ID','password','LoginName','last_login','email','AdminPassword','isActive','isSendOTP','EmployeeID','CreatedBy','RoleID']
        
        

class C_CompanyGroupSerializer(serializers.ModelSerializer):
     class Meta:
        model = C_CompanyGroups
        fields = '__all__'

class M_UserPartiesSerializer1(serializers.Serializer):
      
    id = serializers.IntegerField()
    Role = serializers.IntegerField()
    RoleName=serializers.CharField(max_length=500)
    Party_id=serializers.IntegerField()
    PartyName=serializers.CharField(max_length=500)
    Employee_id=serializers.IntegerField()
    SAPPartyCode=serializers.CharField(max_length=500)
    IsSCMPartyType=serializers.IntegerField()
    GSTIN=serializers.CharField(max_length=500) 

class M_UserPartiesSerializer(serializers.Serializer):
  
    id = serializers.IntegerField()
    Role = serializers.IntegerField()
    RoleName=serializers.CharField(max_length=500)
    Party_id=serializers.IntegerField()
    PartyName=serializers.CharField(max_length=500)
    Employee_id=serializers.IntegerField()
    SAPPartyCode=serializers.CharField(max_length=500)
    IsSCMPartyType=serializers.IntegerField()
    GSTIN=serializers.CharField(max_length=500)
    FSSAINo=serializers.CharField(max_length=500)
    FSSAIExipry=serializers.DateField()
    PartyTypeID=serializers.IntegerField()
    PartyType=serializers.CharField(max_length=500)
    
class EmployeeSerializerForUserCreation(serializers.Serializer): 
    
    id = serializers.IntegerField()
    Name=serializers.CharField(max_length=500)  

class UserListSerializerforgetdata(serializers.ModelSerializer):
    class Meta:
        model = M_Users
        fields = ['Employee','LoginName']

class UserListSerializergetdata(serializers.Serializer):
    id = serializers.IntegerField()
    
class SingleGetUserListUserPartiesSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    Party_id = serializers.IntegerField()
    PartyName=serializers.CharField(max_length=500)
 
class SingleGetUserListUserPartyRoleSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    Role_id = serializers.IntegerField()
    RoleName=serializers.CharField(max_length=500)    
    

    
    