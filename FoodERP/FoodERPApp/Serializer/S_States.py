from ..models import *
from rest_framework import serializers


class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model =   M_States
        fields = '__all__'
