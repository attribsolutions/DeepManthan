from rest_framework import serializers
from ..models import *

# Get ALL Method
class C_CompanyGroupSerializerSecond(serializers.ModelSerializer):
    class Meta:
        model = C_CompanyGroups
        fields = '__all__'

class C_CompanySerializerSecond(serializers.ModelSerializer):
    CompanyGroup= C_CompanyGroupSerializerSecond(read_only=True,)
    class Meta:
        model = C_Companies
        fields = '__all__'
          
class M_PartySerializer(serializers.ModelSerializer):
    class Meta:
        model = M_Parties
        fields = '__all__'

# POST AND PUT Method
class C_CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = C_Companies
        fields = '__all__'

       

# GET Method


class PartyTypeserializer(serializers.Serializer):
    id = serializers.IntegerField()
    Name = serializers.CharField(max_length=100)
    IsSCM =serializers.BooleanField()
    IsDivision =serializers.BooleanField()
    

    class C_CompanySerializer(serializers.ModelSerializer):
        class Meta:
            model = C_Companies
            fields = 'CompanyGroup'

    
    

    
 
    
    
    
          


  