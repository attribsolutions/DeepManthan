from dataclasses import fields
from ..models import *
from rest_framework import serializers


        
                
class M_PartiesSerializer(serializers.ModelSerializer):
    class Meta:
        model =  M_Parties
        fields = '__all__'
        
class M_PartiesSerializer1(serializers.Serializer):

    id = serializers.IntegerField()
    Name = serializers.CharField(max_length=500)
    PartyType_id = serializers.IntegerField( )
    PartyTypeName = serializers.CharField(max_length=500)
    DivisionType_id =  serializers.IntegerField()
    DivisionTypeName = serializers.CharField(max_length=500)
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