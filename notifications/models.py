# notifications/models.py

from django.db import models
from django.contrib.auth import get_user_model
from member.models import VehicleBooking # Import your Booking model (assuming it's named Booking in member app)
from member.models import ComplaintModel
User = get_user_model() # Use get_user_model() for user model consistency

class Notification(models.Model):
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='sent_notifications')
    related_complaint = models.ForeignKey(
    ComplaintModel, on_delete=models.SET_NULL, null=True, blank=True
    )
    # Link to the specific booking if this notification is booking-related
    booking = models.ForeignKey(VehicleBooking, on_delete=models.SET_NULL, null=True, blank=True, related_name='notifications_for_booking')

    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Type of notification (e.g., 'general', 'booking_assignment', 'booking_update')
    notification_type = models.CharField(
        max_length=50,
        choices=[
            ('general', 'General'),
            ('booking_assignment', 'Booking Assignment'), # New type for driver assignments
            ('booking_status_update', 'Booking Status Update'), # For members/vendors
            ('payment_due', 'Payment Due'),
            # Add other types as needed
        ],
        default='general'
    )

    # For driver assignment notifications: their response
    driver_response = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('accepted', 'Accepted'),
            ('rejected', 'Rejected'),
        ],
        default='pending'
    )
    # Optional field for driver's reason for rejection
    rejection_reason = models.TextField(blank=True, null=True)


    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        if self.booking:
            return f'Notification ({self.notification_type}) for {self.recipient.email} - Booking {self.booking.id}'
        return f'Notification ({self.notification_type}) for {self.recipient.email} - {self.message[:30]}'


