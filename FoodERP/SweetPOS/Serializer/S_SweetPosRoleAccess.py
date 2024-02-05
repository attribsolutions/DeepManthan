from rest_framework import serializers
from ..models import *

class SPOSRoleAccessSerializer(serializers.ModelSerializer):
    class Meta:
        model = M_SweetPOSRoleAccess
        fields = '__all__'

class SPOSRoleAccessSerializerSecond(serializers.Serializer):
    id = serializers.IntegerField()
    Name = serializers.CharField(max_length=500)
    CreatedBy = serializers.IntegerField()
    CreatedOn = serializers.DateTimeField()
    UpdatedBy = serializers.IntegerField()
    UpdatedOn = serializers.DateTimeField()
    Division = serializers.IntegerField()
    IsAddNewItem = serializers.BooleanField()
    IsImportItems = serializers.BooleanField()
    IsImportGroups = serializers.BooleanField()
    IsUpdateItem = serializers.BooleanField()
    IsCItemId = serializers.BooleanField()
    IsItemName = serializers.BooleanField()
    IsSalesModify = serializers.BooleanField()
    IsSalesDelete = serializers.BooleanField()
    IsUnitModify = serializers.BooleanField()
    IsShowVoucherButton = serializers.BooleanField()
    IsGiveSweetPOSUpdate = serializers.BooleanField()
    IsSweetPOSAutoUpdate = serializers.BooleanField()
    IsSweetPOSServiceAutoUpdate = serializers.BooleanField()
    IsEayBillUploadExist = serializers.BooleanField()       