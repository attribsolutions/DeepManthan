from rest_framework import serializers
from ..models import M_PosSettings, MC_PosSettingDetails


class MC_PosSettingDetailsLiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = MC_PosSettingDetails
        fields = ['id', 'Setting_Value', 'PartyId', 'Is_Disabled']


class M_PosSettingsListSerializer(serializers.ModelSerializer):
    PosSettingDetails = serializers.SerializerMethodField()

    class Meta:
        model = M_PosSettings
        fields = [
            'id', 'Setting_Key', 'Setting_Value', 'Description',
            'Setting_Type', 'Is_Disabled', 'CreatedOn', 'UpdatedOn',
            'PosSettingDetails'
        ]

    def get_PosSettingDetails(self, obj):
        details = MC_PosSettingDetails.objects.filter(PosSetting=obj)
        return MC_PosSettingDetailsLiteSerializer(details, many=True).data


class MC_PosSettingDetailsCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MC_PosSettingDetails
        exclude = ['PosSetting']


class M_PosSettingsCreateUpdateSerializer(serializers.ModelSerializer):
    PosSettingDetails = MC_PosSettingDetailsCreateSerializer(many=True, required=False)

    class Meta:
        model = M_PosSettings
        fields = [
            'Setting_Key', 'Setting_Value', 'Description',
            'Setting_Type', 'Is_Disabled', 'PosSettingDetails'
        ]

    def create(self, validated_data):
        details_data = validated_data.pop('PosSettingDetails', [])
        setting = M_PosSettings.objects.create(**validated_data)
        for detail in details_data:
            MC_PosSettingDetails.objects.create(PosSetting=setting, **detail)
        return setting

    def update(self, instance, validated_data):
        details_data = validated_data.pop('PosSettingDetails', [])
        # Update setting fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Process PosSettingDetails
        existing_details = {d.PartyId: d for d in instance.PosSettingDetails.all()}
        incoming_party_ids = set()

        for detail in details_data:
            party_id = detail['PartyId']
            incoming_party_ids.add(party_id)
            if party_id in existing_details:
                detail_instance = existing_details[party_id]
                for key, value in detail.items():
                    setattr(detail_instance, key, value)
                detail_instance.save()
            else:
                MC_PosSettingDetails.objects.create(PosSetting=instance, **detail)

        return instance