from rest_framework import serializers

from ...models import Device
from ...service import update_or_create_device


class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = ("token", "name", "active", "type")

    def create(self, validated_data):
        request = self.context["request"]
        self.instance, _ = update_or_create_device(
            user=request.user,
            token=validated_data["token"],
            active=validated_data["active"],
            _type=validated_data["type"],
            name=validated_data["name"],
        )
        return self.instance
