from ..models import *
from rest_framework import serializers

class PartyTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model =  M_PartyType
        fields = '__all__'


   