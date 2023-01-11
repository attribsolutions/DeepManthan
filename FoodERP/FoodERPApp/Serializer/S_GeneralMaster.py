from dataclasses import fields
from django.forms import SlugField
from rest_framework import serializers
from ..models import *



# Get ALL Method

          
# POST AND PUT Method
class C_CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = C_Companies
        fields = '__all__'

# GET Method


class GeneralMasterserializer(serializers.Serializer):
    
    

    class C_CompanySerializer(serializers.ModelSerializer):
        class Meta:
            model = C_Companies
            fields = 'CompanyGroup'

    
    

    
 
    
    
    
          


  