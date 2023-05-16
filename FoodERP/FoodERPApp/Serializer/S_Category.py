from rest_framework import serializers
from ..models import *

# Post and Put Methods Serializer

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = M_Category
        fields = '__all__'

# Get ALL Category,Get Single Category,Get Category On CategoryType Methods Serializers

class CategoryTypeSerializerSecond(serializers.ModelSerializer):
    class Meta:
        model =  M_CategoryType
        fields = '__all__'

class CategorySerializerSecond(serializers.ModelSerializer):
    CategoryType = CategoryTypeSerializerSecond(read_only=True)
    class Meta:
        model = M_Category
        fields = '__all__'      