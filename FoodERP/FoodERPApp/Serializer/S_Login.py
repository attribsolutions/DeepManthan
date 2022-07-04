from dataclasses import field
from pyexpat import model
from xml.etree.ElementInclude import include
from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework_jwt.settings import api_settings
from django.contrib.auth.models import update_last_login

from  ..models import M_Roles, M_Users, MC_UserRoles

from rest_framework import serializers

from ..models import M_Users

JWT_PAYLOAD_HANDLER = api_settings.JWT_PAYLOAD_HANDLER
JWT_ENCODE_HANDLER = api_settings.JWT_ENCODE_HANDLER

class MC_UserRolesSerializer(serializers.ModelSerializer):
    class Meta:
        model = MC_UserRoles
        fields =  ['Role']
        

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



class UserRegistrationSerializer1(serializers.ModelSerializer):
    class Meta:
        model = M_Users
        fields = '__all__'
        fields = ['LoginName','AdminPassword','isActive','Employee']
        
        extra_kwargs = {'password': {'write_only': True}}
    
    def update(self, instance, validated_data):
        
        # * Order Info
        instance.LoginName = validated_data.get(
            'LoginName', instance.LoginName)
        instance.AdminPassword = validated_data.get(
            'AdminPassword', instance.AdminPassword)
        instance.isActive = validated_data.get(
            'isActive', instance.isActive)
        instance.Employee = validated_data.get(
            'Employee', instance.Employee)    
        instance.save()

        for items in instance.UserRole.all():
          items.delete()

        

        for RoleID_data in validated_data['UserRole']:
            Items = MC_UserRoles.objects.create(UserID=instance, **RoleID_data)
        instance.RoleID.add(Items)
 
     

        return instance  


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


class RolesSerializer(serializers.ModelSerializer):
    class Meta:
        model = M_Roles
        fields= ['id','Name']

class UserRolesSerializer(serializers.ModelSerializer):
    Role=RolesSerializer();
    # Role= serializers.SlugRelatedField(read_only=True, slug_field='Name' )
    
    class Meta:
        model = MC_UserRoles
        fields= ['Role']
        


class UserListSerializer(serializers.ModelSerializer):
    UserRole = UserRolesSerializer(many=True, read_only=True)
    class Meta:
        model = M_Users
        fields = '__all__'
        # fields = ['ID','password','LoginName','last_login','email','AdminPassword','isActive','isSendOTP','EmployeeID','CreatedBy','RoleID']
        
        
        
        
 
