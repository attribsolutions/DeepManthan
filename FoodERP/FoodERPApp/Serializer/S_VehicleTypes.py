from ..models import *
from rest_framework import serializers

class VehicleTypesSerializer(serializers.ModelSerializer):
    class Meta :
        model= M_VehicleTypes
        fields = '__all__'