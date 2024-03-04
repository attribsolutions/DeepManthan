from rest_framework import serializers
from ..models import *
from datetime import datetime

class TargetUploadsSerializer(serializers.ModelSerializer):
    class Meta:
        model = T_TargetUploads
        fields = '__all__'