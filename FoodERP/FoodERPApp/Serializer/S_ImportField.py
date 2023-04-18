from rest_framework import serializers
from ..models import *

class ImportField_Serializer(serializers.ModelSerializer):
    class Meta:
        model = M_ImportFields
        fields = '__all__'

class PartyImportFieldsSerializer(serializers.ModelSerializer):
    class Meta:
        model = MC_PartyImportFields
        fields = '__all__'

#Show PartyImportfields Data List serializer

class PartyImportFieldSerializerList(serializers.Serializer):
    id = serializers.IntegerField()
    FieldName = serializers.CharField(max_length=500)
    IsCompulsory = serializers.BooleanField(default=False)
    ControlType_id = serializers.IntegerField()
    FieldValidation_id = serializers.IntegerField()
    Value =serializers.CharField(max_length=500)
    ControlTypeName =serializers.CharField(max_length=500)
    FieldValidationName = serializers.CharField(max_length=500)
         
        


        