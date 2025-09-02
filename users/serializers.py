from rest_framework import serializers
from users.models import User
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import AuthenticationFailed
from users.models import DistrictModel,TalukaModel,VillageModel,GroupModel
import re

class MemberUserRegisterSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)
    message = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = [
            "first_name", "last_name", "email", "mobile", 'adhar_no', 'dob',
            'pan_no', 'zipcode', 'country', 'district', 'taluka', 'Village',
            'address', 'house_or_building', 'road_or_area', 'landmark',
            "password", "confirm_password", "message","state", "city"
        ]
        extra_kwargs = {
            "password": {"write_only": True}
        }

    def get_message(self, obj):
        return "Thank you for registering, please verify your email before continuing"
    
    # def validate_mobile(self, value):
    #     if not re.fullmatch(r"\d{10}", value):
    #         raise serializers.ValidationError("Mobile number must be exactly 10 digits.")
    #     return value
    
    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("User with this email already exists")
        return value

    def validate(self, data):
        # Confirm both passwords match
        if data.get('password') and data.get('confirm_password'):
            if data['password'] != data['confirm_password']:
                raise serializers.ValidationError("Passwords do not match.")

        
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')  # Remove confirm_password before passing
        user_obj = User.objects.create_new_user(**validated_data, role="Member", is_active=True)
        
        return user_obj

class VendorUserRegisterSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)
    message = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = [
            "first_name", "last_name", "email", "mobile", 'adhar_no', 'dob',
            'pan_no', 'zipcode', 'country', 'district', 'taluka', 'Village',
            'address', 'house_or_building', 'road_or_area', 'landmark',
            "password", "confirm_password", "message", "state", "city"
        ]
        extra_kwargs = {
            "password": {"write_only": True}
        }

    def get_message(self, obj):
        return "Thank you for registering, please verify your email before continuing"
    
    # def validate_mobile(self, value):
    #     if not re.fullmatch(r"\d{10}", value):
    #         raise serializers.ValidationError("Mobile number must be exactly 10 digits.")
    #     return value

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("User with this email already exists")
        return value

    def validate(self, data):
        if data.get('password') and data.get('confirm_password'):
            if data['password'] != data['confirm_password']:
                raise serializers.ValidationError("Passwords do not match.")
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')  # Remove confirm_password before passing
        user_obj = User.objects.create_new_user(**validated_data, role="Vendor", is_active=True)
        return user_obj


class DriverUserRegisterSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)
    message = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = [
            "first_name", "last_name", "email", "mobile", 'adhar_no', 'dob',
            'pan_no', 'zipcode', 'country', 'district', 'taluka', 'Village',
            'address', 'house_or_building', 'road_or_area', 'landmark',
            'license_number', 'license_attachment', "password", "confirm_password", "message","state", "city"
        ]
        extra_kwargs = {
            "password": {"write_only": True}
        }

    def get_message(self, obj):
        return "Thank you for registering, please verify your email before continuing"
    
    # def validate_mobile(self, value):
    #     if not re.fullmatch(r"\d{10}", value):
    #         raise serializers.ValidationError("Mobile number must be exactly 10 digits.")
    #     return value

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("User with this email already exists")
        return value

    def validate(self, data):
        if data.get('password') and data.get('confirm_password'):
            if data['password'] != data['confirm_password']:
                raise serializers.ValidationError("Passwords do not match.")
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        user_obj = User.objects.create_new_user(**validated_data, role="Driver", is_active=True)
        return user_obj

    
class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    role = serializers.ChoiceField(choices=User.ROLE_CHOICES)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        role = data.get('role')

        try:
            user = User.objects.get(email=email, role=role)
        except User.DoesNotExist:
            raise AuthenticationFailed("Invalid email or role")

        if not user.check_password(password):
            raise AuthenticationFailed("Invalid password")
        if not user.is_active:
            raise AuthenticationFailed("User account is disabled")

        token, created = Token.objects.get_or_create(user=user)
        return {
            "token": token.key,
            "user_id": user.id,
            "email": user.email,
            "role": user.role,
        }
    
class DriverPublicSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id", "first_name", "last_name", "email", "mobile",
            "license_number", "full_name"
        ]

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    
class DriverUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'email',
            'mobile',
            'district',
            'taluka',
            'Village',
            'license_number',
            'vehicle_type',
            'is_driver_available',
        ]
        read_only_fields = ['email']  # or any others you don't want updated


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
        fields = "__all__"



#################EXTRA FIELD###############################
class UserLocationSerializer(serializers.ModelSerializer):
    """Serializer for user location data"""
    has_coordinates = serializers.ReadOnlyField()
    full_address = serializers.ReadOnlyField()
    geocoding_status = serializers.ReadOnlyField()
    coordinates_tuple = serializers.ReadOnlyField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'village', 'taluka', 'district', 'state',
            'latitude', 'longitude', 'coordinates_updated_at',
            'geocoding_failed', 'manual_coordinates',
            'full_address', 'has_coordinates', 'geocoding_status',
            'coordinates_tuple'
        ]
        read_only_fields = [
            'latitude', 'longitude', 'coordinates_updated_at',
            'geocoding_failed', 'geocoding_attempts'
        ]
    
    def update(self, instance, validated_data):
        """Override update to handle coordinate updates"""
        # Check if location fields are being updated
        location_fields = ['village', 'taluka', 'district', 'state']
        location_changed = any(
            field in validated_data and 
            validated_data[field] != getattr(instance, field)
            for field in location_fields
        )
        
        # Update instance
        instance = super().update(instance, validated_data)
        
        # Trigger coordinate update if location changed
        if location_changed and not instance.manual_coordinates:
            instance.update_coordinates()
        
        return instance