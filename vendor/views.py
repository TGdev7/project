from django.shortcuts import render
from vendor.serializers import *
from rest_framework import generics, mixins, status, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from django.db.models import Q

from member.models import VehicleBooking
from member.serializers import VehicleBookingSerializer
from vendor.models import Vehicle
from vendor.serializers import VehicleSerializer, VendorUserProfileSerializer
from users.models import User, DriverUnavailablePeriod

from rest_framework.decorators import api_view
from rest_framework.exceptions import ValidationError, NotFound
from django.shortcuts import get_object_or_404
from auto_assign.services import DriverAssignmentService

from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import AllowAny
from django.db import transaction 
from notifications.utils import create_notification 
from notifications.models import Notification

# -------- Vehicle ViewSet (for Vendors) --------
class VehicleViewSet(viewsets.ModelViewSet):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        # Ensure the user is a vendor
        if self.request.user.role != "Vendor":
            raise PermissionDenied("Only vendors can add vehicles.")
        serializer.save(user=self.request.user)

    def get_queryset(self):
        # Vendors can see only their own vehicles
        user = self.request.user
        if user.role == "Vendor":
            return Vehicle.objects.filter(user=user)
        return Vehicle.objects.none()


# -------- Vendor Edit Profile --------
class VendorProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        # Use the dedicated read serializer for GET requests
        serializer = VendorProfileReadSerializer(user)
        return Response(serializer.data)

    def put(self, request):
        user = request.user
        # Use the main VendorUserProfileSerializer for PUT (it now has update method)
        serializer = VendorUserProfileSerializer(user, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save() # This will call the update() method we just defined
            # Return data using the read serializer for consistent output
            return Response(VendorProfileReadSerializer(user).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




# -------- Vendor Booking Data --------
class VehicleBookingData(generics.ListAPIView):
    serializer_class = VehicleBookingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user_instance = self.request.user
        user_vehicles = user_instance.vehicle_set.all()
        return VehicleBooking.objects.filter(vehicle__in=user_vehicles)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)


####################### Admin Panel ######################


# -------- Update Vendor --------
class UpdateVendorView(generics.UpdateAPIView, mixins.RetrieveModelMixin):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = "id"
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"success": True, "message": "Vendor data updated successfully"},
            status=status.HTTP_200_OK,
        )


# -------- Delete Vendor --------
class DeleteVendorView(
    mixins.RetrieveModelMixin, mixins.DestroyModelMixin, generics.GenericAPIView
):
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = "id"

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {"success": True, "message": "Record deleted successfully."},
            status=status.HTTP_200_OK,
        )


# -------- Update Vehicle --------
class UpdateVehicleData(generics.UpdateAPIView, mixins.RetrieveModelMixin):
    permission_classes = [IsAuthenticated]
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    lookup_field = "id"

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"success": True, "message": "Vehicle data updated successfully"},
            status=status.HTTP_200_OK,
        )


# -------- Delete Vehicle --------
class DeleteVehicleView(
    mixins.RetrieveModelMixin, mixins.DestroyModelMixin, generics.GenericAPIView
):
    permission_classes = [IsAuthenticated]
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    lookup_field = "id"

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {"success": True, "message": "Record deleted successfully."},
            status=status.HTTP_200_OK,
        )


# -------- Vehicle List --------
class VehicleList(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    def get_queryset(self):
        return Vehicle.objects.filter(user=self.request.user)


# -------- Vendor Dropdown for Admin #####################################################################################
class VendorListDropDown(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = User.objects.filter(Q(role="Vendor") | Q(role="vendor"))
    serializer_class = UserSerializer


# -------- Vendor Dashboard -###########################################################################################
class VendorDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_vehicles = Vehicle.objects.filter(user=request.user)
        total_vehicles = user_vehicles.count()
        total_bookings = VehicleBooking.objects.filter(
            vehicle__in=user_vehicles
        ).count()

        return Response(
            {
                "total_vehicles": total_vehicles,
                "total_bookings": total_bookings,
            }
        )


#############################Vendor Tool Registration #################################################################
class VehicleRegistraction(generics.CreateAPIView):
    serializer_class = VehicleSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        return {"request": self.request}

    def perform_create(self, serializer):
        if self.request.user.role != "Vendor":
            raise PermissionDenied("Only vendors can register vehicles.")
        serializer.save(user=self.request.user)



# views.py
from rest_framework import generics, status
from rest_framework.response import Response
from .models import VehicleType
from .serializers import VehicleTypeSerializer

from admin_panel.permissions import IsAdminUser


class VehicleTypeListCreateView(generics.ListCreateAPIView):
    """
    API view to list all vehicle types and create new ones.

    GET: Returns list of all vehicle types
    POST: Creates a new vehicle type
    """

    queryset = VehicleType.objects.all()
    serializer_class = VehicleTypeSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        """
        Optionally filter vehicle types by name or special license requirement
        """
        queryset = VehicleType.objects.all()
        name = self.request.query_params.get("name", None)
        requires_license = self.request.query_params.get(
            "requires_special_license", None
        )

        if name is not None:
            queryset = queryset.filter(name__icontains=name)
        if requires_license is not None:
            queryset = queryset.filter(
                requires_special_license=requires_license.lower() == "true"
            )

        return queryset.order_by("name")

    def create(self, request, *args, **kwargs):
        """
        Create a new vehicle type with custom response
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response(
                {
                    "message": "Vehicle type created successfully",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {"message": "Failed to create vehicle type", "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )


class VendorUserProfileView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        print(f"DEBUG: request.user: {request.user}")
        print(f"DEBUG: request.user.is_authenticated: {request.user.is_authenticated}")
        # Add a check here to prevent passing None to the serializer if the permission class somehow fails or is overridden
        if not request.user or not request.user.is_authenticated:
            # This case *should* be handled by IsAuthenticated permission,
            # but as a safeguard, or if AnonymousUser is somehow reaching here.
            return Response({"detail": "Authentication credentials were not provided or are invalid."}, status=status.HTTP_401_UNAUTHORIZED)
            
        serializer = VendorUserProfileSerializer(request.user)
        return Response(serializer.data)

#in test
class VendorBookingNotificationView(APIView):
    permission_classes = [IsAuthenticated]

    # Removed the duplicate get method. Combined logic and debug prints here if desired.
    def get(self, request):
        print(f"DEBUG: VendorBookingNotificationView request.user: {request.user}")
        print(f"DEBUG: VendorBookingNotificationView request.user.is_authenticated: {request.user.is_authenticated}")

        vendor = request.user
        # Added a more robust role check
        if not hasattr(vendor, 'role') or vendor.role != 'Vendor':
            return Response({"detail": "Access denied. User is not a Vendor."}, status=status.HTTP_403_FORBIDDEN)

        bookings = VehicleBooking.objects.filter(
            vehicle__user=vendor, # Assuming 'vehicle__user' links to the vendor
            status="pending"
        ).order_by("-booking_date", "-pickup_time")

        serializer = VehicleBookingSerializer(bookings, many=True)
        return Response(serializer.data)


class VendorBookingActionView(generics.GenericAPIView):
    # Expanded select_related for efficiency when building driver notification message
    queryset = VehicleBooking.objects.select_related(
        'vehicle',
        'user', # For the booking member's info (assuming booking.user is the customer)
        'vehicle__vehicle_type', # For vehicle_type.name
        'vehicle__user', # For vendor info on vehicle, if needed
        'service_village' # For service_village.name
    )
    serializer_class = VehicleBookingSerializer # Used for response, not for incoming data parsing here
    permission_classes = [IsAuthenticated] # Add permissions here

    def post(self, request, booking_id, *args, **kwargs):
        vendor = request.user
        action = request.data.get("action")
        driver_id = request.data.get("driver_id") # This comes from the frontend

        # Role check for the vendor
        if not hasattr(vendor, 'role') or vendor.role != 'Vendor':
            return Response({"detail": "Access denied. Only Vendors can perform this action."}, status=status.HTTP_403_FORBIDDEN)

        # Use booking_id as the primary key lookup
        booking = get_object_or_404(
            self.get_queryset(),
            booking_id=booking_id, # Use 'booking_id' for PK lookup
            vehicle__user=vendor # Ensure the vendor owns the vehicle related to this booking
        )

        if booking.status != "pending":
            return Response({"detail": "Booking already processed."}, status=status.HTTP_400_BAD_REQUEST)

        # Use atomic transaction to ensure all operations succeed or fail together
        with transaction.atomic():
            # Define recipient and sender for customer notifications
            customer_recipient = booking.user # Assuming booking.user is the User instance of the customer
            vendor_sender = request.user      # The vendor User instance (who is performing the action)

            if action == "accepted" and driver_id:
                driver = get_object_or_404(User, pk=driver_id, role='Driver') # Ensure 'Driver' role matches your User model

                booking.assigned_driver = driver
                booking.status = "confirmed" # Or 'assigned' if you have a specific status for this
                booking.save() # First save the booking with assigned driver and status

                # Create DriverUnavailablePeriod (your existing logic)
                DriverUnavailablePeriod.objects.create(
                    driver=driver,
                    start_date=booking.booking_date,
                    end_date=booking.return_date
                )

                # Create VehicleUnavailablePeriod (your existing logic)
                VehicleUnavailablePeriod.objects.create(
                    vehicle=booking.vehicle,
                    start_date=booking.booking_date,
                    end_date=booking.return_date
                )

                # ⭐ Corrected: Create notification for member (customer) ⭐
                customer_message_accepted = f"बुकिंग स्वीकारली: आपली बुकिंग (ID: {booking.booking_id}) विक्रेत्याने स्वीकारली आहे."
                create_notification(
                    recipient=customer_recipient,
                    message=customer_message_accepted, # Pass the combined message string
                    sender=vendor_sender, # Pass the User instance (the vendor)
                    notification_type='booking_accepted_customer', # More specific type
                    booking=booking,
                )

                # --- NEW: Create Notification for DRIVER (CORE FEATURE) ---
                # This part was already well-structured using keyword arguments
                message_for_driver = (
                    f"नवीन असाइनमेंट: बुकिंग ID {booking.booking_id}\n"
                    f"वाहन: {booking.vehicle.vehicle_name} \n"
                    # f"वाहनाचा प्रकार: {booking.vehicle.vehicle_type.name if booking.vehicle.vehicle_type else 'उपलब्ध नाही'}\n"
                    f"कामाचे ठिकाण: {booking.service_address if booking.service_address else 'N/A'}\n"
                    f"बुकिंगची तारीख: {booking.booking_date} वेळ: {booking.pickup_time if booking.pickup_time else 'N/A'}\n"
                    f"परतीची तारीख: {booking.return_date} वेळ: {booking.return_time if booking.return_time else 'N/A'}\n"
                    f"अंदाजे एकूण दिवस: {booking.total_days if booking.total_days else 'N/A'}"
                )

                create_notification(
                    recipient=driver,
                    sender=vendor_sender, # The vendor who assigned the driver
                    booking=booking, # Link to the booking object
                    message=message_for_driver,
                    notification_type='booking_assignment', # Specific type for driver assignments
                    driver_response='pending' # Set initial response status
                )
                print(f"DEBUG: Driver notification created for {driver.email} for Booking {booking.booking_id}")
                # --- END NEW ---

            elif action == "accepted":
                # This block handles accepting without assigning a driver immediately.
                booking.status = "accepted"
                booking.save()
                
                # Check if vehicle exists before creating period
                if booking.vehicle:
                    VehicleUnavailablePeriod.objects.create(
                        vehicle=booking.vehicle,
                        start_date=booking.booking_date,
                        end_date=booking.return_date
                    )
                # ⭐ Corrected: Create notification for member (customer) ⭐
                customer_message_accepted_no_driver = f"बुकिंग स्वीकारली: आपली बुकिंग (ID: {booking.booking_id}) विक्रेत्याने स्वीकारली आहे."
                create_notification(
                    recipient=customer_recipient,
                    message=customer_message_accepted_no_driver,
                    sender=vendor_sender, # Pass the User instance (the vendor)
                    notification_type='booking_accepted_customer',
                    booking=booking,
                )

            elif action == "declined":
                # Logic for declining a booking
                booking.status = "declined"
                booking.save()
                # ⭐ Corrected: Create notification for member (customer) ⭐
                customer_message_declined = f"बुकिंग नाकारली: आपली बुकिंग (ID: {booking.booking_id}) विक्रेत्याने नाकारली आहे."
                create_notification(
                    recipient=customer_recipient,
                    message=customer_message_declined,
                    sender=vendor_sender, # Pass the User instance (the vendor)
                    notification_type='booking_declined_customer', # More specific type
                    booking=booking,
                )

            else:
                return Response({"detail": "Invalid action or missing driver_id for 'accepted' action."}, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "detail": f"Booking {action} successfully.",
            "booking_id": booking.booking_id,
            "new_status": booking.status
        }, status=status.HTTP_200_OK)

        


##################### Vehicle type crete for admin ########################################################
from rest_framework import generics, status
from rest_framework.response import Response
from .models import VehicleType
from .serializers import VehicleTypeSerializer

from admin_panel.permissions import IsAdminUser
class VehicleTypeListCreateView(generics.ListCreateAPIView):
    """
    API view to list all vehicle types and create new ones.

    GET: Returns list of all vehicle types
    POST: Creates a new vehicle type
    """

    queryset = VehicleType.objects.all()
    serializer_class = VehicleTypeSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        """
        Optionally filter vehicle types by name or special license requirement
        """
        queryset = VehicleType.objects.all()
        name = self.request.query_params.get("name", None)
        requires_license = self.request.query_params.get(
            "requires_special_license", None
        )

        if name is not None:
            queryset = queryset.filter(name__icontains=name)
        if requires_license is not None:
            queryset = queryset.filter(
                requires_special_license=requires_license.lower() == "true"
            )

        return queryset.order_by("name")

    def create(self, request, *args, **kwargs):
        """
        Create a new vehicle type with custom response
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response(
                {
                    "message": "Vehicle type created successfully",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {"message": "Failed to create vehicle type", "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )
class VehicleTypeListView(generics.ListAPIView):
    """
    API view to list all vehicle types with filtering options.
    
    GET: Returns list of all vehicle types with optional filtering
    """
    
    queryset = VehicleType.objects.all()
    serializer_class = VehicleTypeSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        """
        Optionally filter vehicle types by name or special license requirement
        """
        queryset = VehicleType.objects.all()
        name = self.request.query_params.get("name", None)
        requires_license = self.request.query_params.get(
            "requires_special_license", None
        )
        
        if name is not None:
            queryset = queryset.filter(name__icontains=name)
        if requires_license is not None:
            queryset = queryset.filter(
                requires_special_license=requires_license.lower() == "true"
            )
        
        return queryset.order_by("name")
    
    def list(self, request, *args, **kwargs):
        """
        List vehicle types with custom response format
        """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        
        return Response(
            {
                "message": "Vehicle types retrieved successfully",
                "count": queryset.count(),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class VehicleTypeUpdateView(generics.RetrieveUpdateAPIView):
    """
    API view to retrieve and update a specific vehicle type.
    
    GET: Returns details of a specific vehicle type
    PUT/PATCH: Updates a specific vehicle type
    """
    
    queryset = VehicleType.objects.all()
    serializer_class = VehicleTypeSerializer
    permission_classes = [IsAdminUser]
    lookup_field = 'pk'
    
    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a specific vehicle type with custom response
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        
        return Response(
            {
                "message": "Vehicle type retrieved successfully",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )
    
    def update(self, request, *args, **kwargs):
        """
        Update a vehicle type with custom response
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        
        if serializer.is_valid():
            self.perform_update(serializer)
            return Response(
                {
                    "message": "Vehicle type updated successfully",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        
        return Response(
            {
                "message": "Failed to update vehicle type",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
    
    def partial_update(self, request, *args, **kwargs):
        """
        Partially update a vehicle type with custom response
        """
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)


class VehicleTypeDetailView(generics.RetrieveAPIView):
    """
    API view to retrieve details of a specific vehicle type.
    
    GET: Returns details of a specific vehicle type
    """
    
    queryset = VehicleType.objects.all()
    serializer_class = VehicleTypeSerializer
    permission_classes = [AllowAny]
    lookup_field = 'pk'
    
    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a specific vehicle type with custom response
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        
        return Response(
            {
                "message": "Vehicle type details retrieved successfully",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class VehicleTypeDeleteView(generics.DestroyAPIView):
    """
    API view to delete a specific vehicle type.
    
    DELETE: Deletes a specific vehicle type
    """
    
    queryset = VehicleType.objects.all()
    serializer_class = VehicleTypeSerializer
    permission_classes = [IsAdminUser]
    lookup_field = 'pk'
    
    def destroy(self, request, *args, **kwargs):
        """
        Delete a vehicle type with custom response
        """
        instance = self.get_object()
        vehicle_type_name = instance.name
        
        # Check if vehicle type is being used by any vehicles
        if hasattr(instance, 'vehicles') and instance.vehicles.exists():
            return Response(
                {
                    "message": "Cannot delete vehicle type as it is being used by existing vehicles",
                    "error": "Vehicle type is in use",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        self.perform_destroy(instance)
        
        return Response(
            {
                "message": f"Vehicle type '{vehicle_type_name}' deleted successfully",
            },
            status=status.HTTP_204_NO_CONTENT,
        )



##################################asssign driver and confirm order#######################

from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

class AssignDriverCreateAPIView(generics.CreateAPIView):
    """
    POST endpoint to assign a driver to a booking and confirm it in one go.
    """
    serializer_class = VehicleBookingSerializer  # or a tailor-made serializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        booking_id = self.request.data.get('booking_id')
        driver_id = self.request.data.get('driver_id')

        booking = get_object_or_404(VehicleBooking, pk=booking_id)
        driver = get_object_or_404(User, pk=driver_id, role='driver')

        booking.assigned_driver = driver
        booking.status = VehicleBooking.STATUS_CONFIRMED
        booking.save()

        # Optionally, update serializer.instance
        serializer.instance = booking

    def create(self, request, *args, **kwargs):
        # Ensures we check required fields early
        if 'booking_id' not in request.data or 'driver_id' not in request.data:
            return Response(
                {"detail": "booking_id and driver_id are required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().create(request, *args, **kwargs)

from member.serializers import VehicleBookingSerializer

class AllBookingsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        bookings = VehicleBooking.objects.select_related('user', 'vehicle').all().order_by('-created_at')
        serializer = VehicleBookingSerializer(bookings, many=True)
        return Response({"success": True, "data": serializer.data}) 