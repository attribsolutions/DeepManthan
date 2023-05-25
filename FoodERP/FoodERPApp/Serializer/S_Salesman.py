from rest_framework import serializers
from ..models import *

# Post and Put Methods Serializer
class RouteNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = M_Routes
        fields = ['id','Name']

class SalesManRouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = MC_SalesManRoutes
        fields = ['Route']

class SalesmanSerializer(serializers.ModelSerializer):
    SalesmanRoute = SalesManRouteSerializer(many = True)
    class Meta:
        model = M_Salesman
        fields = ['id', 'Name', 'MobileNo','IsActive', 'CreatedBy', 'UpdatedBy', 'Company', 'Party','SalesmanRoute']

    def create(self, validated_data):
        Salesman_Route = validated_data.pop('SalesmanRoute')

        SalesManID = M_Salesman.objects.create(**validated_data)

        for a in Salesman_Route:
            MC_SalesManRoutes.objects.create(Salesman=SalesManID, **a)

        return SalesManID
    
    def update(self, instance, validated_data):

        instance.Name = validated_data.get(
            'Name', instance.Name)   
        instance.MobileNo = validated_data.get(
            'MobileNo', instance.MobileNo)
        instance.UpdatedBy = validated_data.get(
            'UpdatedBy', instance.UpdatedBy)   
        instance.Company = validated_data.get(
            'Company', instance.Company)
        instance.Party = validated_data.get(
            'Party', instance.Party)

        instance.save()

       
        for a in instance.SalesmanRoute.all():
            a.delete()
   
        for ab in validated_data['SalesmanRoute']:
            MC_SalesManRoutes.objects.create(Salesman=instance, **ab)
   
        return instance 



class SalesManRouteSerializersecond(serializers.ModelSerializer):
    Route = RouteNameSerializer()
    class Meta:
        model = MC_SalesManRoutes
        fields = ['Route']

class SalesmanSerializerSecond(serializers.ModelSerializer):
    SalesmanRoute = SalesManRouteSerializersecond(many = True)
    class Meta:
        model = M_Salesman
        fields = ['id', 'Name', 'MobileNo','IsActive', 'CreatedBy', 'UpdatedBy', 'Company', 'Party','SalesmanRoute']

