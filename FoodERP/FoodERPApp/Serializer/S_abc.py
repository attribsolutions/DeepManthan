from dataclasses import fields
from django.forms import SlugField
from rest_framework import serializers

from ..models import *

class MC_RolePageAccessSerializer(serializers.ModelSerializer):
    class Meta :
        model= MC_RolePageAccess
        fields = '__all__'

class AbcSerializer(serializers.ModelSerializer):
    RoleAccess=MC_RolePageAccessSerializer(many=True)
    class Meta :
        model= M_RoleAccess
        fields = '__all__'
        