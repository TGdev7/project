
from rest_framework import serializers
from users.models import User
from vendor.models import Vendor
from driver.models import Driver


class DistrictReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = User.District
        fields = ['id', 'name']


class TalukaReportSerializer(serializers.ModelSerializer):
    district_name = serializers.CharField(source='district.name', read_only=True)

    class Meta:
        model = User.Taluka
        fields = ['id', 'name', 'district_name']


class VillageReportSerializer(serializers.ModelSerializer):
    district_name = serializers.CharField(source='district.name', read_only=True)
    taluka_name = serializers.CharField(source='taluka.name', read_only=True)

    class Meta:
        model = User.Village
        fields = ['id', 'name', 'taluka_name', 'district_name']


class MemberReportSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    village = serializers.CharField(source='Village.name', read_only=True)
    taluka = serializers.CharField(source='taluka.name', read_only=True)
    district = serializers.CharField(source='district.name', read_only=True)
    join_date = serializers.DateTimeField(source='date_joined', format="%Y-%m-%d")

    class Meta:
        model = User
        fields = [
            'id', 'full_name', 'email', 'mobile', 'address',
            'village', 'taluka', 'district', 'state', 'zipcode', 'country', 'join_date'
        ]

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"


class VendorReportSerializer(serializers.ModelSerializer):
    vendor_name = serializers.SerializerMethodField()
    district = serializers.CharField(source='district.name', read_only=True)
    taluka = serializers.CharField(source='taluka.name', read_only=True)
    village = serializers.CharField(source='village.name', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    contact = serializers.CharField(source='user.mobile', read_only=True)
    state = serializers.CharField(source='user.state', read_only=True)
    zip = serializers.CharField(source='user.zipcode', read_only=True)
    registered_on = serializers.DateTimeField(source='user.date_joined', format="%Y-%m-%d")

    class Meta:
        model = User.Vendor
        fields = [
            'id', 'vendor_name', 'email', 'contact',
            'business_name', 'service_type',
            'district', 'taluka', 'village',
            'state', 'zip', 'registered_on'
        ]

    def get_vendor_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"


class DriverReportSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    mobile = serializers.CharField(source='user.mobile', read_only=True)
    adhar_no = serializers.CharField(source='user.adhar_no', read_only=True)
    pan_no = serializers.CharField(source='user.pan_no', read_only=True)
    dob = serializers.DateField(source='user.dob', read_only=True)
    address = serializers.CharField(source='user.address', read_only=True)
    village = serializers.CharField(source='village.name', read_only=True)
    taluka = serializers.CharField(source='taluka.name', read_only=True)
    district = serializers.CharField(source='district.name', read_only=True)
    state = serializers.CharField(source='user.state', read_only=True)
    zipcode = serializers.CharField(source='user.zipcode', read_only=True)
    country = serializers.CharField(source='user.country', read_only=True)

    class Meta:
        model = User.Driver
        fields = [
            'id', 'first_name', 'last_name', 'email', 'mobile',
            'adhar_no', 'pan_no', 'dob', 'address',
            'village', 'taluka', 'district', 'state', 'zipcode', 'country',
            'license_number', 'license_attachment'
        ]

