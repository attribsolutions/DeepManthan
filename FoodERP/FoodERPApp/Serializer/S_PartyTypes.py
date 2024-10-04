from ..models import *
from rest_framework import serializers


class PartyTypeSerializer(serializers.ModelSerializer):
    SAPIndicator = serializers.CharField(required=False)

    class Meta:
        model = M_PartyType
        fields = '__all__'

# class PartyTypeSerializerSecond(serializers.ModelSerializer):
#     SAPIndicator = serializers.CharField(required=False)
#     CountryName = serializers.SerializerMethodField()

#     class Meta:
#         model = M_PartyType
#         fields = ['Name', 'IsVendor', 'IsSCM', 'IsDivision', 'IsAdminDivision', 'CreatedBy', 'CreatedOn', 'UpdatedBy', 'UpdatedOn', 'IsRetailer', 'Company', 'IsFranchises', 'SAPIndicator', 'CountryID','CountryName'] 
    
#     def get_CountryName(self, obj):
#         # Perform a query to get the country name based on some identifier (e.g., CountryID)
#         country = M_Country.objects.filter(id=obj.CountryID).first()
#         if country:
#             return country.Country
#         return None

   