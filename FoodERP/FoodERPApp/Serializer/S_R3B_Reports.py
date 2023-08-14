from decimal import Decimal, InvalidOperation
from ..models import *
from rest_framework import serializers

class FloatDecimalField(serializers.Field):
    def to_representation(self, value):
        return float(value)

    
'''Details of Outward Supplies and inward supplies liable to reverse charge'''
class DOSAISLTRCSerializer(serializers.Serializer):
    # id = serializers.IntegerField()
    A = serializers.CharField(max_length=100)
    Taxablevalue=FloatDecimalField()
    IGST=FloatDecimalField()
    CGST=FloatDecimalField()
    SGST=FloatDecimalField()
    Cess=FloatDecimalField()
    
    
class EligibleITCSerializer(serializers.Serializer):
    # id = serializers.IntegerField()
    A = serializers.CharField(max_length=100)
    IGST=FloatDecimalField()
    CGST=FloatDecimalField()
    SGST=FloatDecimalField()
    Cess=FloatDecimalField()


class Query3Serializer (serializers.Serializer):
    # id = serializers.IntegerField()
    states = serializers.CharField(max_length=100)
    Taxablevalue=FloatDecimalField()
    IGST=FloatDecimalField()
     