from rest_framework import serializers
from ..models import *
from .S_Companies import * 
 
#List Filter 
class GeneralMasterserializerSecond(serializers.ModelSerializer):
    Company =C_CompanySerializer(read_only=True)
    class Meta:
        model = M_GeneralMaster
        fields = '__all__'    

#Get type,Post data,get single,put  Method
class GeneralMasterserializer(serializers.ModelSerializer):
    class Meta:
        model = M_GeneralMaster
        fields = '__all__'    
 
    
 
    
          


  