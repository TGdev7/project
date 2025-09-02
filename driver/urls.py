from django.urls import path
from .views import *


urlpatterns = [
    path('login/', UserLoginView.as_view(), name='driver-login'),
    path("profile/", DriverUserProfileView.as_view(), name="profile"),
    path("driver-edit-profile/", DriverEditAPIView.as_view(), name="driveredit"),
    
    # Bookings and Orders
    path('orders/', Orders.as_view(), name='orders'),
    path('driver/bookings/', DriverBookingListView.as_view(), name='driver-bookings'),

    # Assignments
    path('assign/', AssignDriverView.as_view(), name='assign-driver'),

    # Vehicle Types
    path('vehicle-types/', AddDriverVehicleTypeView.as_view(), name='driver-vehicle-type-list-create'),
    path('vehicle-types/<int:pk>/update/', DriverVehicleTypeUpdateView.as_view(), name='driver-vehicle-type-update'),

    # Usage Logs
    path('driver-logs/', DriverUsageLogListView.as_view(), name='driver-usage-log-list'),
    path('driver-logs/create/', DriverUsageLogCreateAPIView.as_view(), name='driver-usage-log-create'),
    path('driver-logs/<int:id>/', DriverUsageLogDetailView.as_view(), name='driver-usage-log-detail'),
    path('logs/<int:pk>/complete/', CompleteUsageLogView.as_view(), name='complete-usage-log'),
    path('AllBookings/', AllBookingsDriverAPIView.as_view(), name='driver-all-bookings'),
    # path("driver-usage-log/<int:pk>/update/", DriverUsageLogUpdateAPIView.as_view(), name="driver-usage-log-update"),
    path("driver-usage-log/", DriverUsageLogFilteredListView.as_view(), name="driver-usage-log-filtered"),  # For frontend GET
    path("driver-usage-log/<int:pk>/", DriverUsageLogUpdateAPIView.as_view(), name="driver-usage-log-update"),  # For frontend PUT
    path("driver-logs/booking-info/<int:booking_id>/", DriverBookingInfoAPIView.as_view(), name="driver-booking-info"),
    path('notifications/respond/<int:notification_id>/', RespondToDriverAssignmentAPIView.as_view(), name='respond-driver-assignment'),
    path('my-assigned-bookings/', DriverAssignedBookingsView.as_view(), name='driver-assigned-bookings'),
    path('start-work/<int:booking_id>/', StartWorkView.as_view()),
    path('end-work/<int:booking_id>/', EndWorkView.as_view()),
    path('complaints/<int:booking_id>/', DriverComplaintCreateView.as_view(), name='driver-complaint-create'),


]