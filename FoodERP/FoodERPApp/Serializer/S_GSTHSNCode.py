from asyncore import read
from dataclasses import fields
from ..models import *
from rest_framework import serializers


class M_GstHsnCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model =  M_GSTHSNCode
        fields = '__all__'
        


  