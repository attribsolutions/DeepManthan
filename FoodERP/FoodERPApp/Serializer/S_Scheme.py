from ..models import *
from rest_framework import serializers

class SchemeSerializer(serializers.ModelSerializer):
    class Meta :
        model= M_Scheme
        fields = '__all__'