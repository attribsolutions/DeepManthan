from dataclasses import fields
from ..models import *
from rest_framework import serializers


class M_RolesSerializer(serializers.ModelSerializer):
    class Meta:
        model =  M_Roles
        fields = '__all__'