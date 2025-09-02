from django.shortcuts import render
from users.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics, mixins, permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from django.contrib.auth.hashers import check_password
from member.models import VehicleBooking
from member.serializers import VehicleBookingSerializer
from driver.serializers import DriverUserRegisterSerializer
from .models import DriverUsageLog
from .serializers import DriverUsageLogSerializer, DriverPublicSerializer
from rest_framework.permissions import IsAuthenticated
from .serializers import DriverJobDetailSerializer
from users.serializers import DriverUpdateSerializer
from rest_framework.exceptions import ValidationError
from driver.serializers import DriverVehicleTypeSerializer
from django.utils.timezone import now



# ----------- LOGIN VIEW -----------
class UserLoginView(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data
        username = data.get("username")
        password = data.get("password")

        validation = User.objects.filter(email=username).first()
        if validation is None:
            return Response(
                {"error": "User not found."}, status=status.HTTP_404_NOT_FOUND
            )

        if validation.role.lower() != "driver":
            return Response(
                {"message": "User does not have permission to log in"},
                status=status.HTTP_403_FORBIDDEN,
            )

        if not username or not password:
            return Response(
                {
                    "success": False,
                    "data": {},
                    "message": "Provide username or password",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if username.isnumeric():
            vendor = User.objects.filter(mobile=username).first()
        else:
            vendor = User.objects.filter(email__iexact=username).first()

        if vendor is None:
            return Response(
                {"success": False, "data": {}, "message": "Invalid credentials!"},
                status=status.HTTP_403_FORBIDDEN,
            )

        if check_password(password, vendor.password):
            if vendor.is_active:
                token = self.get_auth_token(vendor)
                return Response(
                    {
                        "success": True,
                        "message": "Successfully Logged In!",
                        "data": token,
                    },
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {
                        "success": False,
                        "message": "Account deactivated! Contact Admin.",
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

        return Response(
            {
                "success": False,
                "message": "Invalid credentials! Check username or password",
            },
            status=status.HTTP_403_FORBIDDEN,
        )

    def get_auth_token(self, user: User) -> dict:
        token, created = Token.objects.get_or_create(user=user)
        return {"token": str(token.key)}


# ----------- DRIVER PROFILE UPDATE -----------
class DriverRegistrationEditAPIView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = DriverUserRegisterSerializer

    def put(self, request):
        user_instance = request.user
        serializer = DriverUpdateSerializer(
            user_instance, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"success": True, "data": serializer.data},
                status=status.HTTP_202_ACCEPTED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ----------- DRIVER ORDERS -----------
class Orders(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = VehicleBooking.objects.all()
    serializer_class = VehicleBookingSerializer

    def get_queryset(self):
        user = self.request.user
        first_name = user.first_name
        return self.queryset.filter(assigned_driver=self.request.user)


# ----------- ADMIN PANEL VIEWS -----------


class DriverDataList(generics.ListAPIView):
    queryset = User.objects.filter(role="Driver")
    serializer_class = DriverPublicSerializer


class UpdateDriverData(generics.UpdateAPIView, mixins.RetrieveModelMixin):
    queryset = User.objects.all()
    serializer_class = DriverUserRegisterSerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"success": True, "message": "Driver data updated successfully"},
            status=status.HTTP_200_OK,
        )


class DeleteDriverView(
    mixins.RetrieveModelMixin, mixins.DestroyModelMixin, generics.GenericAPIView
):
    queryset = User.objects.all()
    serializer_class = DriverUserRegisterSerializer

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {"success": True, "message": "Record deleted successfully."},
            status=status.HTTP_200_OK,
        )


class TotalDriverCount(APIView):
    def get(self, request):
        queryset = User.objects.filter(role="Driver")
        total = queryset.count()
        return Response({"success": True, "total": total})


class DriverUsageLogCreateView(generics.CreateAPIView):
    queryset = DriverUsageLog.objects.all()
    serializer_class = DriverUsageLogSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        # Option 1: If driver is linked to request.user
        driver = getattr(self.request.user, "driver", None)

        # Option 2: You pass driver_id in the request data
        if not driver:
            driver_id = self.request.data.get("driver_id")
            if driver_id:
                driver = driver.objects.get(id=driver_id)

        if not driver:
            raise ValidationError("Driver is required.")

        serializer.save(driver=driver, assigned_by=self.request.user)


class DriverUsageLogListView(generics.ListAPIView):
    queryset = DriverUsageLog.objects.all()
    serializer_class = DriverUsageLogSerializer
    permission_classes = [permissions.IsAuthenticated]


class DriverUsageLogDetailView(generics.RetrieveUpdateAPIView):
    queryset = DriverUsageLog.objects.all()
    serializer_class = DriverUsageLogSerializer
    lookup_field = "id"
    permission_classes = [permissions.IsAuthenticated]


class DriverAssignedJobsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        assigned_jobs = DriverUsageLog.objects.filter(driver=user, is_active=True)
        serializer = DriverJobDetailSerializer(assigned_jobs, many=True)
        return Response(serializer.data)


####
from rest_framework import generics, permissions
from driver.models import DriverVehicleType
from .serializers import *
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied


class AddDriverVehicleTypeView(generics.CreateAPIView):
    """
    Generic API view to add vehicle type to logged-in driver
    """

    serializer_class = DriverVehicleTypeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return DriverVehicleType.objects.filter(driver=self.request.user)

    def perform_create(self, serializer):
        # Ensure the user is a driver
        if self.request.user.role != "Driver":
            raise ValidationError("Only drivers can add vehicle types.")

        # Get vehicle type from the request data
        vehicle_type_id = self.request.data.get("vehicle_type_id")
        if not vehicle_type_id:
            raise ValidationError("vehicle_type_id is required.")

        # Validate vehicle type exists
        vehicle_type = get_object_or_404(VehicleType, id=vehicle_type_id)

        # Check if driver already has this vehicle type
        if DriverVehicleType.objects.filter(
            driver=self.request.user, vehicle_type=vehicle_type
        ).exists():
            raise ValidationError("Driver already has this vehicle type assigned.")

        # Save with the logged-in driver
        serializer.save(driver=self.request.user, vehicle_type=vehicle_type)

    def create(self, request, *args, **kwargs):
        try:
            response = super().create(request, *args, **kwargs)
            return Response(
                {
                    "success": True,
                    "message": "Vehicle type added successfully to driver.",
                    "data": response.data,
                },
                status=status.HTTP_201_CREATED,
            )
        except ValidationError as e:
            return Response(
                {
                    "success": False,
                    "message": str(e),
                    "errors": e.detail if hasattr(e, "detail") else str(e),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {
                    "success": False,
                    "message": "An error occurred while adding vehicle type.",
                    "error": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


# class DriverVehicleTypeListCreateView(generics.ListCreateAPIView):
#     """
#     List all vehicle types associated with the authenticated driver or create a new one.
#     """

#     serializer_class = DriverVehicleTypeSerializer
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         return DriverVehicleType.objects.filter(driver=self.request.user)

#     def perform_create(self, serializer):
#         serializer.save(driver=self.request.user)


class DriverVehicleTypeUpdateView(generics.UpdateAPIView):
    """
    Update a specific DriverVehicleType record
    """

    serializer_class = DriverVehicleTypeSerializer
    permission_classes = [IsAuthenticated]
    queryset = DriverVehicleType.objects.all()

    def get_queryset(self):
        # Ensure driver can only update their own vehicle types
        return DriverVehicleType.objects.filter(driver=self.request.user)


###
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from .models import DriverUsageLog
from .serializers import DriverUsageLogSerializer
from users.models import User
from vendor.models import Vehicle  # adjust if needed

from notifications.models import Notification
class AssignDriverView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        driver_id = request.data.get("driver_id")
        vehicle_id = request.data.get("vehicle_id")
        member_address = request.data.get("member_address")
        job_address = request.data.get("job_address")
        pickup_address = request.data.get("pickup_address")
        remarks = request.data.get("remarks", "")

        try:
            driver = User.objects.get(id=driver_id)
            if driver.role.lower() != "driver":
                return Response({"error": "User is not a driver."}, status=400)

            vehicle = Vehicle.objects.get(id=vehicle_id)

            usage_log = DriverUsageLog.objects.create(
                driver=driver,
                vehicle=vehicle,
                assigned_by=request.user,
                member_address=member_address,
                job_address=job_address,
                pickup_address=pickup_address,
                start_time=timezone.now(),
                remarks=remarks,
            )
            booking = VehicleBooking.objects.filter(vehicle=vehicle, user__address=member_address).first()
            if booking:
                Notification.objects.create(
                user=booking.user,
                title="ड्रायव्हर नियुक्त केला",
                message=f"{driver.get_full_name()} या ड्रायव्हरची नेमणूक तुमच्या बुकिंगसाठी करण्यात आली आहे."
    )

            return Response(
                DriverUsageLogSerializer(usage_log).data, status=status.HTTP_201_CREATED
            )

        except User.DoesNotExist:
            return Response({"error": "Driver not found."}, status=404)
        except Vehicle.DoesNotExist:
            return Response({"error": "Vehicle not found."}, status=404)


class DriverUsageLogListView(generics.ListAPIView):
    serializer_class = DriverUsageLogSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return DriverUsageLog.objects.filter(driver=self.request.user).order_by(
            "-start_time"
        )


class CompleteUsageLogView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            log = DriverUsageLog.objects.get(
                id=pk, driver=request.user, end_time__isnull=True
            )
            log.end_time = timezone.now()
            log.save()
            return Response({"message": "Usage log completed."})
        except DriverUsageLog.DoesNotExist:
            return Response({"error": "Active usage log not found."}, status=404)


# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from member.models import VehicleBooking


class DriverBookingListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        bookings = VehicleBooking.objects.filter(assigned_driver=user)
        serializer = DriverBookingSerializer(bookings, many=True)
        return Response(serializer.data)


# drivers/views.py
from rest_framework.exceptions import ValidationError


class DriverUsageLogCreateView(generics.CreateAPIView):
    queryset = DriverUsageLog.objects.all()
    serializer_class = DriverUsageLogSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        if user.role != "Driver":  # Assuming you have role field on User
            raise ValidationError("Only users with 'driver' role can create logs.")
        serializer.save(driver=user)


class DriverEditAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        instance = request.user
        serializer = UserSerializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"success": True, "data": serializer.data},
                status=status.HTTP_202_ACCEPTED,
            )
        return Response(serializer.errors, status=400)
class DriverUserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = DriverUserProfileSerializer(request.user)
        return Response(serializer.data)

from member.serializers import VehicleBookingSerializer

class AllBookingsDriverAPIView(APIView):
    #permission_classes = [IsAuthenticated]

    def get(self, request):
        bookings = VehicleBooking.objects.select_related('user', 'vehicle').all().order_by('-created_at')
        serializer = VehicleBookingSerializer(bookings, many=True)
        return Response({"success": True, "data": serializer.data}) 
    
class DriverUsageLogCreateAPIView(generics.CreateAPIView):
    serializer_class = DriverUsageLogSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        usage_log = serializer.save(driver=self.request.user)

        # Mark booking as started if needed
        if usage_log.Vechiclebooking and usage_log.booking.assigned_driver_id == self.request.user:
            Notification.objects.filter(
                recipient=self.request.user,
                booking=usage_log.booking,
                notification_type="booking_assignment"
            ).update(driver_response="accepted")
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from .models import DriverUsageLog
from .serializers import DriverUsageLogSerializer

class DriverUsageLogUpdateAPIView(generics.UpdateAPIView):
    serializer_class = DriverUsageLogSerializer
    permission_classes = [IsAuthenticated]
    queryset = DriverUsageLog.objects.all()

    def get_queryset(self):
        # Ensure driver can only update their own logs
        return self.queryset.filter(driver=self.request.user)

    def patch(self, request, *args, **kwargs):
        usage_log = self.get_object()
        action = request.data.get("action")

        if action == "start":
            usage_log.start_time = timezone.now()
            usage_log.is_active = True
        elif action == "end":
            usage_log.end_time = timezone.now()
            usage_log.is_active = False
            usage_log.remarks = request.data.get("remarks", "")

            # Make driver available again
            usage_log.driver.is_driver_available = True
            usage_log.driver.save()

        usage_log.save()
        serializer = self.get_serializer(usage_log)
        return Response(serializer.data)
class DriverUsageLogFilteredListView(generics.ListAPIView):
    serializer_class = DriverJobDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        booking_id = self.request.query_params.get("booking_id")
        return DriverUsageLog.objects.filter(booking__id=booking_id)
#in test
class DriverBookingInfoAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, booking_id):  # booking_id here is booking.booking_id, not booking.id
        try:
            booking = VehicleBooking.objects.get(booking_id=booking_id)
            booking_serializer = VehicleBookingSerializer(booking)

            # Fetch the first usage log (if multiple exist)
            usage_log = DriverUsageLog.objects.filter(booking=booking).first()
            usage_log_data = DriverUsageLogSerializer(usage_log).data if usage_log else None

            response_data = booking_serializer.data
            response_data["usage_log"] = usage_log_data  # Add to response

            return Response(response_data)

        except VehicleBooking.DoesNotExist:
            return Response({"detail": "Booking not found."}, status=status.HTTP_404_NOT_FOUND)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from notifications.models import Notification
from driver.models import DriverUsageLog


class RespondToDriverAssignmentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, notification_id):
        try:
            notification = Notification.objects.get(id=notification_id, user=request.user)

            response_value = request.data.get("response")
            reason = request.data.get("reason", "")

            if response_value not in ["accept", "reject"]:
                return Response({"detail": "Invalid response value."}, status=400)

            # Update response on Notification
            notification.driver_response = response_value
            notification.rejection_reason = reason if response_value == "reject" else ""
            notification.save()

            # Create DriverUsageLog if accepted
            if response_value == "accept":
                booking = notification.booking

                # Prevent duplicate logs
                log_exists = DriverUsageLog.objects.filter(
                    booking=booking,
                    driver=request.user
                ).exists()

                if not log_exists:
                    DriverUsageLog.objects.create(
                        booking=booking,
                        driver=request.user,
                        assigned_by="System"  # or store admin user if applicable
                    )

            return Response({"detail": "Response recorded successfully."})

        except Notification.DoesNotExist:
            return Response({"detail": "Notification not found."}, status=404)

        except VehicleBooking.DoesNotExist:
            return Response({"detail": "Booking not found."}, status=404)

        except Exception as e:
            return Response({"detail": f"Unexpected error: {str(e)}"}, status=500)
# driver/views.py

from rest_framework import generics, permissions
from member.models import VehicleBooking
from driver.serializers import DriverAssignedBookingSerializer

class DriverAssignedBookingsView(generics.ListAPIView):
    serializer_class = DriverAssignedBookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return VehicleBooking.objects.filter(
            assigned_driver=self.request.user,  # ensures driver is set
            status='confirmed'
        ).exclude(assigned_driver__isnull=True).select_related('vehicle', 'vehicle__user', 'user')

#driver log start time
class StartWorkView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, booking_id):
        try:
            booking = VehicleBooking.objects.get(pk=booking_id, assigned_driver=request.user)
        except VehicleBooking.DoesNotExist:
            return Response({"detail": "Booking not found."}, status=status.HTTP_404_NOT_FOUND)

        if not booking.vehicle:
            return Response({"detail": "No vehicle assigned for this booking."}, status=status.HTTP_400_BAD_REQUEST)

        log, created = DriverUsageLog.objects.get_or_create(
            booking=booking,
            driver=request.user,
            defaults={
                'vehicle': booking.vehicle,
                'start_time': now(),
                'assigned_by': request.user
            }
        )

        if not created and log.start_time:
            return Response({"detail": "Work already started."}, status=status.HTTP_400_BAD_REQUEST)

        if not log.start_time:
            log.start_time = now()
            log.save()

        return Response({
            "detail": "Work started successfully.",
            "booking_id": booking.booking_id,
            "start_time": log.start_time
        }, status=status.HTTP_200_OK)

#driver log end work
class EndWorkView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, booking_id):
        try:
            booking = VehicleBooking.objects.get(pk=booking_id, assigned_driver=request.user)
        except VehicleBooking.DoesNotExist:
            return Response({"detail": "Booking not found."}, status=status.HTTP_404_NOT_FOUND)

        try:
            log = DriverUsageLog.objects.get(booking=booking, driver=request.user)
        except DriverUsageLog.DoesNotExist:
            return Response({"detail": "Start work first."}, status=status.HTTP_400_BAD_REQUEST)

        if log.end_time:
            return Response({"detail": "Work already ended."}, status=status.HTTP_400_BAD_REQUEST)

        log.end_time = now()
        log.save()
        return Response({
            "detail": "Work ended successfully.",
            "booking_id": booking.booking_id,
            "end_time": log.end_time
        }, status=status.HTTP_200_OK)

#driver complain 
class DriverComplaintCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, booking_id):
        try:
            booking = VehicleBooking.objects.get(pk=booking_id, assigned_driver=request.user)
        except VehicleBooking.DoesNotExist:
            return Response({"detail": "Booking not found or unauthorized."}, status=status.HTTP_404_NOT_FOUND)

        serializer = DriverComplaintSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(driver=request.user, booking=booking)
            return Response({"detail": "Complaint submitted successfully."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
