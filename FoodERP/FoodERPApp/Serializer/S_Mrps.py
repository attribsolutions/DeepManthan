from asyncore import read
from dataclasses import fields

from ..models import *
from rest_framework import serializers


class M_MRPsSerializer(serializers.ModelSerializer):
    class Meta:
        model =  M_MRPMaster
        fields = '__all__'