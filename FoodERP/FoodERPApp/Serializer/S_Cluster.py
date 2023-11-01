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

    
 
class  GetPartydetailsOnclusterSerializer(serializers.Serializer):
    
    id = serializers.IntegerField()
    Name = serializers.CharField(max_length=500)
    Group_id = serializers.IntegerField()
    Cluster_id = serializers.IntegerField()
    Cluster_Name = serializers.CharField(max_length=500)
    SubCluster_id = serializers.IntegerField()
    SubCluster_Name = serializers.CharField(max_length=500)
    Supplier_id = serializers.IntegerField()
    Supplier_Name = serializers.CharField(max_length=500)
    

   
             

   
