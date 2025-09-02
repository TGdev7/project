from django.db.models import Q, F
from django.utils import timezone
from typing import Optional, List, Dict
import logging
from member.models import VehicleBooking
from users.models import User
from vendor.models import VehicleType
from driver.models import DriverVehicleType

logger = logging.getLogger(__name__)


class DriverAssignmentService:
    """Service class for assigning drivers to bookings"""

    @staticmethod
    def find_best_driver(booking: VehicleBooking, max_drivers: int = 10) -> Optional[User]:
        """
        Find the best available driver for a booking based on:
        1. Vehicle type compatibility
        2. Location proximity
        3. Driver rating and performance
        4. Availability
        """

        # Get service location
        service_lat, service_lon = booking.service_latitude, booking.service_longitude
        if not service_lat or not service_lon:
            logger.warning(f"No service location found for booking {booking.booking_id}")
            return None

        # Get vehicle type
        vehicle_type = booking.vehicle.vehicle_type if booking.vehicle else None
        if not vehicle_type:
            logger.warning(f"No vehicle type found for booking {booking.booking_id}")
            return None

        # Get available drivers who can drive this vehicle type
        available_drivers = User.objects.filter(
            role='Driver',
            is_active=True,
            is_available=True,
            latitude__isnull=False,
            longitude__isnull=False,
            drivervehicletype__vehicle_type=vehicle_type,
            drivervehicletype__is_approved=True
        ).select_related('district', 'taluka', 'Village').prefetch_related('drivervehicletype_set').distinct()

        if not available_drivers.exists():
            logger.warning(f"No available drivers found for vehicle type {vehicle_type}")
            return None

        # Calculate scores for each driver
        driver_scores = []

        for driver in available_drivers:
            score_data = DriverAssignmentService._calculate_driver_score(
                driver, service_lat, service_lon, vehicle_type
            )
            if score_data['total_score'] > 0:  # Only consider drivers with positive scores
                driver_scores.append(score_data)

        if not driver_scores:
            logger.warning(f"No suitable drivers found for booking {booking.booking_id}")
            return None

        # Sort by total score (highest first)
        driver_scores.sort(key=lambda x: x['total_score'], reverse=True)

        # Return the best driver (limit to max_drivers for performance)
        best_drivers = driver_scores[:max_drivers]

        logger.info(f"Found {len(best_drivers)} suitable drivers for booking {booking.booking_id}")

        return best_drivers[0]['driver']

    @staticmethod
    def _calculate_driver_score(driver: User, service_lat: float, service_lon: float,
                                vehicle_type: VehicleType) -> Dict:
        """Calculate a composite score for driver suitability"""

        # Distance from service location
        distance = driver.get_distance_to_location(service_lat, service_lon)

        # Check max allowed distance
        max_distance_km = driver.max_distance_km or 50  # default fallback
        if distance > max_distance_km:
            return {'driver': driver, 'total_score': 0, 'distance': distance}

        # Distance score: 50 points max, decreases with distance
        distance_score = max(0, 50 - (distance * 2))  # Lose 2 points per km

        # Rating score: 30 points max
        rating = driver.average_rating or 0
        rating_score = (rating / 5.0) * 30

        # Experience score: 20 points max
        try:
            driver_vehicle_type = DriverVehicleType.objects.get(
                driver=driver, vehicle_type=vehicle_type
            )
            experience_score = min(20, driver_vehicle_type.experience_years * 2)
        except DriverVehicleType.DoesNotExist:
            experience_score = 0

        # Availability bonus: based on last location update
        availability_score = 0
        if driver.last_location_update:
            hours_since_update = (timezone.now() - driver.last_location_update).total_seconds() / 3600
            if hours_since_update < 1:
                availability_score = 10
            elif hours_since_update < 6:
                availability_score = 5

        total_score = distance_score + rating_score + experience_score + availability_score

        return {
            'driver': driver,
            'total_score': total_score,
            'distance': distance,
            'distance_score': distance_score,
            'rating_score': rating_score,
            'experience_score': experience_score,
            'availability_score': availability_score
        }

    @staticmethod
    def assign_driver_to_booking(booking: VehicleBooking, max_attempts: int = 3) -> bool:
        """
        Assign a driver to a booking
        """
        if booking.assigned_driver:
            logger.info(f"Booking {booking.booking_id} already has an assigned driver")
            return True

        if booking.assignment_attempts >= max_attempts:
            logger.warning(f"Maximum assignment attempts reached for booking {booking.booking_id}")
            return False

        # Find best driver
        best_driver = DriverAssignmentService.find_best_driver(booking)

        if not best_driver:
            booking.assignment_attempts += 1
            booking.save()
            return False

        # Assign driver
        booking.assigned_driver = best_driver
        booking.status = 'assigned'
        booking.assignment_timestamp = timezone.now()
        booking.assignment_attempts += 1
        booking.save()

        # Mark driver as unavailable
        best_driver.is_available = False
        best_driver.save()

        logger.info(f"Successfully assigned driver {best_driver.full_name} to booking {booking.booking_id}")

        return True

    @staticmethod
    def get_nearby_drivers(latitude: float, longitude: float, vehicle_type: VehicleType,
                           radius_km: float = 50) -> List[Dict]:
        """Get all nearby drivers for a specific location and vehicle type"""

        available_drivers = User.objects.filter(
            role='Driver',
            is_active=True,
            is_available=True,
            latitude__isnull=False,
            longitude__isnull=False,
            drivervehicletype__vehicle_type=vehicle_type,
            drivervehicletype__is_approved=True
        ).distinct()

        nearby_drivers = []

        for driver in available_drivers:
            distance = driver.get_distance_to_location(latitude, longitude)
            if distance <= radius_km:
                nearby_drivers.append({
                    'driver': driver,
                    'distance': distance,
                    'rating': driver.average_rating or 0,
                    'total_orders': driver.total_orders_completed
                })

        # Sort by distance
        nearby_drivers.sort(key=lambda x: x['distance'])

        return nearby_drivers
