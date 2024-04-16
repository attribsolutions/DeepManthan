from ..models import *
from rest_framework import serializers

class RolesSerializer(serializers.ModelSerializer):
    class Meta:
        model = M_SweetPOSRoles
        fields ="__all__"

class UsersSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    CompanyID = serializers.IntegerField()
    DivisionID = serializers.IntegerField()
    LoginName = serializers.CharField(max_length=500)
    Password = serializers.CharField(max_length=500)
    RoleID = serializers.IntegerField()
    IsActive =  serializers.IntegerField()
    CreatedBy = serializers.CharField(max_length=500)
    CreatedOn = serializers.CharField(max_length=500)
    UpdatedBy = serializers.CharField(max_length=500)
    UpdatedOn = serializers.CharField(max_length=500)
    RoleName = serializers.CharField(max_length=500)



