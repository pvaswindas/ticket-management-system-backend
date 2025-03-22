from rest_framework import serializers
from .models import Ticket


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = '__all__'
        read_only_fields = ['created_user']

    def update(self, instance, validated_data):
        request = self.context['request']

        if instance.status == 'resolved':
            raise serializers.ValidationError(
                "Resolved tickets cannot be edited."
            )

        if 'assigned_to' in validated_data and not request.user.is_staff:
            raise serializers.ValidationError(
                "Only admins can assign tickets."
            )

        return super().update(instance, validated_data)
