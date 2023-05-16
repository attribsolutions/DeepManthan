from rest_framework import serializers
from ..models import *

class C_CompanyGroupSerializer(serializers.ModelSerializer):
    class Meta :
        model= C_CompanyGroups
        fields = '__all__'  

class C_CompanyGroupSerializerSecond(serializers.ModelSerializer):
    class Meta :
        model= C_CompanyGroups
        fields = ['id','Name','IsSCM','CreatedBy','UpdatedBy']        