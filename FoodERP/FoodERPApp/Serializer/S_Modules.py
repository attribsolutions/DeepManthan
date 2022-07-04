from dataclasses import fields
from ..models import *
from rest_framework import serializers



class H_ModulesSerializer(serializers.ModelSerializer):
    class Meta:
        model = H_Modules
        fields = '__all__'

