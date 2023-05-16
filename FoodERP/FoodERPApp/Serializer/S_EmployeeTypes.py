from ..models import *
from rest_framework import serializers
 
 
class M_EmployeeTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = M_EmployeeTypes
        fields = '__all__'
 
class M_EmployeeTypeSerializer01(serializers.ModelSerializer):
    class Meta:
        model = M_EmployeeTypes
        fields = ['id','Name']