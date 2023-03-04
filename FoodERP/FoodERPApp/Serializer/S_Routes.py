from dataclasses import fields
from django.forms import SlugField
from rest_framework import serializers
from ..models import *




# Post and Put Methods Serializer

class RoutesSerializer(serializers.ModelSerializer):
    class Meta:
        model = M_Routes
        fields = ['id', 'Name', 'Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'IsActive', 'CreatedBy', 'UpdatedBy', 'Company', 'Party']
        
class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model =  M_Routes
        fields = '__all__'        
        
class PartySerializer(serializers.ModelSerializer):
    class Meta:
        model =  M_Parties
        fields = '__all__'
                 
class RoutesUpdateListSerializer(serializers.ModelSerializer):
    Party = PartySerializer(read_only=True)
    SubParty = PartySerializer(read_only=True)
    Route = RoutesSerializer()
    class Meta:
        model = MC_PartySubParty
        fields = '__all__'


