from SweetPOS.models import *
from rest_framework import serializers


class SPOSRoleAccessSerializer(serializers.ModelSerializer):
    class Meta:
        model = M_SweetPOSRoleAccess
        fields = '__all__'

class SPOSRoleAccessSerializerSecond(serializers.Serializer):
    id = serializers.IntegerField()
    Name = serializers.CharField(max_length=500)
    CreatedBy = serializers.IntegerField()
    
    UpdatedBy = serializers.IntegerField()
    
    DivisionID = serializers.IntegerField()
    Party = serializers.IntegerField()
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
    IsEWayBillUploadExist = serializers.BooleanField() 
    TopRows = serializers.IntegerField()
    Query  = serializers.CharField(max_length=500)
    TouchSaleHistoryRows = serializers.IntegerField()
    LicenseValidTill  =  serializers.DateField()

class SPOSLog_inSerializer(serializers.ModelSerializer):
        class Meta:
            model = M_SweetPOSLogin
            fields = '__all__'

class MachineTypeSerializer(serializers.ModelSerializer):
        class Meta:
            model = M_SweetPOSMachine
            fields = '__all__'