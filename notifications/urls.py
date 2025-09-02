# notifications/urls.py

from django.urls import path
# Import all relevant views
from .views import (
    DriverAssignmentListView,
    DriverBookingResponseAPIView,
    UserNotificationListView, # Uncommented as it's a valid view
    MarkNotificationAsReadAPIView, # New view for marking as read
    CompleteDriverLogView,
)

urlpatterns = [
    # General user notification list
    path('user/', UserNotificationListView.as_view(), name='user-notification-list'),
    
    # --- NEW: Driver-specific notification URLs ---
    path('driver-assignments/', DriverAssignmentListView.as_view(), name='driver-assignment-list'),
    path('driver-assignments/<int:notification_id>/response/', DriverBookingResponseAPIView.as_view(), name='driver-assignment-response'),
    path("complete-driver-log/<str:booking_id>/", CompleteDriverLogView.as_view(), name="complete-driver-log"),

    # --- END NEW ---

    # URL for marking notifications as read
    path('<int:notification_id>/mark-as-read/', MarkNotificationAsReadAPIView.as_view(), name='mark-notification-read'),
]