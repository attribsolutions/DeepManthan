from ..models import *
from rest_framework import serializers

class RolesSerializer(serializers.ModelSerializer):
    class Meta:
        model = M_SweetPOSRoles
        fields ="__all__"

class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = M_SweetPOSUser
        fields ="__all__"

