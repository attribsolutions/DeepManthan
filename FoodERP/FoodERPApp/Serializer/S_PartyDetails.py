from ..models import *
from rest_framework import serializers

# Post and Put  Methods Serializer for M_PartyDetails

class PartyDetailsSerializer(serializers.ModelSerializer):
    class Meta :
        model= M_PartyDetails
        fields = '__all__'

class  GetPartydetailsSerializer(serializers.Serializer):
    
    id = serializers.IntegerField()
    PartyID = serializers.IntegerField()
    PartyName = serializers.CharField(max_length=500)
    Group_id = serializers.IntegerField()
    Cluster_id = serializers.IntegerField()
    ClusterName = serializers.CharField(max_length=500)
    SubCluster_id = serializers.IntegerField()
    SubClusterName = serializers.CharField(max_length=500)
    Supplier_id = serializers.IntegerField()
    SupplierName = serializers.CharField(max_length=500)
    GM_id = serializers.IntegerField()
    NH_id = serializers.IntegerField()
    RH_id = serializers.IntegerField()
    ASM_id = serializers.IntegerField()
    SE_id = serializers.IntegerField()
    SO_id = serializers.IntegerField()
    SR_id = serializers.IntegerField()
    MT_id = serializers.IntegerField()