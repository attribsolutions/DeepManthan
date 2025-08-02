from rest_framework import serializers
from ..models import M_ERPUrls

class M_ERPUrlsSerializer(serializers.ModelSerializer):
    class Meta:
        model = M_ERPUrls
        fields = ['id', 'Name', 'Urls']
