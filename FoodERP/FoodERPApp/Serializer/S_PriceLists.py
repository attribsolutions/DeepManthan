from rest_framework import serializers
from ..models import *


# Get ALL Method
class PriceListSerializer(serializers.ModelSerializer):
    class Meta:
        model =  M_PriceList
        fields = '__all__'
        
class C_CompanySerializer(serializers.ModelSerializer):
    class Meta :
        model= C_Companies
        fields = ['id','Name']

class PartyTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model =  M_PartyType
        fields = ['id','Name']

class PriceListSerializerSecond(serializers.ModelSerializer):
    
    Company = C_CompanySerializer()
    PLPartyType = PartyTypeSerializer()
    
    class Meta:
        model = M_PriceList
        fields = ['id', 'Name', 'BasePriceListID', 'Company', 'MkUpMkDn', 'PLPartyType', 'CreatedBy', 'CreatedOn', 'UpdatedBy', 'UpdatedOn']
    
   
