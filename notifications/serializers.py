# notifications/serializers.py

from rest_framework import serializers
from .models import Notification
from member.models import VehicleBooking # Adjust if your Booking model has a different name or app
from users.models import User # Your CustomUser model
from vendor.models import Vehicle # Assuming Vehicle model is in vendor app
from users.models import VillageModel, DistrictModel, TalukaModel # Assuming these are relevant for Vehicle
from vendor.models import VehicleType

# Re-using your SafeUserSerializer
class SafeUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'role'] # Add relevant fields
        read_only_fields = ['id', 'email', 'role']


# Re-using your SafeVehicleSerializer, ensuring it includes upload_image if needed
class SafeVehicleSerializer(serializers.ModelSerializer):
    vendor_info = serializers.SerializerMethodField()
    village_name = serializers.CharField(source='village.name', read_only=True)
    district_name = serializers.CharField(source='district.name', read_only=True)
    taluka_name = serializers.CharField(source='taluka.name', read_only=True)
    vehicle_type_name = serializers.CharField(source='vehicle_type.name', read_only=True)
    upload_image = serializers.URLField(read_only=True) # Ensure this points to the correct field name in your Vehicle model

    class Meta:
        model = Vehicle
        fields = [
            'id', 'vendor_info', 'village_name', 'district_name', 'taluka_name',
            'name', 'vehicle_name', 'vehicle_no', 'status', 'price_per_day',
            'created_at', 'updated_at', 'vehicle_type_name', 'upload_image',  # Added 'model' assuming it exists
        ]

    def get_vendor_info(self, obj):
        vendor = getattr(obj, 'user', None) # Assuming 'user' links to the vendor on the Vehicle model
        if vendor and vendor.role == 'Vendor': # Ensure it's actually a vendor
            return {
                "vendor_id": vendor.id,
                "name": f"{vendor.first_name} {vendor.last_name}".strip(), # Use full name
                "mobile": vendor.mobile,
                "email": vendor.email,
            }
        return None

# Serializer for nesting Booking details within Notifications for drivers
class NotificationBookingSerializer(serializers.ModelSerializer):
    # ⭐ MODIFIED: Use SerializerMethodField for full member name ⭐
    member_name = serializers.SerializerMethodField()
    member_contact = serializers.CharField(source='user.mobile', read_only=True) # Assuming phone_number exists on CustomUser
    
    vehicle = SafeVehicleSerializer(read_only=True) # Nested vehicle details
    service_village_name = serializers.CharField(source='service_village.name', read_only=True) # Name of the service village

    class Meta:
        model = VehicleBooking
        fields = [
            'booking_id',
            'member_name',
            'member_contact',
            'vehicle', # This will use SafeVehicleSerializer
            'service_village_name',
            'service_address', # The new field we added
            'booking_date',
            'pickup_time',
            'return_date',
            'return_time',
            'total_area',
            
            'purpose',
            'special_requirements',
            'status',
            'total_days', # The @property field from the model
        ]
        read_only_fields = fields # All fields are for display, not for creating/updating booking via this serializer

    # ⭐ NEW METHOD for member_name ⭐
    def get_member_name(self, obj):
        if obj.user: # Assuming 'user' is the ForeignKey on VehicleBooking to your User model
            return f"{obj.user.first_name} {obj.user.last_name}".strip()
        return "N/A" # Or handle as appropriate if user might be null


# Final Notification serializer, now including detailed booking info
class NotificationSerializer(serializers.ModelSerializer):
    recipient = SafeUserSerializer(read_only=True)
    sender = SafeUserSerializer(read_only=True)

    booking_details = NotificationBookingSerializer(source='booking', read_only=True)

    class Meta:
        model = Notification
        fields = [
            'id',
            'recipient',
            'sender',
            'message',
            'notification_type',
            'is_read',
            'created_at',
            'booking_details', # This will contain all the booking info
            'driver_response', # For driver's current response status
            'rejection_reason', # For driver's rejection reason
        ]
        # These are all read-only when fetching a notification
        read_only_fields = [
            'id', 'recipient', 'sender', 'message', 'notification_type',
            'is_read', 'created_at', 'booking_details', 'driver_response', 'rejection_reason'
        ]


# ⭐ NEW: Serializer for driver's response to an assignment ⭐
class DriverAssignmentResponseSerializer(serializers.Serializer):
    action = serializers.CharField(write_only=True) # 'accept' or 'reject'
    rejection_reason = serializers.CharField(required=False, allow_blank=True) # Optional for rejection

    def validate(self, data):
        action = data.get('action')
        rejection_reason = data.get('rejection_reason')

        if action not in ['accept', 'reject']:
            raise serializers.ValidationError({"action": "Invalid action. Must be 'accept' or 'reject'."})

        # Make rejection_reason mandatory if action is 'reject' (optional, based on your business logic)
        # if action == 'reject' and not rejection_reason:
        #     raise serializers.ValidationError({"rejection_reason": "Rejection reason is required for 'reject' action."})

        return data