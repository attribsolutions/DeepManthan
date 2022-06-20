from dataclasses import fields
from ..models import *
from rest_framework import serializers
from FoodERPApp.Serializer.S_State import *
from FoodERPApp.Serializer.S_Resion import *


class M_EmployeesSerializer(serializers.ModelSerializer):
    class Meta:
        model = M_Employees
        fields = '__all__'
 
 