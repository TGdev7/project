from member.models import *
from users.models import User
from rest_framework import serializers
from users.models import DistrictModel
from vendor.serializers import VehicleSerializer
#from admin_panel.serializers import DistrictSerializer
from users.models import DistrictModel,TalukaModel,VillageModel
from vendor.models import Vehicle
from rest_framework import generics, permissions

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class member_registrationSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = ["first_name","last_name","email","mobile",'adhar_no','dob','pan_no','zipcode','email','district','taluka','Village',"password"]
      
class varasadhar_detailSerializer(serializers.ModelSerializer):
    class Meta:
        model = varasadhar_details
        fields = '__all__'

class bank_detailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = bank_details
        fields = '__all__'
        read_only_fields = ['user']

from .serializers import bank_detailsSerializer

class BankDetailListCreateAPIView(generics.ListCreateAPIView):
    queryset = bank_details.objects.all()
    serializer_class = bank_detailsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return bank_details.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)




class farm_detailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = farm_details
        fields = '__all__'
        read_only_fields = ['user']




class UserLoginSerializer(serializers.ModelSerializer):
  class Meta:
    model = User
    fields = ['email', 'password']

####################new_vehicle_booking###################
from admin_panel.serializers import VillageSerializer
from django.shortcuts import get_object_or_404
class VehicleBookingSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    vehicle = VehicleSerializer(read_only=True)
    assigned_driver = UserSerializer(read_only=True)
    service_village = VillageSerializer(read_only=True)
    
    # Write-only fields for creating/updating
    vehicle_id = serializers.IntegerField(write_only=True)
    service_village_id = serializers.IntegerField(write_only=True, required=False)
    
    class Meta:
        model = VehicleBooking
        fields = [
            'booking_id', 'user', 'vehicle', 'vehicle_id',
            'total_area', 'advance_rupees', 'total_charges',
            # 'rating', 
            'remaining_charges', 'assigned_driver',
            'service_village', 'service_village_id',
            'service_latitude', 'service_longitude', 'service_address',
            'booking_date', 'return_date', 'pickup_time', 'return_time',
            'total_days', 'total_amount',
            'status', 'purpose', 'special_requirements',
            'created_at', 'updated_at'
        ]
        #read_only_fields = ['booking_id', 'total_days', 'total_amount', 'created_at', 'updated_at']
        read_only_fields = ['booking_id', 'total_days', 'created_at', 'updated_at']


    def create(self, validated_data):
        request = self.context['request']

        # Assign the user
        validated_data['user'] = request.user

        # Set vehicle
        vehicle_id = validated_data.pop('vehicle_id')
        vehicle = get_object_or_404(Vehicle, id=vehicle_id)
        validated_data['vehicle'] = vehicle

        # Optional: Set service village
        service_village_id = validated_data.pop('service_village_id', None)
        if service_village_id:
            service_village = get_object_or_404(VillageModel, id=service_village_id)
            validated_data['service_village'] = service_village

        # ✅ Actually create and return the instance
        return VehicleBooking.objects.create(**validated_data)


    def get_vehicle_data(self, obj):
        from .serializers import VehicleSerializer  # Avoid circular import
        return VehicleSerializer(obj.vehicle).data if obj.vehicle else None 

        return super().create(validated_data)


# from auto_assign.serializers import DriverSerializer
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
#             'assigned_driver_data', 'status', 'service_address', 'assignment_timestamp',
#             'service_village'
#         ]

#     def create(self, validated_data):
#         vehicle = validated_data.pop('vehicle')
#         booking = VehicleBooking.objects.create(vehicle=vehicle, **validated_data)
#         return booking

   
class MemberUserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "first_name", "last_name", "email", "mobile", 'adhar_no', 'dob', 'role',
            'pan_no', 'zipcode', 'country', 'district', 'taluka', 'Village',
            'address', 'house_or_building', 'road_or_area', 'landmark',
            "state", "city"
        ]

class RatingSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = Rating
        fields = [
            'id', 'user', 'user_id', 'email',
            'booking',  # ✅ include this
            'value', 'created_at', 'addition_feedback'
        ]
        read_only_fields = ['id', 'user', 'user_id', 'email', 'created_at']
        
class instrumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = instrument
        fields = '__all__'

class ComplaintDropDownSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComplaintDropDownModel
        fields = '__all__'



from rest_framework import serializers
from .models import ComplaintModel

from member.models import VehicleBooking

class ComplaintSerializer(serializers.ModelSerializer):
    """
    Serializer for ComplaintModel with user ID, email, and booking details.
    """
    user = serializers.StringRelatedField(read_only=True)
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    booking = serializers.PrimaryKeyRelatedField(
        queryset=VehicleBooking.objects.all(),
        required=False,
        allow_null=True
    )

    class Meta:
        model = ComplaintModel
        fields = ['id', 'reason', 'description', 'user', 'user_id', 'email', 'booking']
        read_only_fields = ['id', 'user', 'user_id', 'email']

    def validate_reason(self, value):
        if value and len(value.strip()) < 3:
            raise serializers.ValidationError("Reason must be at least 3 characters long.")
        return value.strip() if value else value

    def validate_description(self, value):
        if value and len(value.strip()) < 10:
            raise serializers.ValidationError("Description must be at least 10 characters long.")
        return value.strip() if value else value

    def validate(self, data):
        reason = data.get('reason', '').strip() if data.get('reason') else ''
        description = data.get('description', '').strip() if data.get('description') else ''
        if not reason and not description:
            raise serializers.ValidationError("Either reason or description must be provided.")
        return data
