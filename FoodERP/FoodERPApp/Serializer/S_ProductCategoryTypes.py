from dataclasses import fields
from ..models import *
from rest_framework import serializers


class M_ProductCategoryTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model =  M_ProductCategoryType
        fields = '__all__'