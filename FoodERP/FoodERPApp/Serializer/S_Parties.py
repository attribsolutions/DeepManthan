from asyncore import read
from dataclasses import fields

from ..models import *
from rest_framework import serializers


class DivisionsSerializer(serializers.ModelSerializer):
    
    class Meta:
        model =  M_Parties
        fields = ['id','Name'] 
              
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
    
    def update(self, instance, validated_data):
        instance.Name = validated_data.get(
            'Name', instance.Name)
        instance.PriceList = validated_data.get(
            'PriceList', instance.PriceList)
        instance.PartyType = validated_data.get(
            'PartyType', instance.PartyType)
        instance.Company = validated_data.get(
            'Company', instance.Company)
        instance.Email = validated_data.get(
            'Email', instance.Email)
        instance.MobileNo = validated_data.get(
            'MobileNo', instance.MobileNo)
        instance.AlternateContactNo = validated_data.get(
            'AlternateContactNo', instance.AlternateContactNo)
        instance.State = validated_data.get(
            'State', instance.State)
        instance.District = validated_data.get(
            'District', instance.District)
        instance.Taluka = validated_data.get(
            'Taluka', instance.Taluka)
        instance.City = validated_data.get(
            'City', instance.City)
        instance.GSTIN = validated_data.get(
            'GSTIN', instance.GSTIN)
        instance.PAN = validated_data.get(
            'PAN', instance.PAN)
        instance.IsDivision = validated_data.get(
            'IsDivision', instance.IsDivision)
        instance.District = validated_data.get(
            'District', instance.District)
        instance.isActive = validated_data.get(
            'isActive', instance.isActive)
        
        instance.MkUpMkDn = validated_data.get(
            'MkUpMkDn', instance.MkUpMkDn)
            
        instance.save()   
        
        for a in instance.PartyAddress.all():
            a.delete()
        
        for PartyAddress_data in validated_data['PartyAddress']:
            Party = MC_PartyAddress.objects.create(Party=instance, **PartyAddress_data)  
                  
        return instance
            
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


class AddressTypesSerializerSecond(serializers.ModelSerializer):
    class Meta:
        model =  M_AddressTypes
        fields = '__all__'
    
class PartyAddressSerializerSecond(serializers.ModelSerializer):
    AddressType = AddressTypesSerializerSecond(read_only=True)
    class Meta:
        model = MC_PartyAddress
        fields = ['id','Address', 'FSSAINo', 'FSSAIExipry', 'PIN', 'IsDefault', 'AddressType'] 

class DistrictSerializerSecond(serializers.ModelSerializer):
    class Meta:
        model =  M_PriceList
        fields = ['id','Name']
        
class StateSerializerSecond(serializers.ModelSerializer):
    class Meta:
        model =  M_States
        fields = ['id','Name'] 
        
class CompanySerializerSecond(serializers.ModelSerializer):
    class Meta:
        model =  C_Companies
        fields = ['id','Name']
        
class PartyTypeSerializerSecond(serializers.ModelSerializer):
    class Meta:
        model =  M_PartyType
        fields = ['id','Name']

class PriceListSerializerSecond(serializers.ModelSerializer):
    class Meta:
        model =  M_PriceList
        fields = ['id','Name']                           
    
class M_PartiesSerializerSecond(serializers.ModelSerializer):
    PartyAddress = PartyAddressSerializerSecond(many=True)
    District= DistrictSerializerSecond()
    State= StateSerializerSecond()
    Company = CompanySerializerSecond()
    PartyType = PartyTypeSerializerSecond()
    PriceList=PriceListSerializerSecond()
    class Meta:
        model =  M_Parties
        fields = '__all__'



  