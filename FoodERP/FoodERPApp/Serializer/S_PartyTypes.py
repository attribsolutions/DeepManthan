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


       

   