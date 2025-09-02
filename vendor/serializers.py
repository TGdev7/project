from vendor.models import Vehicle, VehicleType
from rest_framework import serializers
from users.models import User
from users.models import DistrictModel, TalukaModel, VillageModel
from django.contrib.auth.hashers import make_password
from django.db import models
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from member.models import VehicleBooking
from .models import *

class VendorRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "mobile", "password", "role"]
        extra_kwargs = {
            "password": {"write_only": True},
        }

    def create(self, validated_data):
        validated_data["password"] = make_password(validated_data["password"])
        validated_data["role"] = "Vendor"  # force role to Vendor
        return User.objects.create(**validated_data)


# --------- User Serializer ----------
class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "email",
            "mobile",
            "adhar_no",
            "dob",
            "pan_no",
            "zipcode",
            "district",
            "taluka",
            "Village",
            "city",
            "state",
            "password",
        ]

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


# --------- Vendor Registration Serializer ----------
class VendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "email",
            "mobile",
            "adhar_no",
            "dob",
            "pan_no",
            "zipcode",
            "district",
            "taluka",
            "Village",
            "city",
            "state",
            "password",
        ]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.role = "Vendor"  # Ensure the role is set to Vendor
        user.save()
        return user


def validate_vendor(self, value):
    if value.role != "Vendor":
        raise serializers.ValidationError("Selected user is not a Vendor.")
    return value
###########################vehicle serilizers#################
from admin_panel.serializers import DistrictSerializer,TalukaSerializer,VillageSerializer
class VehicleListSerializer(serializers.ModelSerializer):
    
    district = DistrictSerializer(read_only=True)
    taluka = TalukaSerializer(read_only=True)
    village = VillageSerializer(read_only=True)
    
    class Meta:
        model = Vehicle
        fields =  "__all__"

# --------- Vehicle (Tool) Serializer ----------
class VehicleSerializer(serializers.ModelSerializer):
    vendor_info = serializers.SerializerMethodField()
    village_name = serializers.SerializerMethodField()

    class Meta:
        model = Vehicle
        exclude = ["user"]
        read_only_fields = [
            "vendor_info",
            "district_name",
            "taluka_name",
            "village_name",
            "charges",
        ]

    def get_charges(self, obj):
        try:
            return float(obj.charges)
        except (TypeError, ValueError):
            return 0.0  # or None or your default value

    def create(self, validated_data):
        user = self.context["request"].user
        if user.role != "Vendor":
            raise serializers.ValidationError("Only vendors can add vehicles.")
        validated_data["user"] = user
        return super().create(validated_data)

    def get_vendor_info(self, obj):
        if obj.user:
            return {
                "vendor_id": obj.user.id,
                "name": f"{obj.user.first_name} {obj.user.last_name}",
                "mobile": obj.user.mobile,
                "email": obj.user.email,
            }
        return None

    def get_district_name(self, obj):
        return obj.user.district.name if obj.user and obj.user.district else None

    def get_taluka_name(self, obj):
        return obj.user.taluka.name if obj.user and obj.user.taluka else None

    def get_village_name(self, obj):
        return obj.user.Village.name if obj.user and obj.user.Village else None


def __str__(self):
    return f"{self.vehicle_name} - {self.user.get_full_name() if self.user else 'No Vendor'}"


from auto_assign.serializers import DriverSerializer


class VehicleBookingSerializer(serializers.ModelSerializer):
    district_name = serializers.SerializerMethodField()
    taluka_name = serializers.SerializerMethodField()
    village_name = serializers.SerializerMethodField()
    user_data = serializers.SerializerMethodField()
    vehicle_data = serializers.SerializerMethodField()
    assigned_driver_data = DriverSerializer(source="assigned_driver", read_only=True)
    vehicle = serializers.PrimaryKeyRelatedField(queryset=Vehicle.objects.all())
    remaining_charges = serializers.SerializerMethodField()
    charges = serializers.SerializerMethodField()

    def get_charges(self, obj):
        if obj.vehicle:
            try:
                return float(obj.vehicle.charges)
            except (TypeError, ValueError):
                return 0.0
        return 0.0

    def get_remaining_charges(self, obj):
        try:
            advance = float(obj.advance_rupees) if obj.advance_rupees else 0.0
        except (TypeError, ValueError):
            advance = 0.0
        try:
            total = float(obj.total_charges)
        except (TypeError, ValueError):
            total = 0.0
        return total - advance

    def get_user_data(self, obj):
        from .serializers import UserSerializer  # Avoid circular import

        return UserSerializer(obj.user).data if obj.user else None

    def get_vehicle_data(self, obj):
        from .serializers import VehicleSerializer  # Avoid circular import

        return VehicleSerializer(obj.vehicle).data if obj.vehicle else None

    def get_district_name(self, obj):
        if obj.user and obj.user.district:
            return obj.user.district.name
        return None

    def get_taluka_name(self, obj):
        if obj.user and obj.user.taluka:
            return obj.user.taluka.name
        return None

    def get_village_name(self, obj):
        if obj.user and obj.user.Village:
            return obj.user.Village.name
        return None

    class Meta:
        model = VehicleBooking
        fields = [
            "booking_id",
            "vehicle_data",
            "register_no",
            "date",
            "time",
            "total_area",
            "advance_rupees",
            "vehicle",
            "charges",
            "remaining_charges",
            "rating",
            "user_data",
            "district_name",
            "taluka_name",
            "village_name",
            "assigned_driver_data",
            "status",
            "service_latitude",
            "service_longitude",
            "service_address",
            "assignment_timestamp",
        ]

    def create(self, validated_data):
        vehicle = validated_data.pop("vehicle")
        booking = VehicleBooking.objects.create(vehicle=vehicle, **validated_data)
        return booking


#######################vehicle_type create###########################
class VehicleTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleType
        fields = ["id", "name", "description", "requires_special_license", "created_at"]
        read_only_fields = ["id", "created_at"]


# vendor/serializers.py

from rest_framework import serializers
from users.models import User, DistrictModel, TalukaModel, VillageModel 

class VendorUserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "first_name", "last_name", "email", "mobile", "adhar_no", "dob", "role",
            "pan_no", "zipcode", "country", "district", "taluka", "Village",
            "address", "house_or_building", "road_or_area", "landmark",
            "state", "city"
        ]
        read_only_fields = ["email", "role"]


# if it give error of _meta use this 

# class VendorUserProfileSerializer(serializers.Serializer):
   
#     first_name = serializers.CharField(max_length=255, required=False, allow_blank=True)
#     last_name = serializers.CharField(max_length=255, required=False, allow_blank=True)
#     email = serializers.EmailField(max_length=255, read_only=True)
#     mobile = serializers.CharField(max_length=20, required=False, allow_blank=True)

#     adhar_no = serializers.CharField(max_length=20, required=False, allow_blank=True)
#     dob = serializers.DateField(required=False)
#     role = serializers.CharField(max_length=20, read_only=True) 
#     pan_no = serializers.CharField(max_length=20, required=False, allow_blank=True)
#     zipcode = serializers.CharField(max_length=20, required=False, allow_blank=True)
#     country = serializers.CharField(max_length=100, required=False, allow_blank=True)

#     district = serializers.PrimaryKeyRelatedField(
#         queryset=DistrictModel.objects.all(), required=False, allow_null=True
#     )
#     taluka = serializers.PrimaryKeyRelatedField(
#         queryset=TalukaModel.objects.all(), required=False, allow_null=True
#     )
#     village = serializers.PrimaryKeyRelatedField(
#         queryset=VillageModel.objects.all(), required=False, allow_null=True
#     )


#     address = serializers.CharField(max_length=255, required=False, allow_blank=True)
#     house_or_building = serializers.CharField(max_length=275, required=False, allow_blank=True)
#     road_or_area = serializers.CharField(max_length=275, required=False, allow_blank=True)
#     landmark = serializers.CharField(max_length=275, required=False, allow_blank=True)
#     state = serializers.CharField(max_length=100, required=False, allow_blank=True)
#     city = serializers.CharField(max_length=100, required=False, allow_blank=True)

    
#     def update(self, instance, validated_data):
#         # Iterate over all validated data and update the instance
#         for attr, value in validated_data.items():
#             setattr(instance, attr, value)
#         instance.save()
#         return instance

#     # Add a to_representation method for consistency after update
#     # This ensures the GET (read) representation is used for the response
#     def to_representation(self, instance):
#         # Delegate to a ModelSerializer for read-only representation
#         # This leverages the working GET serializer logic
#         return VendorProfileReadSerializer(instance).data
class VendorProfileReadSerializer(serializers.Serializer):
    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "email",
            "mobile",
            "adhar_no",
            "dob",
            "role",
            "pan_no",
            "zipcode",
            "country",
            "district",
            "taluka",
            "Village",
            "address",
            "house_or_building",
            "road_or_area",
            "landmark",
            "state",
            "city",
        ]
        read_only_fields = fields

# class VendorProfileReadSerializer(serializers.Serializer):
#     first_name = serializers.CharField(read_only=True)
#     last_name = serializers.CharField(read_only=True)
#     email = serializers.EmailField(read_only=True)
#     mobile = serializers.CharField(read_only=True)
#     adhar_no = serializers.CharField(read_only=True)
#     dob = serializers.DateField(read_only=True)
#     role = serializers.CharField(read_only=True)
#     pan_no = serializers.CharField(read_only=True)
#     zipcode = serializers.CharField(read_only=True)
#     country = serializers.CharField(read_only=True)
#     # For display, use StringRelatedField
#     district = serializers.StringRelatedField(read_only=True)
#     taluka = serializers.StringRelatedField(read_only=True)
#     Village = serializers.StringRelatedField(read_only=True)
#     address = serializers.CharField(read_only=True)
#     house_or_building = serializers.CharField(read_only=True)
#     road_or_area = serializers.CharField(read_only=True)
#     landmark = serializers.CharField(read_only=True)
#     state = serializers.CharField(read_only=True)
#     city = serializers.CharField(read_only=True)

# ... (rest of your serializers.py file) ...

#####################vehicleunavailable########################
class VehicleUnavailablePeriodSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleUnavailablePeriod
        fields = ['id', 'vehicle', 'start_date', 'end_date']

class DriverSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # Expose only the necessary fields for a driver dropdown
        fields = ['id', 'first_name', 'last_name', 'mobile', 'email'] 