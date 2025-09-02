from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers

class GatAdhikariTokenObtainSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        if self.user.role != 'Group_Admin':
            raise serializers.ValidationError(
                {'detail': 'You are not assigned as Gatadhikari.'},
                code='not_gatadhikari',
            )
        data['role'] = self.user.role   # helpful for frontend
        return data