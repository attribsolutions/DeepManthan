from rest_framework import serializers
from ..models import *


class EmployeeTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = M_EmployeeTypes
        fields = '__all__'


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = M_Roles
        fields = '__all__'


