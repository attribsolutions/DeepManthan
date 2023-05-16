from ..models import *
from rest_framework import serializers
  
class Employeeserializer(serializers.Serializer):
    id = serializers.IntegerField()
    Name = serializers.CharField(max_length=500) 

class Userserializer(serializers.Serializer):
    id = serializers.IntegerField()
    LoginName = serializers.CharField(max_length=500)         
    AdminPassword = serializers.CharField(max_length=500)    
               
   


   