from rest_framework import serializers
from ..models import M_PaymentModes,MC_PaymentModeDetails

# Serializer for M_PaymentModes
class M_PaymentModesSerializer(serializers.ModelSerializer):
    class Meta:
        model = M_PaymentModes
        fields = ['id', 'Payment_Mode','TenderCode','Description']

class MC_PaymentModeDetailsSerializer(serializers.ModelSerializer):
    Paymentmodes = M_PaymentModesSerializer(read_only=True)

    class Meta:
        model = MC_PaymentModeDetails
        fields = ['id', 'PartyId', 'Paymentmodes']
