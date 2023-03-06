from dataclasses import fields
from django.forms import SlugField
from rest_framework import serializers
from ..models import *


# Post and Put Methods Serializer

class SalemanSerializer(serializers.ModelSerializer):
    class Meta:
        model = M_Salesman
        fields = ['id', 'Name', 'MobileNo','IsActive', 'CreatedBy', 'UpdatedBy', 'Company', 'Party']


