from ..models import *
from rest_framework import serializers


class M_EmployeesSerializer01(serializers.ModelSerializer):
    class Meta:
        model =  M_Employees
        fields = '__all__'

 
class M_EmployeesSerializer02(serializers.Serializer):
    id = serializers.IntegerField()
    Name = serializers.CharField(max_length=100)
    Address = serializers.CharField(max_length=500)
    Mobile = serializers.CharField(max_length=100)
    email = serializers.EmailField(max_length=255) 
    DOB = serializers.CharField(max_length=100)
    PAN = serializers.CharField(max_length=100)
    AadharNo = serializers.CharField(max_length=100)
    working_hours =  serializers.DecimalField(max_digits = 15,decimal_places=2)
    CreatedBy = serializers.IntegerField(default=False)
    CreatedOn = serializers.DateTimeField()
    UpdatedBy = serializers.IntegerField(default=False)
    UpdatedOn = serializers.DateTimeField()
    CompanyName = serializers.CharField(max_length=100)
    DesignationName = serializers.CharField(max_length=100)
    EmployeeTypeName = serializers.CharField(max_length=100)
    StateName = serializers.CharField(max_length=100)
    Companies_id = serializers.IntegerField()
    Designation_id = serializers.IntegerField()
    EmployeeType_id = serializers.IntegerField()
    State_id = serializers.IntegerField()


   