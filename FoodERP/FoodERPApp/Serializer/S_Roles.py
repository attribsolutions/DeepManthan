from dataclasses import fields
from ..models import *
from rest_framework import serializers



class RoleEmployeeTypesSerializer(serializers.ModelSerializer):
    class Meta:
        model =  MC_RolesEmployeeTypes
        fields = ['EmployeeType']
    

class M_RolesSerializer(serializers.ModelSerializer):
    
    RoleEmployeeTypes= RoleEmployeeTypesSerializer(many=True)
    class Meta:
        model =  M_Roles 
        fields = ['id','Name','Description','isActive','isSCMRole','Dashboard','CreatedBy','UpdatedBy','RoleEmployeeTypes']
        
    def create(self, validated_data):
        RoleEmployeeTypes_data = validated_data.pop('RoleEmployeeTypes')
        RoleID = M_Roles.objects.create(**validated_data)
        for RoleEmployeeType_data in RoleEmployeeTypes_data:
            RoleEmployeeType =MC_RolesEmployeeTypes.objects.create(Role=RoleID, **RoleEmployeeType_data) 
        return RoleID           