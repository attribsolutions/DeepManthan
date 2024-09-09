
from ..models import *
from rest_framework import serializers

class M_MRPsSerializer(serializers.ModelSerializer):
    class Meta:
        model =  M_MRPMaster
        fields = '__all__'
        

class M_MRPsSerializerSecond(serializers.Serializer):
    id = serializers.IntegerField()
    EffectiveDate = serializers.DateField()
    Company_id = serializers.IntegerField()
    Division_id = serializers.IntegerField()
    Party_id = serializers.IntegerField()
    CompanyName = serializers.CharField(max_length=100)
    DivisionName = serializers.CharField(max_length=100)
    PartyName = serializers.CharField(max_length=100)
    CreatedBy = serializers.IntegerField()
    CreatedOn = serializers.DateTimeField()
    CommonID= serializers.IntegerField() 
     
    
class MRPListDetailsSerializer(serializers.Serializer):
    id = serializers.IntegerField() 
    EffectiveDate = serializers.DateField()
    MRP = serializers.DecimalField(max_digits=20, decimal_places=2)
    CommonID = serializers.IntegerField()
    CompanyName = serializers.CharField(max_length=100)
    ItemName = serializers.CharField(max_length=100)
    ItemCount = serializers.IntegerField()