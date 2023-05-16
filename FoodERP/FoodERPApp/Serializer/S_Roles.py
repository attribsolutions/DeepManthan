from ..models import *
from rest_framework import serializers

class RoleEmployeeTypesSerializer(serializers.ModelSerializer):
    class Meta:
        model =  MC_RolesEmployeeTypes
        fields = ['EmployeeType']

class C_CompanySerializer1(serializers.ModelSerializer):
    class Meta:
        model = C_Companies
        fields = ['id','Name']

class M_RolesSerializerforFilter(serializers.ModelSerializer):
    RoleEmployeeTypes= RoleEmployeeTypesSerializer(many=True)
    Company=C_CompanySerializer1(read_only=True)
    class Meta:
        model =  M_Roles 
        fields = ['id','Name','Description','isActive','isSCMRole','IsPartyConnection','Dashboard','CreatedBy','UpdatedBy','RoleEmployeeTypes','Company']
        
class M_RolesSerializer(serializers.ModelSerializer):
    RoleEmployeeTypes= RoleEmployeeTypesSerializer(many=True)
    # Company=C_CompanySerializer1(read_only=True)
    class Meta:
        model =  M_Roles 
        fields = ['id','Name','Description','isActive','isSCMRole','IsPartyConnection','Dashboard','CreatedBy','UpdatedBy','RoleEmployeeTypes','Company']
        
    def create(self, validated_data):
        RoleEmployeeTypes_data = validated_data.pop('RoleEmployeeTypes')
        RoleID = M_Roles.objects.create(**validated_data)
        for RoleEmployeeType_data in RoleEmployeeTypes_data:
            RoleEmployeeType =MC_RolesEmployeeTypes.objects.create(Role=RoleID, **RoleEmployeeType_data) 
        return RoleID           

    def update(self, instance, validated_data):
        
        
        instance.Name = validated_data.get(
            'Name', instance.Name)
        instance.Description = validated_data.get(
            'Description', instance.Description)    
        instance.isActive = validated_data.get(
            'isActive', instance.isActive)
        instance.isSCMRole = validated_data.get(
            'isSCMRole', instance.isSCMRole)
        instance.IsPartyConnection = validated_data.get(
            'IsPartyConnection', instance.IsPartyConnection)
        instance.Dashboard = validated_data.get(
            'Dashboard', instance.Dashboard)
        instance.UpdatedBy = validated_data.get(
            'UpdatedBy', instance.UpdatedBy) 
        instance.UpdatedOn = validated_data.get(
            'UpdatedOn', instance.UpdatedOn)           
        
        instance.save()

        for items in instance.RoleEmployeeTypes.all():
          items.delete()

        

        for OrderItem_data in validated_data['RoleEmployeeTypes']:
            Items = MC_RolesEmployeeTypes.objects.create(Role=instance, **OrderItem_data)
        instance.RoleEmployeeTypes.add(Items)

        return instance
    

class EmployeeTypesSerializerSecond(serializers.ModelSerializer):
    class Meta:
        model =  M_EmployeeTypes
        fields = ['id','Name']
        
class RoleEmployeeTypesSerializerSecond(serializers.ModelSerializer):
    EmployeeType = EmployeeTypesSerializerSecond()
    class Meta:
        model =  MC_RolesEmployeeTypes
        fields = ['EmployeeType']
        
class M_RolesSerializerSecond(serializers.ModelSerializer):
    RoleEmployeeTypes= RoleEmployeeTypesSerializerSecond(many=True,read_only=True)
    class Meta:
        model =  M_Roles 
        fields = ['id','Name','Description','isActive','isSCMRole','IsPartyConnection','Dashboard','CreatedBy','UpdatedBy','RoleEmployeeTypes']          