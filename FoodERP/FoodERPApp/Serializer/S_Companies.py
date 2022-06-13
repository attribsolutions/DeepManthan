from dataclasses import fields
from django.forms import SlugField
from rest_framework import serializers

from ..models import *



class C_CompanyGroupsSerializer(serializers.ModelSerializer):
    class Meta :
        model= C_CompanyGroups
        fields = ['ID','Name']

class C_CompanySerializer2(serializers.ModelSerializer):
    CompanyGroup = C_CompanyGroupsSerializer()
    
    class Meta:
        model = C_Companies
        fields = '__all__'

class C_CompanySerializer(serializers.ModelSerializer):
    
    
    class Meta:
        model = C_Companies
        fields = '__all__'
