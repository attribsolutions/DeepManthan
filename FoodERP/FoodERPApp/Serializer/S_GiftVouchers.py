from ..models import *
from rest_framework import serializers


class GiftVoucherSerializer(serializers.ModelSerializer):
    class Meta :
        model= M_GiftVoucherCode
        fields = '__all__'