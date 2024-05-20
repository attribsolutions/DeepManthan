from ..models import *
from rest_framework import serializers

class SPOSstockSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = T_SPOSStock
        fields = '__all__'
