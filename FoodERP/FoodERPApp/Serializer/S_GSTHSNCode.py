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
        
class GSTHSNCodeCompanyPartyTypeSerializer(serializers.Serializer):
    id=serializers.IntegerField()
    EffectiveDate= serializers.DateField()
    GSTPercentage=serializers.DecimalField(max_digits=10, decimal_places=2)
    HSNCode=serializers.CharField(max_length=100) 
    CommonID=serializers.IntegerField() 
    IsDeleted=serializers.BooleanField(default=False)
    CreatedBy=serializers.IntegerField()
    CreatedOn=serializers.DateTimeField()
    UpdatedBy = serializers.IntegerField()
    UpdatedOn=serializers.DateTimeField()
    CompanyID=serializers.IntegerField()
    PartyTypeID=serializers.IntegerField()
    PartyTypeName = serializers.CharField(max_length=100)
    CompanyName = serializers.CharField(max_length=100)