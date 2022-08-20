from dataclasses import fields
from django.forms import SlugField
from rest_framework import serializers

from ..models import *

# Get ALL Method
class ProductCategorySerializer(serializers.ModelSerializer):
 
    class Meta:
        model = M_ProductCategory
        fields = '__all__'

class ProductCategorySerializer2(serializers.Serializer):
    id = serializers.IntegerField()
    Name = serializers.CharField(max_length=100)
    ProductCategoryType_id = serializers.IntegerField()
    ProductCategoryTypeName = serializers.CharField(max_length=100)
      