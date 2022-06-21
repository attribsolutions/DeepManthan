from ..models import *
from rest_framework import serializers


class M_DesignationsSerializer(serializers.ModelSerializer):
    class Meta:
        model =  M_Designations
        fields = '__all__'

class M_DesignationsSerializer01(serializers.ModelSerializer):
    class Meta:
        model =  M_Designations
        fields = ['id','Name']        