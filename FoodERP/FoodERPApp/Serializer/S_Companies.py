from dataclasses import fields
from django.forms import SlugField
from rest_framework import serializers

from ..models import *



class C_CompanyGroupsSerializer(serializers.ModelSerializer):
    class Meta :
        model= C_CompanyGroups
        fields = ['id','Name']
        
class C_CompanyGroupsSerializer1(serializers.ModelSerializer):
    class Meta :
        model= C_CompanyGroups
        fields = '__all__'        
        
    

# Get ALL Method
class C_CompanySerializer1(serializers.ModelSerializer):
 
    CompanyGroup= serializers.SlugRelatedField(read_only=True,slug_field='Name')
    class Meta:
        model = C_Companies
        fields = '__all__'
       
        
# POST AND PUT Method
class C_CompanySerializer2(serializers.ModelSerializer):
    class Meta:
        model = C_Companies
        fields = '__all__'

# GET Method

class C_CompanySerializer3(serializers.Serializer):
    id = serializers.IntegerField()
    Name = serializers.CharField(max_length=100)
    Address = serializers.CharField(max_length=100)
    GSTIN = serializers.CharField(max_length=100)
    PhoneNo = serializers.CharField(max_length=100)
    CompanyAbbreviation = serializers.CharField(max_length=100)
    EmailID = serializers.CharField(max_length=100)
    CompanyGroup_id = serializers.IntegerField()
    CompanyGroupName = serializers.CharField(max_length=100)
    CreatedBy = serializers.IntegerField()
    UpdatedBy = serializers.IntegerField()


class DivisionTypeserializer(serializers.Serializer):
    id = serializers.IntegerField()
    Name = serializers.CharField(max_length=100)
    IsSCM =serializers.BooleanField()
    

    class C_CompanySerializer(serializers.ModelSerializer):
        class Meta:
            model = C_Companies
            fields = 'CompanyGroup'

    
    

    
 
    
    
    
          


  