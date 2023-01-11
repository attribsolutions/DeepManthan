from dataclasses import fields
from django.forms import SlugField
from rest_framework import serializers
from ..models import *

from .S_Companies import * 
 


class GeneralMasterserializer(serializers.ModelSerializer):
    Company =C_CompanySerializer(read_only=True)
    class Meta:
        model = M_GeneralMaster
        fields = '__all__'    

    
 
    
    
    
          


  