from django.db import models
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Q, F
from django.utils import timezone
import math
from users.models import User
from driver.models import *
from member.models import VehicleBooking

class DriverAssignment(models.Model):
    """Track driver assignment history and performance"""
    order = models.ForeignKey(VehicleBooking, on_delete=models.CASCADE, related_name='assignment_history')
    driver = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'Driver'})
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    
    distance_to_pickup_km = models.FloatField()
    assignment_score = models.FloatField()  # Calculated score for assignment decision
    
    assigned_at = models.DateTimeField(auto_now_add=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    rejected_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True, null=True)
    
    # Performance metrics
    pickup_time = models.DateTimeField(null=True, blank=True)
    delivery_time = models.DateTimeField(null=True, blank=True)
    customer_rating = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(5)])
    
    def __str__(self):
        return f"{self.order.order_number} -> {self.driver.full_name}"
