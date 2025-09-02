# notifications/views.py

from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated # Explicitly import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db import transaction

# --- Required Imports ---
from .models import Notification
from .serializers import NotificationSerializer
from users.models import User # Your CustomUser model
from notifications.utils import create_notification # For consistent notification creation
from member.models import VehicleBooking # Import VehicleBooking for type hints or direct use
from driver.models import DriverUsageLog  # ✅ Import added
from django.utils import timezone    
# --- End Required Imports ---


# Recommended: Use generics.ListAPIView for simple listing
class UserNotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # The Notification model has a 'recipient' field for the user who receives it.
        # Ensure 'select_related' is added for efficient fetching of related data
        return Notification.objects.filter(recipient=self.request.user).select_related(
            'sender', # For sender details
            'booking', # For booking details
            'booking__vehicle', # For vehicle details within booking
            'booking__vehicle__user', # For vendor info on vehicle
            'booking__user', # For member info on booking
            'booking__vehicle__vehicle_type', # For vehicle type name
            'booking__service_village' # For service village name
        ).order_by('-created_at')

# REMOVED: NotificationListView - This was a duplicate of UserNotificationListView.
# Using generics.ListAPIView is generally preferred for simple list endpoints.

class DriverAssignmentListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Ensure the user making the request is a driver
        if not hasattr(self.request.user, 'role') or self.request.user.role != 'Driver':
            return Notification.objects.none() # Return empty queryset if not a driver

        return Notification.objects.filter(
            recipient=self.request.user,
            notification_type='booking_assignment', # Only show driver assignments
            driver_response='pending' # Only show pending assignments
        ).select_related(
            'sender',
            'booking',
            'booking__vehicle',
            'booking__vehicle__vehicle_type', # For vehicle_type.name
            'booking__user', # --- IMPORTANT: Changed from 'booking__member' to 'booking__user' ---
            'booking__service_village',
            'booking__vehicle__user' # For vendor info in SafeVehicleSerializer
        ).order_by('-created_at')


class DriverBookingResponseAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, notification_id, *args, **kwargs):
        action = request.data.get('action')  # 'accept' or 'reject'
        rejection_reason = request.data.get('rejection_reason', '')  # Optional for rejection

        # Ensure the user is a driver and is the recipient of the notification
        if not hasattr(request.user, 'role') or request.user.role != 'Driver':
            return Response({'detail': 'Permission denied. Only drivers can respond to assignments.'},
                            status=status.HTTP_403_FORBIDDEN)

        notification = get_object_or_404(
            Notification,
            id=notification_id,
            recipient=request.user,
            notification_type='booking_assignment',
            driver_response='pending'
        )

        with transaction.atomic():
            if action == 'accept':
                notification.driver_response = 'accepted'
                notification.is_read = True
                notification.save()

                booking = notification.booking
                if booking:
                    booking.status = 'confirmed'
                    booking.assigned_driver = request.user
                    booking.save()

                    # ✅ Create Driver Usage Log
                    DriverUsageLog.objects.create(
                        booking=booking,
                        driver=request.user,
                        vehicle=booking.vehicle,
                        assigned_by=notification.sender,
                        
                        service_address=booking.service_address,
                        member_address=getattr(booking.user, 'address', ''),  # Optional fallback
                        start_time=timezone.now()
                    )

                    # ✅ Update Driver Availability
                    request.user.is_driver_available = False
                    request.user.save()

                    # ✅ Notify Member
                    create_notification(
                        recipient=booking.user,
                        sender=request.user,
                        message=f"तुमची बुकिंग ID {booking.booking_id} ({booking.vehicle.vehicle_name} साठी) ड्रायव्हर {request.user.first_name} द्वारे स्वीकारली आहे.",
                        notification_type='booking_status_update',
                        booking=booking,
                        is_read=False
                    )

                    # ✅ Notify Vendor
                    create_notification(
                        recipient=booking.vehicle.user,
                        sender=request.user,
                        message=f"ड्रायव्हर {request.user.first_name} ने बुकिंग ID {booking.booking_id} स्वीकारली आहे.",
                        notification_type='booking_status_update',
                        booking=booking,
                        is_read=False
                    )

                return Response({'status': 'accepted', 'message': 'Booking accepted successfully.'},
                                status=status.HTTP_200_OK)

            elif action == 'reject':
                notification.driver_response = 'rejected'
                notification.is_read = True
                notification.rejection_reason = rejection_reason
                notification.save()

                booking = notification.booking
                if booking:
                    booking.status = 'pending'
                    booking.assigned_driver = None
                    booking.save()

                    # Notify Member
                    create_notification(
                        recipient=booking.user,
                        sender=request.user,
                        message=f"तुमची बुकिंग ID {booking.booking_id} ({booking.vehicle.vehicle_name} साठी) ड्रायव्हरने नाकारली आहे. कारण: {rejection_reason or 'दिले नाही'}. आम्ही पुन्हा असाइनमेंटचा प्रयत्न करू.",
                        notification_type='booking_status_update',
                        booking=booking,
                        is_read=False
                    )

                    # Notify Vendor
                    create_notification(
                        recipient=booking.vehicle.user,
                        sender=request.user,
                        message=f"ड्रायव्हर {request.user.first_name} ने बुकिंग ID {booking.booking_id} नाकारली आहे. कारण: {rejection_reason or 'दिले नाही'}.",
                        notification_type='booking_status_update',
                        booking=booking,
                        is_read=False
                    )

                    # Notify Admin
                    admin_user = User.objects.filter(is_superuser=True).first()
                    if admin_user:
                        create_notification(
                            recipient=admin_user,
                            sender=request.user,
                            message=f"Booking ID {booking.booking_id} was rejected by driver {request.user.email}. Reason: {rejection_reason or 'None'}. Needs re-assignment.",
                            notification_type='booking_status_update',
                            booking=booking,
                            is_read=False
                        )

                return Response({'status': 'rejected', 'message': 'Booking rejected successfully.'},
                                status=status.HTTP_200_OK)

            else:
                return Response({'error': 'Invalid action. Must be \"accept\" or \"reject\".'},
                                status=status.HTTP_400_BAD_REQUEST)


class MarkNotificationAsReadAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, notification_id):
        try:
            notification = Notification.objects.get(id=notification_id, recipient=request.user)
            notification.is_read = True
            notification.save()
            return Response({'detail': 'Notification marked as read.'}, status=status.HTTP_200_OK)
        except Notification.DoesNotExist:
            return Response({'detail': 'Notification not found or you do not have permission to mark it as read.'}, status=status.HTTP_404_NOT_FOUND)
        

        from rest_framework.decorators import api_view
from driver.models import DriverUsageLog

class CompleteDriverLogView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, booking_id):
        try:
            log = DriverUsageLog.objects.get(booking__booking_id=booking_id, driver=request.user)
        except DriverUsageLog.DoesNotExist:
            return Response({'error': 'Log not found for this booking and driver'}, status=404)

        start_time = request.data.get('start_time')
        end_time = request.data.get('end_time')
        remarks = request.data.get('remarks', '')

        if not start_time or not end_time:
            return Response({'error': 'Start time and end time are required'}, status=400)

        log.start_time = start_time  # Or keep existing if already present
        log.end_time = end_time
        log.remarks = remarks
        log.save()

        # Make driver available again
        request.user.is_driver_available = True
        request.user.save()

        return Response({'message': 'Driver log completed successfully'})
