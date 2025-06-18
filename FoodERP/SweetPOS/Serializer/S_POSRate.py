from ..models import *
from rest_framework import serializers


class RateSerializer(serializers.ModelSerializer):
    class Meta:
        model = M_SPOSRateMaster
        fields = ['POSRateType', 'IsChangeRateToDefault', 'EffectiveFrom', 'Rate', 'ItemID']
