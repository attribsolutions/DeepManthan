from dataclasses import fields

from ..Serializer.S_PartyTypes import PartyTypeSerializer
from ..models import *
from rest_framework import serializers


class DivisionsSerializer(serializers.ModelSerializer):
    
    class Meta:
        model =  M_Parties
        fields = ['id','Name'] 
        # fields = '__all__'      

class AddressTypesSerializer(serializers.ModelSerializer):
    class Meta:
        model =  M_AddressTypes
        fields = '__all__'
        
class PartyAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = MC_PartyAddress
        fields = ['Address', 'FSSAINo', 'FSSAIExipry', 'PIN', 'IsDefault', 'AddressType']                

class M_PartiesSerializer(serializers.ModelSerializer):
    PartyAddress = PartyAddressSerializer(many=True)
    class Meta:
        model =  M_Parties
        fields = '__all__'
        
    def create(self, validated_data):
        PartyAddress_data = validated_data.pop('PartyAddress')
        PartyID= M_Parties.objects.create(**validated_data)
        
        for PartyAddress in PartyAddress_data:
            Party = MC_PartyAddress.objects.create(Party=PartyID, **PartyAddress) 
               
        return PartyID
       

        
class M_PartiesSerializer1(serializers.Serializer):

    id = serializers.IntegerField()
    Name = serializers.CharField(max_length=500)
    PartyType_id = serializers.IntegerField( )
    PartyTypeName = serializers.CharField(max_length=500)
    PriceList_id =  serializers.IntegerField()
    PriceListName = serializers.CharField(max_length=500)
    Company_id =  serializers.IntegerField()
    CompanyName = serializers.CharField(max_length=500)
    Email = serializers.EmailField(max_length=200)
    Address = serializers.CharField(max_length=500)
    MobileNo=serializers.IntegerField()
    AlternateContactNo=serializers.CharField(max_length=500)
    PIN = serializers.CharField(max_length=500)
    State_id = serializers.IntegerField()
    StateName = serializers.CharField(max_length=500)
    District_id = serializers.IntegerField()
    DistrictName = serializers.CharField(max_length=500)
    Taluka = serializers.IntegerField ()
    City = serializers.IntegerField()
    GSTIN =  serializers.CharField(max_length=500)
    PAN =  serializers.CharField(max_length=500)
    FSSAINo = serializers.CharField(max_length=500)
    FSSAIExipry = serializers.DateField()
    isActive =  serializers.BooleanField()
    CreatedBy = serializers.IntegerField(default=False)
    CreatedOn = serializers.DateTimeField()
    UpdatedBy = serializers.IntegerField(default=False)
    UpdatedOn = serializers.DateTimeField()
    
    