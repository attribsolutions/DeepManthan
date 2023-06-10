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
        
class StateSerializerSecond(serializers.ModelSerializer):
    class Meta:
        model =   M_States
        fields = ['id','Name'] 

class DistrictsSerializerThird(serializers.ModelSerializer):
    State = StateSerializerSecond(read_only=True)
    class Meta:
        model =   M_Districts
        fields = ['id','Name','State'] 
        
class CitiesSerializerSecond(serializers.ModelSerializer):
    District = DistrictsSerializerThird(read_only=True)
    class Meta:
        model =   M_Cities
        fields = ['id','Name','CreatedBy','CreatedOn','UpdatedBy','District']

class CitiesSerializer(serializers.ModelSerializer):
    class Meta:
        model =   M_Cities
        fields = ['Name','District','CreatedBy','CreatedOn','UpdatedBy']
