from ..models import *
from rest_framework import serializers

class M_DriverSerializer(serializers.ModelSerializer):
    class Meta :
        model= M_Drivers
        fields = '__all__'

 