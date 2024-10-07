from ..models import *
from rest_framework import serializers


class PartyTypeSerializer(serializers.ModelSerializer):
    SAPIndicator = serializers.CharField(required=False)

    class Meta:
        model = M_PartyType
        fields = '__all__'

    # def to_representation(self, instance):
    #     # get representation from ModelSerializer
    #     ret = super(PartyTypeSerializer, self).to_representation(instance)
    #     country = M_Country.objects.get(id=instance.CountryID)
    #     if country:
    #         ret['Country'] = country.Country  
    #     else:
    #         ret['Country'] = None  
            
    #     return ret


       

   