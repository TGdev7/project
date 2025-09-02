from rest_framework import serializers
from .models import *
from users.serializers import DriverUserRegisterSerializer
from users.models import User
from vendor.models import Vehicle
from vendor.serializers import VehicleSerializer
from users.serializers import DriverPublicSerializer
from member.models import VehicleBooking
from member.serializers import VehicleBookingSerializer

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from driver.models import DriverVehicleType
from vendor.serializers import VehicleTypeSerializer


class DriverProfileSerializer(serializers.ModelSerializer):
    user = DriverPublicSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role="Driver"), source="user", write_only=True
    )

    class Meta:
        model = User
        fields = [
            "id",
            "user",
            "user_id",
            "license_number",
            "vehicle_type",
            "is_driver_available",
            "district",
            "taluka",
            "village",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]

class DriverUserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "first_name", "last_name", "email", "mobile", 'adhar_no', 'dob', 'role',
            'pan_no', 'zipcode', 'country', 'district', 'taluka', 'Village',
            'address', 'house_or_building', 'road_or_area', 'landmark',
            'license_number', 'license_attachment', "state", "city"
        ]
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class DriverUsageLogSerializer(serializers.ModelSerializer):
    driver = DriverPublicSerializer(read_only=True)
    vehicle = VehicleSerializer(read_only=True)
    assigned_by = DriverPublicSerializer(read_only=True)

    driver_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.filter(role='Driver'), source='driver', write_only=True)
    vehicle_id = serializers.PrimaryKeyRelatedField(queryset=Vehicle.objects.all(), source='vehicle', write_only=True)
    assigned_by_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), source='assigned_by', write_only=True)

    class Meta:
        model = DriverUsageLog
        fields = [
            "id",
            "user",
            "user_id",
            "license_number",
            "vehicle_type",
            "is_driver_available",
            "district",
            "taluka",
            "village",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]


# class DriverUsageLogSerializer(serializers.ModelSerializer):
#     driver = DriverPublicSerializer(read_only=True)
#     vehicle = VehicleSerializer(read_only=True)
#     assigned_by = DriverPublicSerializer(read_only=True)

#     driver_id = serializers.PrimaryKeyRelatedField(
#         queryset=User.objects.filter(role="Driver"), source="driver", write_only=True
#     )
#     vehicle_id = serializers.PrimaryKeyRelatedField(
#         queryset=Vehicle.objects.all(), source="vehicle", write_only=True
#     )
#     assigned_by_id = serializers.PrimaryKeyRelatedField(
#         queryset=User.objects.all(), source="assigned_by", write_only=True
#     )

#     class Meta:
#         model = DriverUsageLog
#         fields = [
#             "id",
#             "driver",
#             "driver_id",
#             "vehicle",
#             "vehicle_id",
#             "assigned_by",
#             "assigned_by_id",
#             "start_time",
#             "end_time",
#             "is_active",
#             "member_address",
#             "job_address",
#             "pickup_address",
#             "remarks",
#             "created_at",
#             "updated_at",
#         ]
#         read_only_fields = ["created_at", "updated_at"]


class DriverUsageLogSerializer(serializers.ModelSerializer):
    driver = DriverPublicSerializer(read_only=True)
    vehicle = VehicleSerializer(read_only=True)
    assigned_by = DriverPublicSerializer(read_only=True)
    booking = VehicleBookingSerializer(read_only=True)

    driver_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.filter(role="Driver"), source="driver", write_only=True)
    vehicle_id = serializers.PrimaryKeyRelatedField(queryset=Vehicle.objects.all(), source="vehicle", write_only=True)
    assigned_by_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), source="assigned_by", write_only=True)
    booking_id = serializers.PrimaryKeyRelatedField(queryset=VehicleBooking.objects.all(), source="booking", write_only=True)

    class Meta:
        model = DriverUsageLog
        fields = [
            "id",
            "driver", "driver_id",
            "vehicle", "vehicle_id",
            "assigned_by", "assigned_by_id",
            "booking", "booking_id",
            "start_time", "end_time",
            "is_active",
            "member_address",
            # "service_address",
            "pickup_address",
            "remarks",
            "created_at", "updated_at"
        ]
        read_only_fields = ["created_at", "updated_at"]


from rest_framework import serializers
from .models import DriverVehicleType

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from driver.models import DriverVehicleType
from vendor.serializers import VehicleTypeSerializer


class DriverVehicleTypeSerializer(serializers.ModelSerializer):
    vehicle_type_details = VehicleTypeSerializer(source="vehicle_type", read_only=True)
    driver_name = serializers.CharField(source="User.full_name", read_only=True)

    class Meta:
        model = DriverVehicleType
        fields = [
            "id",
            "driver",
            "vehicle_type",
            "vehicle_type_details",
            "driver_name",
            "is_approved",
            "experience_years",
            "certification_document",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "driver",
            "created_at",
            "driver_name",
        ]

    def validate_experience_years(self, value):
        if value < 0:
            raise serializers.ValidationError("Experience years cannot be negative.")
        return value
from rest_framework import serializers
from member.models import VehicleBooking

class DriverBookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleBooking
        fields = '__all__'  # or customize


# driver/serializers.py

from rest_framework import serializers
from .models import DriverUsageLog

class DriverJobDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = DriverUsageLog
        fields = [
            'id',
            'booking',
            'driver',
            'start_time',
            'end_time',
            'remarks',
            'member_address',
            'pickup_address',
            'job_address',
            'is_available'
        ]
        read_only_fields = ['id', 'booking', 'driver', 'member_address', 'pickup_address', 'job_address']


# driver/serializers.py

from rest_framework import serializers
from member.models import VehicleBooking
from driver.models import DriverUsageLog
from vendor.models import Vehicle
from users.models import User

class DriverAssignedBookingSerializer(serializers.ModelSerializer):
    vehicle_name = serializers.CharField(source='vehicle.vehicle_name')
    vendor_name = serializers.CharField(source='vehicle.user.full_name', default='', read_only=True)
    vendor_phone = serializers.CharField(source='vehicle.user.phone', default='', read_only=True)
    member_name = serializers.CharField(source='user.full_name', default='', read_only=True)
    member_phone = serializers.CharField(source='user.phone', default='', read_only=True)
    # service_address = models.CharField(source='Vechiclebooking.service_address, default='', read_ony=True)
    start_time = serializers.SerializerMethodField()
    end_time = serializers.SerializerMethodField()

    class Meta:
        model = VehicleBooking
        fields = [
            'booking_id',
            'vehicle_name',
            'vendor_name', 'vendor_phone',
            'member_name', 'member_phone',
            'service_address',
            'start_time', 'end_time',
        ]

    def get_start_time(self, obj):
        log = DriverUsageLog.objects.filter(booking=obj, driver=obj.assigned_driver).first()
        return log.start_time if log else None

    def get_end_time(self, obj):
        log = DriverUsageLog.objects.filter(booking=obj, driver=obj.assigned_driver).first()
        return log.end_time if log else None

class DriverComplaintSerializer(serializers.ModelSerializer):
    class Meta:
        model = DriverComplaint
        fields = ['id', 'driver', 'booking', 'message', 'created_at']
        read_only_fields = ['id', 'driver', 'booking', 'created_at'] 