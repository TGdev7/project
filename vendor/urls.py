from django.urls import path
from .views import *
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    # path('register/', VendorRegisterView.as_view(), name='vendor-register'),
    path("login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("dashboard/", VendorDashboardView.as_view(), name="vendor-dashboard"),
    path("vehicle-registraction/", VehicleRegistraction.as_view(),
        name="vehicle-registraction",
    ),
    path(
        "vehicledataedit/<int:id>/", UpdateVehicleData.as_view(), name="vehicle-data-edit"
    ),
    path("vehiclelist/", VehicleList.as_view(), name="vehicle-list"),
    path("vehicledatadelete/<int:id>/",DeleteVehicleView.as_view(),name="vehicle-data-edit",),
    path("vehicleBookingData/", VehicleBookingData.as_view(), name="vehicle-Booking-Data"),
    
    path("profile/", VendorUserProfileView.as_view(), name="profile"),
    path("vendor-edit-profile/", VendorProfileView.as_view(), name="vendor-edit"),
    path('booking-notifications/', VendorBookingNotificationView.as_view(), name='vendor-booking-notifications'),
    path('booking-action/<int:booking_id>/', VendorBookingActionView.as_view(), name='vendor-booking-action'),

    #######vehicle type api###########
    
    path("vehicle-types-add/",VehicleTypeListCreateView.as_view(),name="vehicle-type-list-create"),
    path('vehicle-types/', VehicleTypeListView.as_view(), name='vehicle-type-list-create'),
    
    # List only
    path('vehicle-types/list/', VehicleTypeListView.as_view(), name='vehicle-type-list'),
    
    # Detail operations
    path('vehicle-types/<int:pk>/', VehicleTypeDetailView.as_view(), name='vehicle-type-detail'),
    path('vehicle-types/<int:pk>/update/', VehicleTypeUpdateView.as_view(), name='vehicle-type-update'),
    path('vehicle-types/<int:pk>/delete/', VehicleTypeDeleteView.as_view(), name='vehicle-type-delete'),

    path('all-Bookings/', AllBookingsAPIView.as_view(), name='all-bookings'),
    
]   
