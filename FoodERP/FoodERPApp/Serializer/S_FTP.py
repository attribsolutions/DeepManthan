from rest_framework import serializers
from ..models import *



class FTPFileDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = M_SAPCustomerLedger
        fields = '__all__'