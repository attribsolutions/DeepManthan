from dataclasses import fields
from django.forms import SlugField
from rest_framework import serializers
from ..models import *


class ReceiptModeSerializer(serializers.ModelSerializer):
    class Meta:
        model = M_GeneralMaster
        fields = '__all__'