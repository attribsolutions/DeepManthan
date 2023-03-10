from dataclasses import fields
from django.forms import SlugField
from rest_framework import serializers
from ..models import *

# Post and Put Methods Serializer

class LoadingSheetDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model =  TC_LoadingSheetDetails
        fields = ['Invoice']

class LoadingSheetSerializer(serializers.ModelSerializer):
    LoadingSheetDetails = LoadingSheetDetailsSerializer(many=True)
    class Meta:
        model = T_LoadingSheet
        fields = ['id', 'Date', 'No', 'Party', 'Route', 'Vehicle', 'Driver', 'CreatedBy', 'UpdatedBy', 'LoadingSheetDetails']
        
    def create(self, validated_data):
        LoadingSheetDetails_data = validated_data.pop('LoadingSheetDetails')
        LoadingSheetID = T_LoadingSheet.objects.create(**validated_data)
        for LoadingSheet_data in LoadingSheetDetails_data:
            TC_LoadingSheetDetails.objects.create(LoadingSheet=LoadingSheetID, **LoadingSheet_data)
            
        return LoadingSheetID 
       
        
        
        