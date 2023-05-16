from ..models import *
from rest_framework import serializers

class M_UnitsSerializer(serializers.ModelSerializer):
    class Meta :
        model= M_Units
        fields = ['id','Name']