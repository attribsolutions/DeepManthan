from dataclasses import fields
from ..models import *
from rest_framework import serializers

class M_EmployeesSerializer(serializers.ModelSerializer):
    class Meta:
        model = M_Employees
        fields = '__all__'