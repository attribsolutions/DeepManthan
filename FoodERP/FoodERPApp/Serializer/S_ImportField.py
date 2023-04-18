from rest_framework import serializers
from ..models import *

class ImportField_Serializer(serializers.ModelSerializer):
    class Meta:
        model = M_ImportFields
        fields = '__all__'

# class PartyImportFields_Serializer(serializers.ModelSerializer):
#     ImportField = ImportField_Serializer(read_only=True)
#     class Meta:
#         model = MC_PartyImportFields
#         fields = '__all__'