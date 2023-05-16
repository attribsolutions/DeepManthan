from rest_framework import serializers
from ..models import  *
   
class FSSAINoSerializer(serializers.ModelSerializer):
    class Meta:
        model = MC_PartyAddress
        fields = '__all__'
        
class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = C_Companies
        fields = '__all__'
        
class PriceListSerializer(serializers.ModelSerializer):
    class Meta:
        model = M_PriceList
        fields = '__all__'

class PartyTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = M_PartyType
        fields = '__all__'
        
class DistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = M_Districts
        fields = '__all__'

class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model = M_States
        fields = '__all__'
        
class SubPartySerializer(serializers.ModelSerializer):
    District= DistrictSerializer(read_only=True)
    State= StateSerializer(read_only=True)
    PriceList= PriceListSerializer(read_only=True)
    PartyType= PartyTypeSerializer(read_only=True)
    Company= CompanySerializer(read_only=True)
    
    class Meta:
        model = M_Parties
        fields = '__all__' 


class PartyWiseSerializer(serializers.ModelSerializer):
    SubParty= SubPartySerializer(read_only=True)
    Party = SubPartySerializer(read_only=True)
    class Meta:
        model =   MC_PartySubParty
        fields = '__all__'
        
