from dataclasses import fields
from ..models import *
from rest_framework import serializers


class ResionSerializer(serializers.ModelSerializer):
    class Meta:
        model =  M_Resion
        fields = '__all__'