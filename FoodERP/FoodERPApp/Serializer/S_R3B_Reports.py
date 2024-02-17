from decimal import Decimal, InvalidOperation
from ..models import *
from rest_framework import serializers

class FloatDecimalField(serializers.Field):
    def to_representation(self, value):
        return float(value)

    
'''Details of Outward Supplies and inward supplies liable to reverse charge'''
class DOSAISLTRCSerializer(serializers.Serializer):
    NatureOfSupplies = serializers.CharField(max_length=100)
    TotalTaxableValue = FloatDecimalField()
    IntegratedTax = FloatDecimalField()
    CentralTax = FloatDecimalField()
    State_UTTax = FloatDecimalField()
    Cess = FloatDecimalField()
    
    def to_representation(self, obj):
        representation = super().to_representation(obj)
        representation['Nature Of Supplies'] = representation.pop('NatureOfSupplies')
        representation['Total Taxable Value'] = representation.pop('TotalTaxableValue')
        representation['Integrated Tax'] = representation.pop('IntegratedTax')
        representation['Central Tax'] = representation.pop('CentralTax')
        representation['State / UT Tax'] = representation.pop('State_UTTax')
        representation['Cess'] = representation.pop('Cess')
        return representation

   
class EligibleITCSerializer(serializers.Serializer):
    # id = serializers.IntegerField()
    Details = serializers.CharField(max_length=100)
    IntegratedTax=FloatDecimalField()
    CentralTax=FloatDecimalField()
    State_UTTax=FloatDecimalField()
    Cess=FloatDecimalField()
    
    def to_representation(self, obj):
        representation = super().to_representation(obj)
        representation['Details'] = representation.pop('Details')
        representation['Integrated Tax'] = representation.pop('IntegratedTax')
        representation['Central Tax'] = representation.pop('CentralTax')
        representation['State / UT Tax'] = representation.pop('State_UTTax')
        representation['Cess'] = representation.pop('Cess')
        return representation


class Query3Serializer (serializers.Serializer):
    # id = serializers.IntegerField()
    PlaceOfSupplyState_UT = serializers.CharField(max_length=100)
    TaxableValue=FloatDecimalField()
    AmountOfIntegratedTax=FloatDecimalField()
    
    def to_representation(self, obj):
        representation = super().to_representation(obj)
        representation ['Place Of Supply State / UT'] = representation.pop('PlaceOfSupplyState_UT')
        representation ['Taxable Value'] = representation.pop('TaxableValue')
        representation ['Amount Of Integrated Tax'] = representation.pop('AmountOfIntegratedTax')
        return representation