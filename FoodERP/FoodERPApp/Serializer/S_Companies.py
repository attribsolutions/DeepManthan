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

         
class PartyAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = MC_PartyAddress
        fields = '__all__'

class M_PartySerializer(serializers.ModelSerializer):
    PartyAddress = PartyAddressSerializer(many=True)
    class Meta:
        model = M_Parties
        fields = ['id','Name', 'Email', 'MobileNo', 'AlternateContactNo', 'SAPPartyCode', 'GSTIN', 'PAN', 'IsDivision', 'MkUpMkDn', 'isActive', 'CreatedBy', 'UpdatedBy', 'Company', 'District','PartyType','PriceList','State','City','Latitude','Longitude','IsApprovedParty','SkyggeID','UploadSalesDatafromExcelParty','Country', 'PartyAddress']

    def create(self, validated_data):
        party_address_data = validated_data.pop('PartyAddress')
        party = M_Parties.objects.create(**validated_data)
        for address_data in party_address_data:
            MC_PartyAddress.objects.create(Party=party, **address_data)
        return party

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

    
    

    
 
    
    
    
          


  