from ..models import *
from rest_framework import serializers

class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model =   M_States
        fields = '__all__'

class DistrictsSerializer(serializers.ModelSerializer):
    class Meta:
        model =   M_Districts
        fields = '__all__'

class DistrictsSerializerSecond(serializers.ModelSerializer):
    class Meta:
        model =   M_Districts
        fields = ['id','Name']


class CitiesSerializerSecond(serializers.ModelSerializer):
    District = DistrictsSerializerSecond(read_only=True)
    class Meta:
        model =   M_Cities
        fields = ['id','Name','CreatedBy','CreatedOn','UpdatedBy','District']

class CitiesSerializer(serializers.ModelSerializer):
    class Meta:
        model =   M_Cities
        fields = ['Name','District','CreatedBy','CreatedOn','UpdatedBy']
