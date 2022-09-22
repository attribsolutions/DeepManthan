from asyncore import read
from dataclasses import fields

from ..models import *
from rest_framework import serializers


class M_MarginsSerializer(serializers.ModelSerializer):
    class Meta:
        model =  M_MarginMaster
        fields = '__all__'