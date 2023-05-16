from ..models import *
from rest_framework import serializers

class CategoryTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model =  M_CategoryType
        fields = '__all__'