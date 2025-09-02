from rest_framework import serializers
from users.models import User
from vendor.models import VehicleType, Vehicle
from member.models import VehicleBooking 
from driver.models import DriverVehicleType


class DriverVehicleTypeSerializer(serializers.ModelSerializer):
    vehicle_type_name = serializers.CharField(source='vehicle_type.name', read_only=True)
    
    class Meta:
        model = DriverVehicleType
        fields = ['vehicle_type', 'vehicle_type_name', 'is_approved', 'experience_years', 'created_at']


class DriverSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()
    vehicle_types = DriverVehicleTypeSerializer(source='drivervehicletype_set', many=True, read_only=True)
    distance = serializers.FloatField(read_only=True)  # Will be added dynamically
    
    class Meta:
        model = User
        fields = [
            'id', 'full_name', 'email', 'mobile', 'average_rating', 
            'total_orders_completed', 'is_available', 'vehicle_types',
            'latitude', 'longitude', 'distance', 'max_distance_km'
        ]
        read_only_fields = ['created_at']
        def get_full_name(self, obj):
            return f"{obj.first_name} {obj.last_name}"
# class VehicleBookingSerializer(serializers.ModelSerializer):
#     district_name = serializers.SerializerMethodField()
#     taluka_name = serializers.SerializerMethodField()
#     village_name = serializers.SerializerMethodField()
#     user_data = serializers.SerializerMethodField()
#     vehicle_data = serializers.SerializerMethodField()
#     assigned_driver_data = DriverSerializer(source='assigned_driver', read_only=True)
#     vehicle = serializers.PrimaryKeyRelatedField(queryset=Vehicle.objects.all())
#     remaining_charges = serializers.SerializerMethodField()
#     charges = serializers.SerializerMethodField()

#     def get_charges(self, obj):
#         if obj.vehicle:
#             try:
#                 return float(obj.vehicle.charges)
#             except (TypeError, ValueError):
#                 return 0.0  
#         return 0.0

#     def get_remaining_charges(self, obj):
#         try:
#             advance = float(obj.advance_rupees) if obj.advance_rupees else 0.0
#         except (TypeError, ValueError):
#             advance = 0.0
#         try:
#             total = float(obj.total_charges)
#         except (TypeError, ValueError):
#             total = 0.0
#         return total - advance

#     def get_user_data(self, obj):
#         from .serializers import UserSerializer  # Avoid circular import
#         return UserSerializer(obj.user).data if obj.user else None

#     def get_vehicle_data(self, obj):
#         from .serializers import VehicleSerializer  # Avoid circular import
#         return VehicleSerializer(obj.vehicle).data if obj.vehicle else None

#     def get_district_name(self, obj):
#         if obj.user and obj.user.district:
#             return obj.user.district.name
#         return None

#     def get_taluka_name(self, obj):
#         if obj.user and obj.user.taluka:
#             return obj.user.taluka.name
#         return None

#     def get_village_name(self, obj):
#         if obj.user and obj.user.Village:
#             return obj.user.Village.name
#         return None

#     class Meta:
#         model = VehicleBooking
#         fields = [
#             'booking_id', 'vehicle_data', 'register_no', 'date', 'time', 'total_area', 
#             'advance_rupees', 'vehicle', 'charges', 'remaining_charges', 
#             'rating', 'user_data', 'district_name', 'taluka_name', 'village_name',
#             'assigned_driver_data', 'status', 'service_latitude', 'service_longitude',
#             'service_address', 'assignment_timestamp'
#         ]

#     def create(self, validated_data):
#         vehicle = validated_data.pop('vehicle')
#         booking = VehicleBooking.objects.create(vehicle=vehicle, **validated_data)
#         return booking
