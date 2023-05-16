
from ..models import *
from rest_framework import serializers

class M_MarginsSerializer(serializers.ModelSerializer):
    class Meta:
        model =  M_MarginMaster
        fields = '__all__'

class M_MarginsSerializerSecond(serializers.Serializer):
    id = serializers.IntegerField()
    EffectiveDate = serializers.DateField()
    Company_id = serializers.IntegerField()
    PriceList_id = serializers.IntegerField()
    Party_id = serializers.IntegerField()
    CompanyName = serializers.CharField(max_length=100)
    PriceListName = serializers.CharField(max_length=100)
    PartyName = serializers.CharField(max_length=100)
    CreatedBy = serializers.IntegerField()
    CreatedOn = serializers.DateTimeField()
    CommonID= serializers.IntegerField()        