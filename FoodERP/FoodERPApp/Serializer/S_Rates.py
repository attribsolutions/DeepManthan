from ..models import *
from rest_framework import serializers

class M_RatesSerializer(serializers.ModelSerializer):
    class Meta:
        model =  M_RateMaster
        fields = '__all__'        
        
class M_RatesSerializerSecond(serializers.Serializer):
    id = serializers.IntegerField()
    EffectiveDate = serializers.DateField()
    Company_id = serializers.IntegerField()  
    CompanyName = serializers.CharField(max_length=100)   
    CreatedBy = serializers.IntegerField()
    CreatedOn = serializers.DateTimeField()
    CommonID= serializers.IntegerField()     
            
        