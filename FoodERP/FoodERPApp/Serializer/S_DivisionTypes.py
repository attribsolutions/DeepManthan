from dataclasses import fields
from ..models import *
from rest_framework import serializers



class M_DivisionTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model =  M_DivisionType
        fields = '__all__'