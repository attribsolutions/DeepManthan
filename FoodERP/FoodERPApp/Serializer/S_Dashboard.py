from rest_framework import serializers
from ..models import *
# class Ord

class Invoices_Serializer(serializers.ModelSerializer):
    class Meta:
        model = T_Invoices
        fields = '__all__'