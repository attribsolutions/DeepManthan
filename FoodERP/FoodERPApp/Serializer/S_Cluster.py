from ..models import *
from rest_framework import serializers

# Post, Get,Getall, Put and Patch Methods Serializer for M_Cluster

class ClusterSerializer(serializers.ModelSerializer):
    class Meta :
        model= M_Cluster
        fields = '__all__'

# Post, Get, Getall,  Put and Patch Methods Serializer for M_SubCluster

class SubClusterSerializer(serializers.ModelSerializer):

    class Meta :
        model= M_SubCluster
        fields = '__all__'   


class SubClusterSerializerSecond(serializers.ModelSerializer):
    Cluster = ClusterSerializer(read_only=True)
    class Meta:
        model = M_SubCluster
        fields = '__all__'          

   
