from ..models import *
from rest_framework import serializers
from ..Serializer.S_EmployeeTypes import *
from ..Serializer.S_Designations import *
from ..Serializer.S_States import *
from ..Serializer.S_Companies import C_CompanySerializer1

class M_EmployeesSerializer(serializers.ModelSerializer):
    class Meta:
        model = M_Employees
        fields = '__all__'
 
class M_EmployeesSerializer1(serializers.ModelSerializer):
    EmployeeType = M_EmployeeTypeSerializer01()
    Designations = M_DesignationsSerializer01()
    State = StateSerializer1()
    Companies = C_CompanySerializer1()
    class Meta:
        model = M_Employees
        fields = '__all__'
