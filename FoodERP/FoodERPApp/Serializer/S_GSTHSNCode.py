from ..models import *
from rest_framework import serializers

class CompanySerializerSecond(serializers.ModelSerializer):
    class Meta:
        model = C_Companies
        fields = ['id','Name'] 
        
class M_GstHsnCodeSerializer(serializers.ModelSerializer):
    company = CompanySerializerSecond(read_only=True)
    class Meta:
        model =  M_GSTHSNCode
        fields = '__all__'
        


  