from decimal import Decimal, InvalidOperation
from ..models import *
from rest_framework import serializers

class FloatDecimalField(serializers.Field):
    def to_representation(self, value):
        return float(value)

    
'''Details of Outward Supplies and inward supplies liable to reverse charge'''
class DOSAISLTRCSerializer(serializers.Serializer):
    # id = serializers.IntegerField()
    NatureOfSupplies = serializers.CharField(max_length=100)
    TotalTaxableValue=FloatDecimalField()
    IntegratedTax=FloatDecimalField()
    CentralTax=FloatDecimalField()
    State_UTTax=FloatDecimalField()
    Cess =FloatDecimalField()
    
    
class EligibleITCSerializer(serializers.Serializer):
    # id = serializers.IntegerField()
    Details = serializers.CharField(max_length=100)
    IntegratedTax=FloatDecimalField()
    CentralTax=FloatDecimalField()
    State_UTTax=FloatDecimalField()
    Cess=FloatDecimalField()


class Query3Serializer (serializers.Serializer):
    # id = serializers.IntegerField()
    PlaceOfSupplyState_UT = serializers.CharField(max_length=100)
    TaxableValue=FloatDecimalField()
    AmountOfIntegratedTax=FloatDecimalField()
     