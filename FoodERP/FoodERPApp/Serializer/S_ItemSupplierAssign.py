from rest_framework import serializers
from ..models import *

class ItemSupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model =  M_ItemSupplier
        fields = '__all__'

        