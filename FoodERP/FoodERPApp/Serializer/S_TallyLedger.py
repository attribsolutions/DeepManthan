from ..models import *
from rest_framework import serializers




class TallyLedgerSerializer(serializers.ModelSerializer):
    class Meta:
        model = M_Ledger
        fields = '__all__'