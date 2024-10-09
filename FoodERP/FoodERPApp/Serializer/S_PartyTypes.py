from ..models import *
from rest_framework import serializers
from ..Serializer.S_Parties import *

class PartyTypeSerializer(serializers.ModelSerializer):
    SAPIndicator = serializers.CharField(required=False)

    class Meta:
        model = M_PartyType
        fields = '__all__'

class PartTypeSerializerSecond(serializers.ModelSerializer):
    SAPIndicator = serializers.CharField(required=False)
    Country = CountrySerializer()

    class Meta:
        model = M_PartyType
        fields = ['id','Name', 'IsVendor', 'IsSCM', 'IsDivision', 'IsAdminDivision', 'CreatedBy', 'CreatedOn', 'UpdatedBy', 'UpdatedOn', 'IsRetailer', 'Company', 'IsFranchises', 'SAPIndicator', 'Country']   

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        
        country_data = representation.pop('Country', None)
        if country_data:
            representation['CountryID'] = country_data.get('id')
            representation['CountryName'] = country_data.get('Country')
        return representation
       

   