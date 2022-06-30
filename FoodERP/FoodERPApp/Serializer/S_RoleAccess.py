from dataclasses import fields
from rest_framework import serializers
from ..Serializer.S_Modules import *

from ..Serializer.S_Roles import M_RolesSerializer
from ..models import *




class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    """
    A ModelSerializer that takes an additional `fields` argument that
    controls which fields should be displayed.
    """

    def __init__(self, *args, **kwargs):
        # Don't pass the 'fields' arg up to the superclass
        fields = kwargs.pop('fields', None)

        # Instantiate the superclass normally
        super(DynamicFieldsModelSerializer, self).__init__(*args, **kwargs)

        if fields is not None:
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields)
            existing = set(self.fields.keys())
            for field_name in existing - allowed:
                self.fields.pop(field_name) 

class M_RoleAccessSerializer1(DynamicFieldsModelSerializer):
    
    class Meta:
        model = M_RoleAccess
        fields = '__all__'
        

class M_RoleAccessSerializerfordistinctModule(serializers.Serializer):
    ID = serializers.IntegerField(read_only=True)
    Name = serializers.CharField(required=False, allow_blank=True, max_length=100) 

class M_PagesSerializerforRoleAccess(DynamicFieldsModelSerializer):
    
    class Meta:
        model = M_Pages
        fields ="__all__" 

class MC_RolePageAccessSerilaizer(serializers.ModelSerializer):

    class Meta:
        model = MC_RolePageAccess
        fields = ['RoleAccess','PageAccess']

class M_RoleAccessSerializer(serializers.ModelSerializer):
    RolePageAccess=MC_RolePageAccessSerilaizer(many=True)
    class Meta:
        model = M_RoleAccess
        fields = ['Role','Company','Division','Modules','Pages','RolePageAccess']
           
    def create(self, validated_data):
        RolePageAccess_datas = validated_data.pop('RolePageAccess')
        RoleAccessID = M_RoleAccess.objects.create(**validated_data)
        for RolePageAccess_data in RolePageAccess_datas:
           TC_OrderItems.objects.create(RoleAccess=RoleAccessID, **RolePageAccess_data)
            
        return RoleAccessID    


   