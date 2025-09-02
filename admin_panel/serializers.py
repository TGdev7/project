from rest_framework import serializers
from users.models import DistrictModel,TalukaModel,VillageModel,GroupModel
from django.contrib.auth import get_user_model
from member.models import VehicleBooking
from users.models import User

class DistrictSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = DistrictModel
        fields = "__all__"

class TalukaSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = TalukaModel
        fields = "__all__"

class VillageSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = VillageModel
        fields = "__all__"

class GroupModelSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = GroupModel
from users.models import DriverUnavailablePeriod
class DriverUnavailablePeriodSerializer(serializers.ModelSerializer):
    class Meta:
        model = DriverUnavailablePeriod
        fields = ['id', 'driver', 'start_date', 'end_date']


        
# class AssignUserDriverSerializer(serializers.Serializer):
#     booking_id = serializers.IntegerField()
#     driver_id = serializers.IntegerField()

#     def validate(self, data):
#         from users.models import User
#         from member.models import VehicleBooking

#         try:
#             booking = VehicleBooking.objects.get(booking_id=data['booking_id'])
#         except VehicleBooking.DoesNotExist:
#             raise serializers.ValidationError("Invalid booking ID")

#         try:
#             driver = User.objects.get(id=data['driver_id'], role='driver')
#         except User.DoesNotExist:
#             raise serializers.ValidationError("Invalid driver ID or user is not a driver")

#         if not driver.is_available:
#             raise serializers.ValidationError("Driver is not available")

#         data['booking'] = booking
#         data['driver'] = driver
#         return data

#     def save(self):
#         booking = self.validated_data['booking']
#         driver = self.validated_data['driver']

#         booking.assigned_driver = driver
#         booking.status = 'confirmed'
#         booking.save()

#         driver.is_available = False
#         driver.save()

#         return booking
    
