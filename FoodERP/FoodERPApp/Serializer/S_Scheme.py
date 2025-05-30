from ..models import *
from rest_framework import serializers

class SchemeSerializer(serializers.ModelSerializer):
    class Meta :
        model= M_Scheme
        fields = '__all__'
        
class SchemeTypeSerializer(serializers.ModelSerializer):
    class Meta :
        model= M_SchemeType
        fields = '__all__'