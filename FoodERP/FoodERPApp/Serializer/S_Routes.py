from dataclasses import fields
from django.forms import SlugField
from rest_framework import serializers

from ..models import *



# Post and Put Methods Serializer

class RoutesSerializer(serializers.ModelSerializer):
    class Meta:
        model = M_Routes
        fields = ['id', 'Name', 'Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'IsActive', 'CreatedBy', 'UpdatedBy', 'Company', 'Party']



