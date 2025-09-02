from django.db import models
from django.db.models import Q, F
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import math
import logging

from users.managers import UserManager
from admin_panel.utils import get_coordinates_from_village
from django.core.exceptions import ValidationError
logger = logging.getLogger(__name__)


# ────────────────────────────────────────────────────────────
#  Address hierarchy models
# ────────────────────────────────────────────────────────────
class DistrictModel(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class TalukaModel(models.Model):
    district = models.ForeignKey(DistrictModel, on_delete=models.CASCADE, related_name="distric_taluka")
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class VillageModel(models.Model):
    district = models.ForeignKey(DistrictModel, on_delete=models.CASCADE, related_name="distric_Village")
    taluka   = models.ForeignKey(TalukaModel, on_delete=models.CASCADE, related_name="taluka_Village")
    name     = models.CharField(max_length=100)

    # latitude / longitude + geocoding helpers …
    latitude                   = models.FloatField(null=True, blank=True)
    longitude                  = models.FloatField(null=True, blank=True)
    last_location_update       = models.DateTimeField(null=True, blank=True)
    coordinates_updated_at     = models.DateTimeField(null=True, blank=True)
    geocoding_failed           = models.BooleanField(default=False)
    geocoding_attempts         = models.PositiveIntegerField(default=0)
    manual_coordinates         = models.BooleanField(default=False)

    # -------------- geocoding helpers (unchanged) --------------
    # … keep your full clean(), save(), _perform_geocoding() from original text …
    def clean(self):
        """Custom validation"""
        super().clean()
        
        # Validate coordinate ranges
        if self.latitude is not None:
            if not (-90 <= float(self.latitude) <= 90):
                raise ValidationError({'latitude': 'Latitude must be between -90 and 90'})
        
        if self.longitude is not None:
            if not (-180 <= float(self.longitude) <= 180):
                raise ValidationError({'longitude': 'Longitude must be between -180 and 180'})
    
    def save(self, *args, **kwargs):
        """Override save method to automatically geocode village"""
        # Skip geocoding if coordinates are manually set
        skip_geocoding = kwargs.pop('skip_geocoding', False)
        
        # Check if village or taluka has changed or coordinates are missing
        should_geocode = False
        
        if not skip_geocoding and not self.manual_coordinates:
            should_geocode = True
        
        # Perform geocoding if needed
        if should_geocode and self.name:
            self._perform_geocoding()
        
        # Validate before saving
        self.full_clean()
        super().save(*args, **kwargs)
    
    def _perform_geocoding(self):
        """Internal method to perform geocoding with error handling and retry logic"""
        max_attempts = 3
        
        if self.geocoding_attempts >= max_attempts:
            logger.warning(f"Max geocoding attempts reached for village: {self.name}")
            return
        
        try:
            lat, lon = get_coordinates_from_village(self.name, self.taluka.name, self.district.name)
            
            if lat and lon:
                self.latitude = lat
                self.longitude = lon
                self.geocoding_failed = False
                self.coordinates_updated_at = timezone.now()
                self.geocoding_attempts += 1
                logger.info(f"Successfully geocoded {self.name}")
            else:
                self.geocoding_failed = True
                self.geocoding_attempts += 1
                logger.warning(f"Failed to geocode village: {self.name}")
                
        except Exception as e:
            self.geocoding_failed = True
            self.geocoding_attempts += 1
            logger.error(f"Error during geocoding for village {self.name}: {str(e)}")
    
    def update_coordinates(self, force=False):
        """Method to manually update coordinates"""
        if not self.name:
            return False, "No village specified"
        
        if self.manual_coordinates and not force:
            return False, "Coordinates are manually set. Use force=True to override."
        
        # Reset attempt counter if forcing update
        if force:
            self.geocoding_attempts = 0
        
        old_lat, old_lon = self.latitude, self.longitude
        self._perform_geocoding()
        
        if self.latitude and self.longitude:
            self.save(skip_geocoding=True)  # Avoid recursive geocoding
            return True, f"Coordinates updated from ({old_lat}, {old_lon}) to ({self.latitude}, {self.longitude})"
        
        return False, "Geocoding failed"
    
    def set_manual_coordinates(self, latitude, longitude):
        """Set coordinates manually and prevent auto-geocoding"""
        try:
            self.latitude = float(latitude)
            self.longitude = float(longitude)
            self.manual_coordinates = True
            self.geocoding_failed = False
            self.coordinates_updated_at = timezone.now()
            self.save(skip_geocoding=True)
            return True, "Manual coordinates set successfully"
        except (ValueError, TypeError) as e:
            return False, f"Invalid coordinates: {str(e)}"
    
    def reset_to_auto_geocoding(self):
        """Reset to automatic geocoding and update coordinates"""
        self.manual_coordinates = False
        self.geocoding_attempts = 0
        result, message = self.update_coordinates(force=True)
        return result, message
    
    @property
    def has_coordinates(self):
        """Check if user has valid coordinates"""
        return self.latitude is not None and self.longitude is not None
    
    @property
    def coordinates_tuple(self):
        """Get coordinates as tuple (lat, lon)"""
        if self.has_coordinates:
            return (float(self.latitude), float(self.longitude))
        return None
    
    @property
    def full_address(self):
        """Get full address string"""
        address_parts = [self.name, self.taluka.name, self.district.name]
        return ", ".join([part for part in address_parts if part])
    
    @property
    def geocoding_status(self):
        """Get human-readable geocoding status"""
        if self.manual_coordinates:
            return "Manual coordinates"
        elif self.has_coordinates and not self.geocoding_failed:
            return "Auto-geocoded successfully"
        elif self.geocoding_failed:
            return f"Geocoding failed ({self.geocoding_attempts} attempts)"
        else:
            return "No coordinates"
    
    def __str__(self):
        return f"{self.name}"
    def __str__(self):
        return self.name


# ────────────────────────────────────────────────────────────
#  User model
# ────────────────────────────────────────────────────────────
class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ("Member", "Member"),
        ("Vendor", "Vendor"),
        ("Driver", "Driver"),
        ("Gat_Adhikari", "Gat_Adhikari"),   # Single group admin
    )

    # basic identity
    first_name   = models.CharField(max_length=255, blank=True, null=True)
    last_name    = models.CharField(max_length=255, blank=True, null=True)
    email        = models.EmailField(max_length=255, unique=True, blank=True, null=True)
    mobile       = models.CharField(max_length=20, unique=True, blank=True, null=True)

    # address
    zipcode        = models.CharField(max_length=20, blank=True, null=True)
    city           = models.CharField(max_length=100, blank=True, null=True)
    state          = models.CharField(max_length=100, blank=True, null=True)
    country        = models.CharField(max_length=100, blank=True, null=True)
    address        = models.CharField(max_length=255, blank=True, null=True)
    house_or_building = models.CharField(max_length=275, blank=True, null=True)
    road_or_area      = models.CharField(max_length=275, blank=True, null=True)
    landmark          = models.CharField(max_length=275, blank=True, null=True)

    # role & IDs
    role     = models.CharField(max_length=20, choices=ROLE_CHOICES, blank=True, null=True)
    pan_no   = models.CharField(max_length=20, blank=True, null=True)
    adhar_no = models.CharField(max_length=20, blank=True, null=True)
    dob      = models.DateField(blank=True, null=True)

    # foreign keys
    district = models.ForeignKey(DistrictModel, on_delete=models.SET_NULL, blank=True, null=True)
    taluka   = models.ForeignKey(TalukaModel,   on_delete=models.SET_NULL, blank=True, null=True)
    Village  = models.ForeignKey(VillageModel,  on_delete=models.SET_NULL, blank=True, null=True)

    # driver-specific fields
    license_number    = models.CharField(max_length=50, blank=True, null=True)
    license_attachment = models.ImageField(upload_to="license_attachments/", blank=True, null=True)
    vehicle_number    = models.CharField(max_length=50, blank=True, null=True)
    vehicle_type      = models.CharField(max_length=100, blank=True, null=True)
    

    latitude              = models.FloatField(null=True, blank=True)
    longitude             = models.FloatField(null=True, blank=True)
    last_location_update  = models.DateTimeField(null=True, blank=True)
    total_orders_completed = models.IntegerField(default=0)
    average_rating        = models.FloatField(default=0.0, validators=[MinValueValidator(0.0), MaxValueValidator(5.0)])
    
    max_distance_km       = models.FloatField(default=50.0)

    # status
    is_active      = models.BooleanField(default=True)
    is_staff       = models.BooleanField(default=False)
    is_admin       = models.BooleanField(default=False)
    is_superuser   = models.BooleanField(default=False)
    created_at     = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD  = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    # ---------------- new uniqueness rule ----------------
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["role"],
                condition=Q(role="Gat_Adhikari"),
                name="unique_single_gatadhikari",
            ),
        ]

    # --------------- helper methods … (unchanged) ---------------
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    """ def can_drive_vehicle(self, vehicle_type):
        Check if driver can drive the specified vehicle type
        return DriverVehicleType.objects.filter(
            driver=self, 
            vehicle_type=vehicle_type, 
            is_approved=True
        ).exists()"""

    def get_distance_to_location(self, target_lat, target_lon):
        """Calculate distance to target location using Haversine formula"""
        if not self.latitude or not self.longitude:
            return float('inf')
        
        return self.calculate_distance(
            self.latitude, self.longitude, 
            target_lat, target_lon
        )

    @staticmethod
    def calculate_distance(lat1, lon1, lat2, lon2):
        """Calculate distance between two points using Haversine formula"""
        # Convert latitude and longitude from degrees to radians
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        # Radius of earth in kilometers
        r = 6371
        return c * r
    
    def save(self, *args, **kwargs):
        if self.Village:
            self.latitude = self.Village.latitude
            self.longitude = self.Village.longitude
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.email} - {self.role}"
    def get_unavailable_periods(self):
        """ Return all the unavailable periods for this vehicle. """
        return DriverUnavailablePeriod.objects.filter(driver=self)

    def is_available_for_dates(self, start_date, end_date):
        """
        Check if the vehicle is available for the given date range.
        """
        # Get all unavailable periods for this vehicle
        unavailable_periods = self.get_unavailable_periods()

        # Check for overlap with any existing unavailable period
        for period in unavailable_periods:
            # If the requested date range overlaps with any of the unavailable periods
            if (start_date <= period.end_date and end_date >= period.start_date):
                return False  # Vehicle is not available

        return True  # Driver is available

class DriverUnavailablePeriod(models.Model):
    driver = models.ForeignKey(User, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()

    class Meta:
        indexes = [
            models.Index(fields=['driver', 'start_date']),
            models.Index(fields=['driver', 'end_date']),
        ]

# ────────────────────────────────────────────────────────────
#  Group Model (unchanged)
# ────────────────────────────────────────────────────────────
class GroupModel(models.Model):
    farmer_name = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    Village_name = models.ForeignKey(VillageModel, on_delete=models.CASCADE, blank=True, null=True)
    group_name = models.CharField(max_length=20, blank=True, null=True)
    mobile     = models.CharField(max_length=20, blank=True, null=True)
    email      = models.CharField(max_length=20, blank=True, null=True)
    selection  = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.group_name or "Unnamed Group"





