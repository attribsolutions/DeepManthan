from ..models import *
from rest_framework import serializers


class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model =   M_State
        fields = '__all__'

class StateSerializer1(serializers.ModelSerializer):
    class Meta:
        model =   M_State
        fields = ['id','Name']