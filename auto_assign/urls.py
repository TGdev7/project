from django.urls import path
from . import views


urlpatterns = [
    # Driver assignment endpoints
    path('bookings/<int:booking_id>/assign-driver/', views.assign_driver_to_booking, name='assign-driver'),
    path('drivers/nearby/', views.get_nearby_drivers, name='nearby-drivers'),
    path('drivers/update-location/', views.update_driver_location, name='update-driver-location'),
    path('drivers/toggle-availability/', views.toggle_driver_availability, name='toggle-driver-availability'),
]