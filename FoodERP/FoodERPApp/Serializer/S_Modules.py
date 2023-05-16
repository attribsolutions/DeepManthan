from ..models import *
from rest_framework import serializers

class H_ModulesSerializer(serializers.ModelSerializer):
    class Meta:
        model = H_Modules
        fields = '__all__'


class H_ModulesSerializer2(serializers.ModelSerializer):
    class Meta:
        model = H_Modules
        fields = ['id','Name']
