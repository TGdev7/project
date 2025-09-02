from django.db import models
from users.models import User, VillageModel
from vendor.models import Vehicle
from django.utils import timezone
from django.core.exceptions import ValidationError

class varasadhar_details(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,blank=True,null=True)
    varasadhar_name = models.CharField(max_length=255,blank=True,null=True)
    address = models.CharField(max_length=255,blank=True,null=True)
    relations = models.CharField(max_length=255,blank=True,null=True)
    gender = models.CharField(max_length=255,blank=True,null=True)

    def __str__(self):
        return f"{self.user}"

class bank_details(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='bank_details', blank=True, null=True)
    bank_name = models.CharField(max_length=200,blank=True,null=True)
    branch_name = models.CharField(max_length=255,blank=True,null=True)
    account_no = models.CharField(max_length=255,blank=True,null=True)
    IFSC_NO =  models.CharField(max_length=20,unique=True,blank=True,null=True)
    def __str__(self):
        return f"Bank details for {self.user}"   


class farm_details(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    pike = models.CharField(max_length=255, blank=True, null=True)
    phalabaga = models.CharField(max_length=255, blank=True, null=True)
    farm_business = models.CharField(max_length=255, blank=True, null=True)
    organic_farming = models.CharField(max_length=255, blank=True, null=True)
    instrument = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - Farm Details"
'''
class VehicleBooking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ]
    booking_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User,on_delete=models.CASCADE, blank=True, null=True, related_name= "user_booking")
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, blank=True, null=True, related_name='Vehicle')
    selected_vehicle = models.ForeignKey(Vehicle,on_delete=models.CASCADE, blank=True, null=True, related_name='info_vehicle')
    register_no = models.CharField(max_length=200,blank=True,null=True)
    date =  models.DateField(null=True,blank=True)
    time = models.TimeField(null=True,blank=True)
    total_area = models.FloatField(max_length=200,blank=True,null=True) 
    advance_rupees = models.CharField(max_length=200,blank=True,null=True)
    total_charges = models.FloatField(default=0.0)
    created_at = models.DateTimeField(default=timezone.now)
    rating = models.IntegerField(default=0)
    remaining_charges = models.IntegerField(blank=True,null=True)
    assigned_driver = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,related_name="driver_booking")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    def __str__(self):
        return f"{self.user}" 
        '''
from vendor.models import Vehicle
class VehicleBooking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Confirmation'),
        ('confirmed', 'Confirmed'), # Status when vendor accepts and assigns driver
        ('accepted', 'Accepted by Vendor (No Driver Yet)'), # Status when vendor accepts without driver
        ('rejected', 'Rejected'), # For driver rejection
        ('declined', 'Declined by Vendor'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ]
    
    booking_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="user_booking")
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, blank=True, null=True, related_name='Vehicle')
   
   
    total_area = models.FloatField(max_length=200, blank=True, null=True) 
    advance_rupees = models.CharField(max_length=200, blank=True, null=True)
    total_charges = models.FloatField(default=0.0)
    
    rating = models.IntegerField(default=0)
    remaining_charges = models.IntegerField(blank=True, null=True)
    assigned_driver = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="driver_booking")
    
    
    # Location fields for pickup/service location
    service_village = models.ForeignKey(VillageModel,on_delete=models.CASCADE, blank=True, null=True)
    service_latitude = models.FloatField(null=True, blank=True)
    service_longitude = models.FloatField(null=True, blank=True)
    service_address = models.TextField(
        verbose_name="Service Working Address",
        help_text="The detailed address where the service is to be performed.",
        blank=True,
        null=True
    )
    
    # Assignment tracking
    # assignment_attempts = models.IntegerField(default=0)
    # assignment_timestamp = models.DateTimeField(null=True, blank=True)
    # Booking Details
    booking_date = models.DateField()
    return_date = models.DateField()
    pickup_time = models.TimeField(null=True, blank=True)
    return_time = models.TimeField(null=True, blank=True)
    


    # Pricing
    total_days = models.IntegerField(null=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Additional Info
    purpose = models.CharField(max_length=200, blank=True)
    special_requirements = models.TextField(blank=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if self.booking_date and self.return_date:
            self.total_days = (self.return_date - self.booking_date).days + 1
            if self.vehicle.price_per_day:
                self.total_amount = self.vehicle.price_per_day * self.total_days
            else:
                self.total_amount = 0.0
        super().save(*args, **kwargs)
    
    
    
    def __str__(self):
        return f"Booking {self.booking_id} - {self.user}"
        
    # def save(self, *args, **kwargs):
    #     if self.service_village:
    #         self.service_latitude = self.service_village.latitude
    #         self.service_longitude = self.service_village.longitude
    #     super().save(*args, **kwargs)
    #     self.vehicle.update_availability()
    
    # def assign_driver(self):
    #     # Use self.service_latitude and self.service_longitude
    #     if self.service_latitude and self.service_longitude:
    #         from auto_assign.services import DriverAssignmentService
    #         assignment_success = DriverAssignmentService.assign_driver_to_booking(self)
    #         return assignment_success
    #     return False

from member.models import VehicleBooking
class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    booking = models.ForeignKey(VehicleBooking, on_delete=models.CASCADE, blank=True, null=True, related_name="booking_ratings")
    value = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    addition_feedback = models.CharField(max_length=100, blank=True, null=True) 

    def __str__(self):
        return f"{self.user} - {self.value}"


class instrument(models.Model):
    instrument = models.CharField(max_length=100,null=True,blank=True)
    def __str__(self):
        return f"{self.instrument}"

class ComplaintDropDownModel(models.Model):
    reasons = models.CharField(max_length=100,null=True,blank=True)
    def __str__(self):
        return f"{self.reasons}"

class ComplaintModel(models.Model):
    reason = models.CharField(max_length=100,null=True,blank=True)
    description =  models.CharField(max_length=100,null=True,blank=True)
    user= models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    booking = models.ForeignKey(VehicleBooking, on_delete=models.SET_NULL, null=True, blank=True)
    is_resolved= models.BooleanField(default=False)
    def __str__(self):
        return f"{self.reason}"
    
