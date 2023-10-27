from ..models import *
from rest_framework import serializers

# Post and Put  Methods Serializer for M_PartyDetails

class PartyDetailsSerializer(serializers.ModelSerializer):
    class Meta :
        model= M_PartyDetails
        fields = '__all__'