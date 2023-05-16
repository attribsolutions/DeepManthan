from ..models import *
from rest_framework import serializers
from .S_Parties import * 
from .S_Items import * 
from .S_GSTHSNCode import * 
from .S_Margins import * 
from .S_Mrps import * 

class M_TermsAndConditionsSerializer(serializers.ModelSerializer):
    class Meta : 
        model = M_TermsAndConditions
        fields = '__all__'