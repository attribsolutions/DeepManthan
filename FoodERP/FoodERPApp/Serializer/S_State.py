from dataclasses import fields
from ..models import *
from rest_framework import serializers


class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model =   M_State
        fields = '__all__'