from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from users.models import DistrictModel,TalukaModel, VillageModel

class VehicleType(models.Model):
    """Vehicle types that can be driven"""
    name = models.CharField(max_length=100, unique=True)  # e.g., 'Tractor', 'Truck', 'Harvester'
    description = models.TextField(blank=True)
    requires_special_license = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Vehicle(models.Model):
    VEHICLE_STATUS_CHOICES = [
        ('available', 'Available'),
        ('booked', 'Booked'),
        ('maintenance', 'Under Maintenance'),
        ('inactive', 'Inactive'),]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
   
    name = models.CharField(max_length=100)
    vehicle_name = models.CharField(max_length=255, blank=True, null=True)
    power = models.CharField(max_length=255, blank=True, null=True)
    no_compression = models.CharField(max_length=255, blank=True, null=True)
    compressor_type = models.CharField(max_length=255, blank=True, null=True)
    lubrication_type = models.CharField(max_length=255, blank=True, null=True)
    vehicle_no = models.CharField(max_length=255, blank=True, null=True)
    rental_available = models.BooleanField(default=True)
    condition = models.CharField(max_length=255, blank=True, null=True)
    insurance_no = models.CharField(max_length=255, blank=True, null=True)
    buy_rate = models.CharField(max_length=255, blank=True, null=True)
    charges = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    upload_image = models.ImageField(upload_to='images/', default='images/default.jpg')
    description = models.TextField(blank=True, null=True)
    cooling_method = models.CharField(max_length=255, blank=True, null=True)
    vehicle_type = models.ForeignKey(VehicleType, on_delete=models.CASCADE)
    
    #LOCATION
    district = models.ForeignKey(DistrictModel, on_delete=models.CASCADE)
    taluka = models.ForeignKey(TalukaModel, on_delete=models.CASCADE)
    village = models.ForeignKey(VillageModel, on_delete=models.CASCADE)
    
    # Status and Availability
    status = models.CharField(max_length=20, choices=VEHICLE_STATUS_CHOICES, default='available')
  

    # Rental Details
    price_per_day = models.DecimalField(max_digits=10, decimal_places=2)
    price_per_hour = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)

    #Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def get_unavailable_periods(self):
        """ Return all the unavailable periods for this vehicle. """
        return VehicleUnavailablePeriod.objects.filter(vehicle=self)

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

        return True  # Vehicle is available
    
    def __str__(self):
        owner = self.user.get_full_name() if self.user else "No User"
        return f"{self.vehicle_name or self.name} - {owner}"


class VehicleUnavailablePeriod(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()

    class Meta:
        indexes = [
            models.Index(fields=['vehicle', 'start_date']),
            models.Index(fields=['vehicle', 'end_date']),
        ]
    
    def __str__(self):
        return f"{self.vehicle.name} Unavailable from {self.start_date} to {self.end_date}"
