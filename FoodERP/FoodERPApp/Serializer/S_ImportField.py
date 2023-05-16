from rest_framework import serializers
from ..models import *


class ControlType_Serializer(serializers.ModelSerializer):
    class Meta:
        model = M_ControlTypeMaster
        fields = ['id','Name']

class FieldValidations_Serializer(serializers.ModelSerializer):
    class Meta:
        model = M_FieldValidations
        fields = ['id','Name']

class ImportFieldSerializerSecond(serializers.ModelSerializer):
    ControlType = ControlType_Serializer(read_only=True)
    FieldValidation = FieldValidations_Serializer(read_only=True)
    class Meta:
        model = M_ImportFields
        fields = '__all__'

#Save  Importfields  serializer        
class ImportFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = M_ImportFields
        fields = '__all__'

#Save  PartyImportfields  serializer
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
    Value = serializers.CharField(max_length=500)
    Party_id = serializers.IntegerField()
    ControlTypeName =serializers.CharField(max_length=500)
    FieldValidationName = serializers.CharField(max_length=500)
    RegularExpression = serializers.CharField(max_length=500)
        


        