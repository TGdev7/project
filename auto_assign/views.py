from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, NotFound
from django.shortcuts import get_object_or_404
from .services import DriverAssignmentService
from users.models import User
from member.models import VehicleBooking
from member.serializers import VehicleBookingSerializer
from .serializers import *
from vendor.models import VehicleType
from django.utils import timezone
from django.db.models import Q


@api_view(['POST'])
def assign_driver_to_booking(request, booking_id):
    from member.serializers import VehicleBookingSerializer
    """
    Manually assign a driver to a specific booking
    POST /api/bookings/{booking_id}/assign-driver/
    """
    booking = get_object_or_404(VehicleBooking, booking_id=booking_id)
    
    # Check if already assigned
    if booking.assigned_driver:
        return Response(
            {'error': 'Driver already assigned to this booking'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Attempt assignment
    success = DriverAssignmentService.assign_driver_to_booking(booking)
    
    if success:
        booking.refresh_from_db()
        serializer = VehicleBookingSerializer(booking)
        return Response({
            'message': 'Driver assigned successfully',
            'booking': serializer.data
        })
    else:
        return Response(
            {'error': 'No suitable drivers found'}, 
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
def get_nearby_drivers(request):
    """
    Get nearby drivers for a specific location and vehicle type
    GET /api/drivers/nearby/?lat=19.2183&lon=72.9781&vehicle_type_id=1&radius=50
    """
    try:
        latitude = float(request.GET.get('lat'))
        longitude = float(request.GET.get('lon'))
        vehicle_type_id = int(request.GET.get('vehicle_type_id'))
        radius = float(request.GET.get('radius', 50))
    except (TypeError, ValueError):
        return Response(
            {'error': 'Invalid parameters. Required: lat, lon, vehicle_type_id'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        vehicle_type = VehicleType.objects.get(id=vehicle_type_id)
    except VehicleType.DoesNotExist:
        return Response(
            {'error': 'Vehicle type not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    nearby_drivers = DriverAssignmentService.get_nearby_drivers(
        latitude, longitude, vehicle_type, radius
    )
    
    # Add distance to each driver's data
    drivers_data = []
    for driver_info in nearby_drivers:
        driver = driver_info['driver']
        serializer = DriverSerializer(driver)
        driver_data = serializer.data
        driver_data['distance'] = round(driver_info['distance'], 2)
        drivers_data.append(driver_data)
    
    return Response({
        'drivers': drivers_data,
        'total_count': len(drivers_data),
        'search_radius_km': radius
    })


@api_view(['POST'])
def update_driver_location(request):
    """
    Update driver's current location
    POST /api/drivers/update-location/
    Body: {"latitude": 19.2183, "longitude": 72.9781}
    """
    if request.user.role != 'Driver':
        return Response(
            {'error': 'Only drivers can update location'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        latitude = float(request.data.get('latitude'))
        longitude = float(request.data.get('longitude'))
    except (TypeError, ValueError):
        return Response(
            {'error': 'Invalid latitude or longitude'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Update driver location
    request.user.latitude = latitude
    request.user.longitude = longitude
    request.user.last_location_update = timezone.now()
    request.user.save()
    
    return Response({'message': 'Location updated successfully'})


@api_view(['POST'])
def toggle_driver_availability(request):
    """
    Toggle driver availability status
    POST /api/drivers/toggle-availability/
    """
    if request.user.role != 'Driver':
        return Response(
            {'error': 'Only drivers can toggle availability'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    request.user.is_available = not request.user.is_available
    request.user.save()
    
    return Response({
        'message': f'Availability set to {"available" if request.user.is_available else "unavailable"}',
        'is_available': request.user.is_available
    })


