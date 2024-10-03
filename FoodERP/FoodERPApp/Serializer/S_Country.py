from rest_framework import serializers
from ..models import *

class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model =  M_Country
        fields = '__all__'