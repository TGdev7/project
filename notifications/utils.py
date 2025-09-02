# notifications/utils.py

from django.db import transaction
from .models import Notification
from django.contrib.auth import get_user_model

User = get_user_model() # Ensure you get your custom User model, if applicable

# Removed the first, simpler create_notification function
# Only keep this comprehensive one:

def create_notification(
    recipient,
    message,
    sender=None,
    notification_type='general',
    booking=None,
    is_read=False,
    driver_response='pending', # Default for assignment notifications
    rejection_reason=None, # Only for driver rejections
    **kwargs # To catch any extra keyword arguments for future flexibility
):
    """
    Creates a new Notification instance.

    Args:
        recipient (User): The user who will receive this notification.
        message (str): The main text content of the notification.
        sender (User, optional): The user who initiated the notification. Defaults to None.
        notification_type (str, optional): The type of notification (e.g., 'general', 'booking_assignment').
                                            Defaults to 'general'.
        booking (VehicleBooking, optional): The related VehicleBooking object, if any. Defaults to None.
        is_read (bool, optional): Whether the notification has been read. Defaults to False.
        driver_response (str, optional): The driver's response status for 'booking_assignment' types.
                                         Defaults to 'pending'.
        rejection_reason (str, optional): Reason for rejection, if applicable. Defaults to None.
    """
    # Basic type checking for critical User fields (optional, but good for debugging)
    if not isinstance(recipient, User):
        raise TypeError(f"Recipient must be a User instance, but got {type(recipient)}")
    if sender is not None and not isinstance(sender, User):
        raise TypeError(f"Sender must be a User instance or None, but got {type(sender)}")

    with transaction.atomic():
        Notification.objects.create(
            recipient=recipient,
            message=message,
            sender=sender,
            notification_type=notification_type,
            booking=booking,
            is_read=is_read,
            driver_response=driver_response,
            rejection_reason=rejection_reason,
            **kwargs # Pass any other kwargs directly to the create method
        )
    print(f"DEBUG: Notification created for {recipient.email} (Type: {notification_type})")