from  ..models import M_Items
from rest_framework import serializers


class M_ItemsSerializer01(serializers.ModelSerializer):
    class Meta:
        model =  M_Items
        fields = '__all__'

class M_ItemsSerializer02(serializers.Serializer):
    id = serializers.IntegerField()
    ItemGroup_id= serializers.IntegerField()
    ItemGroupName = serializers.CharField()
    Name = serializers.CharField(max_length=500)
    Sequence = serializers.DecimalField(max_digits = 5,decimal_places=2)
    BaseUnitID_id = serializers.IntegerField()
    GSTPercentage = serializers.DecimalField(max_digits = 10,decimal_places=2)
    MRP = serializers.DecimalField(max_digits = 20,decimal_places=2)
    Rate =serializers.DecimalField(max_digits = 20,decimal_places=2)
    isActive = serializers.BooleanField(default=False)
    CreatedBy = serializers.IntegerField(default=False)
    CreatedOn = serializers.DateTimeField()
    UpdatedBy = serializers.IntegerField(default=False)
    UpdatedOn = serializers.DateTimeField()
            