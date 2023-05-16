from ..models import *
from rest_framework import serializers

class H_PageAccessSerializer(serializers.ModelSerializer):
    class Meta:
        model =  H_PageAccess
        fields = '__all__'