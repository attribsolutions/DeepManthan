from xml.etree.ElementInclude import include
from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework_jwt.settings import api_settings
from django.contrib.auth.models import update_last_login

from  ..models import M_Users, MC_UserRoles

from rest_framework import serializers

from ..models import M_Users

JWT_PAYLOAD_HANDLER = api_settings.JWT_PAYLOAD_HANDLER
JWT_ENCODE_HANDLER = api_settings.JWT_ENCODE_HANDLER

class UserRolesSerializer(serializers.ModelSerializer):
    class Meta:
        model = MC_UserRoles
        fields = '__all__'

class UserRegistrationSerializer(serializers.ModelSerializer):
    RoleID=UserRolesSerializer(many=True)
    class Meta:
        model = M_Users
        fields = '__all__'
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        Roles_data = validated_data.pop('RoleID')
       
        user = M_Users.objects.create_user(**validated_data)
        for Role_data in Roles_data:
            MC_UserRoles.objects.create(
                UserID=user, 
                RoleID=Role_data['RoleID'])
        return user

class UserRegistrationSerializer1(serializers.ModelSerializer):
    class Meta:
        model = M_Users
        fields = '__all__'
        fields = ['LoginName','AdminPassword','isActive','EmployeeID']
        
        extra_kwargs = {'password': {'write_only': True}}
    
    def update(self, instance, validated_data):
        
        # * Order Info
        instance.LoginName = validated_data.get(
            'LoginName', instance.LoginName)
        instance.AdminPassword = validated_data.get(
            'AdminPassword', instance.AdminPassword)
        instance.isActive = validated_data.get(
            'isActive', instance.isActive)
        instance.EmployeeID = validated_data.get(
            'EmployeeID', instance.EmployeeID)    
        instance.save()

        for items in instance.RoleID.all():
          items.delete()

        

        for RoleID_data in validated_data['RoleID']:
            Items = MC_UserRoles.objects.create(UserID=instance, **RoleID_data)
        instance.RoleID.add(Items)
 
     

        return instance  


    

class UserListSerializer(serializers.ModelSerializer):
    RoleID = UserRolesSerializer(many=True, read_only=True)
    class Meta:
        model = M_Users
        fields = '__all__'
        
        
        
 
class UserLoginSerializer(serializers.Serializer):
    
    LoginName = serializers.CharField(max_length=255)
    password = serializers.CharField(max_length=128, write_only=True)
    token = serializers.CharField(max_length=255, read_only=True)

    def validate(self, data):
        LoginName = data.get("LoginName", None)
        password = data.get("password", None)
        user = authenticate(LoginName=LoginName, password=password)

        if user is None:
            raise serializers.ValidationError(
                'A user with this email and password is not found.'
            )
        try:
            payload = JWT_PAYLOAD_HANDLER(user)
            jwt_token = JWT_ENCODE_HANDLER(payload)

            update_last_login(None, user)
        except M_Users.DoesNotExist:
            raise serializers.ValidationError(
                'User with given email and password does not exists'
            )
        return {
            'LoginName': user.LoginName,
            'token': jwt_token
        }