from dataclasses import fields
from django.forms import SlugField
from rest_framework import serializers

from ..models import *

# Get ALL Method
class SubProductCategorySerializer(serializers.ModelSerializer):
 
    class Meta:
        model = M_ProductSubCategory
        fields = '__all__'

class SubProductCategorySerializer2(serializers.Serializer):
    id = serializers.IntegerField()
    Name = serializers.CharField(max_length=100)
    ProductCategory_id = serializers.IntegerField()
    ProductCategoryName = serializers.CharField(max_length=100)