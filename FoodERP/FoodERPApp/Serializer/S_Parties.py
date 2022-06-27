from dataclasses import fields
from ..models import *
from rest_framework import serializers


class M_PartyTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model =  M_PartyType
        fields = '__all__'
        
class M_DivisionTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model =  M_DivisionType
        fields = '__all__'
                
class M_PartiesSerializer(serializers.ModelSerializer):
    class Meta:
        model =  M_Parties
        fields = '__all__'
        
class M_Partiesserializer1(serializers.Serializer):

    ID = serializers.IntegerField()
    Name = serializers.CharField(max_length=500)
    PartyTypeID = serializers.IntegerField( )
    PartyType = serializers.CharField(max_length=500)
    DividionTypeID =  serializers.IntegerField()
    DivisionType = serializers.CharField(max_length=500)
    companyID =  serializers.IntegerField()
    CompanyName = serializers.CharField(max_length=500)
    CustomerDivision =  serializers.IntegerField()
    Email = serializers.EmailField(max_length=200)
    Address = serializers.CharField(max_length=500)
    PIN = serializers.CharField(max_length=500)
    State = serializers.IntegerField()
    StateName = serializers.CharField(max_length=500)
    District = serializers.IntegerField()
    Taluka = serializers.IntegerField ()
    City = serializers.IntegerField()
    GSTN =  serializers.CharField(max_length=500)
    FSSAINo = serializers.CharField(max_length=500)
    FSSAIExipry = serializers.DateField()
    IsActive =  serializers.IntegerField()
    CreatedBy = serializers.IntegerField(default=False)
    CreatedOn = serializers.DateTimeField()
    UpdatedBy = serializers.IntegerField(default=False)
    UpdatedOn = serializers.DateTimeField()