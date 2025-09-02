# from django.db import transaction
# from django.utils import timezone
# from users.models import User, 
# from member.models import VehicleBooking
# from .utils import haversine_distance, get_coordinates_from_village, calculate_assignment_score

# class DriverAssignmentService:
    
#     @staticmethod
#     def get_available_drivers():
#         """Get all available drivers"""
#         return User.objects.filter(
#             role='Driver',
#             driver_profile__status='available'
#         ).select_related('driver_profile')
    
#     @staticmethod
#     def calculate_distances(work_request, drivers):
#         """Calculate distances between work location and driver locations"""
#         distances = []
        
#         # Get work coordinates
#         work_lat, work_lon = work_request.work_latitude, work_request.work_longitude
#         if not work_lat or not work_lon:
#             work_lat, work_lon = get_coordinates_from_village(work_request.work_village)
#             if work_lat and work_lon:
#                 work_request.work_latitude = work_lat
#                 work_request.work_longitude = work_lon
#                 work_request.save()
        
#         if not work_lat or not work_lon:
#             return []
        
#         for driver in drivers:
#             # Get driver coordinates
#             driver_lat, driver_lon = driver.latitude, driver.longitude
#             if not driver_lat or not driver_lon:
#                 driver_lat, driver_lon = get_coordinates_from_village(driver.village)
#                 if driver_lat and driver_lon:
#                     driver.latitude = driver_lat
#                     driver.longitude = driver_lon
#                     driver.save()
            
#             if driver_lat and driver_lon:
#                 distance = haversine_distance(work_lat, work_lon, driver_lat, driver_lon)
                
#                 # Check if driver is willing to travel this distance
#                 if distance <= driver.driver_profile.max_distance_km:
#                     score = calculate_assignment_score(driver.driver_profile, work_request, distance)
#                     distances.append({
#                         'driver': driver,
#                         'distance': distance,
#                         'score': score
#                     })
        
#         # Sort by score (descending) then by distance (ascending)
#         distances.sort(key=lambda x: (-x['score'], x['distance']))
#         return distances
    
#     @staticmethod
#     @transaction.atomic
#     def auto_assign_driver(work_request_id):
#         """Automatically assign the best available driver to a work request"""
#         try:
#             work_request = VehicleBooking.objects.get(id=work_request_id, status='pending')
#         except VehicleBooking.DoesNotExist:
#             return {'success': False, 'message': 'Work request not found or already assigned'}
        
#         # Get available drivers
#         available_drivers = DriverAssignmentService.get_available_drivers()
#         if not available_drivers:
#             return {'success': False, 'message': 'No available drivers found'}
        
#         # Calculate distances and scores
#         driver_distances = DriverAssignmentService.calculate_distances(work_request, available_drivers)
#         if not driver_distances:
#             return {'success': False, 'message': 'No drivers found within acceptable distance'}
        
#         # Get the best driver (highest score, lowest distance)
#         best_match = driver_distances[0]
#         best_driver = best_match['driver']
        
#         # Assign the driver
#         work_request.assigned_driver = best_driver
#         work_request.status = 'assigned'
#         work_request.assigned_at = timezone.now()
#         work_request.save()
        
#         # Update driver status
#         best_driver.driver_profile.status = 'busy'
#         best_driver.driver_profile.save()
        
#         # Create assignment record
#         assignment = assignment.objects.create(
#             work_request=work_request,
#             driver=best_driver,
#             distance_km=best_match['distance'],
#             assignment_score=best_match['score'],
#             auto_assigned=True
#         )
        
#         return {
#             'success': True,
#             'message': 'Driver assigned successfully',
#             'assignment': {
#                 'driver_name': best_driver.username,
#                 'driver_phone': best_driver.phone_number,
#                 'distance_km': best_match['distance'],
#                 'assignment_score': best_match['score']
#             }
#         }
    
#     @staticmethod
#     def get_assignment_suggestions(work_request_id, limit=5):
#         """Get top driver suggestions for a work request"""
#         try:
#             work_request = WorkRequest.objects.get(id=work_request_id)
#         except WorkRequest.DoesNotExist:
#             return []
        
#         available_drivers = DriverAssignmentService.get_available_drivers()
#         driver_distances = DriverAssignmentService.calculate_distances(work_request, available_drivers)
        
#         suggestions = []
#         for match in driver_distances[:limit]:
#             suggestions.append({
#                 'driver_id': match['driver'].id,
#                 'driver_name': match['driver'].username,
#                 'village': match['driver'].village,
#                 'phone': match['driver'].phone_number,
#                 'distance_km': round(match['distance'], 2),
#                 'rating': float(match['driver'].driver_profile.rating),
#                 'total_trips': match['driver'].driver_profile.total_trips,
#                 'assignment_score': match['score']
#             })
        
#         return suggestions
