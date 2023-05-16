from ..models import *
from rest_framework import serializers
from ..Serializer.S_Parties import *

class M_DriverSerializer2(serializers.ModelSerializer):
    Party = DivisionsSerializer(read_only=True)
    class Meta :
        model= M_Drivers
        fields = '__all__'

class M_DriverSerializer(serializers.ModelSerializer):

    class Meta :
        model= M_Drivers
        fields = '__all__' 