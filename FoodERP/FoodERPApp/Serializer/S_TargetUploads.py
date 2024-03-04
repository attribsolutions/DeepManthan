from rest_framework import serializers
from ..models import *
from datetime import datetime

class PartySerializer(serializers.ModelSerializer):
    class Meta:
        model = M_Parties
        fields = '__all__'

class TargetUploadsSerializer(serializers.ModelSerializer):
    Party = PartySerializer(read_only=True)
    class Meta:
        model = T_TargetUploads
        fields = '__all__'


