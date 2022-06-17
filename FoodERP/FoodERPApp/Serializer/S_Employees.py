from dataclasses import fields
from ..models import *
from rest_framework import serializers



class M_EmployessSerializer(serializers.ModelSerializer):
    class Meta:
        model = M_Employess
        fields = '__all__'