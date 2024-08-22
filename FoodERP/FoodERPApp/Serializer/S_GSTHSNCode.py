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
        
        
class MRPGSTHSNSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    EffectiveDate = serializers.DateField()
    GSTPercentage = serializers.DecimalField(max_digits=5, decimal_places=2)
    HSNCode=serializers.CharField(max_length=500)
    CommonID = serializers.IntegerField()
    CompanyName = serializers.CharField(max_length=100)
    ItemName = serializers.CharField(max_length=100)
    


  