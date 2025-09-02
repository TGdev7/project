from django.db import models
from member.models import VehicleBooking
from vendor.models import Vehicle, VehicleType 

class DriverUsageLog(models.Model):
    from users.models import User
    booking = models.ForeignKey('member.VehicleBooking', on_delete=models.SET_NULL, null=True, blank=True, related_name='driver_logs')
    driver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='usage_logs')
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='usage_logs')
    assigned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_driver_logs')

    member_address = models.TextField( null=True, blank=True)
    service_address = models.TextField(null=True, blank=True)
    pickup_address = models.TextField(null=True, blank=True)
    
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    
    is_active = models.BooleanField(default=True)
    remarks = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.pk and self.start_time:
            self.driver.is_driver_available = False
            self.driver.save()
        elif self.end_time:
            self.driver.is_driver_available = True
            self.driver.save()

        super().save(*args, **kwargs)


    def duration(self):
        if self.end_time:
            return self.end_time - self.start_time
        return None

    def __str__(self):
        return f"{self.driver.get_full_name()} - {self.vehicle.name} [{self.start_time}]"



class DriverVehicleType(models.Model):
    from users.models import User
    """Many-to-many relationship between drivers and vehicle types they can drive"""
    driver = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'Driver'})
    vehicle_type = models.ForeignKey(VehicleType, on_delete=models.CASCADE)
    is_approved = models.BooleanField(default=True, help_text="Admin approval for driving this vehicle type")
    experience_years = models.IntegerField(default=0)
    certification_document = models.FileField(upload_to='driver_certifications/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['driver', 'vehicle_type']

    def __str__(self):
        return f"{self.driver.full_name} - {self.vehicle_type.name}"
      # adjust as per your app structure


class DriverComplaint(models.Model):
    from users.models import User
    driver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='complaints')
    booking = models.ForeignKey(VehicleBooking, on_delete=models.CASCADE, related_name='driver_complaints')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Complaint by {self.driver} on Booking {self.booking.id}"
