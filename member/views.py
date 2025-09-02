from django.shortcuts import render
from rest_framework import status
from rest_framework.views import APIView
from member.serializers import *
from rest_framework import generics,views,mixins,status
from member.models import *
from users.models import User
from rest_framework.response import Response
from django.contrib.auth.hashers import make_password, check_password
from users.models import DistrictModel,TalukaModel,VillageModel
from admin_panel.serializers import TalukaSerializer,VillageSerializer
from vendor.serializers import VendorSerializer,VehicleSerializer
from vendor.models import Vehicle
from rest_framework.permissions import IsAuthenticated
from django.db.models import Max
from rest_framework.authtoken.models import Token
from rest_framework.test import APIRequestFactory
from django.http import HttpRequest
from rest_framework.test import APIClient
from rest_framework import response
#from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import generics, permissions, filters
from django.db.models import Q


class MemberRegistrationForm(generics.CreateAPIView):

    queryset =  User.objects.all()
    serializer_class = member_registrationSerializer

class MemberRegistrationUpdate(views.APIView):
    permission_classes = [IsAuthenticated]
    def put(self, request):
        serializer = member_registrationSerializer(request.user, data=request.data, partial=True)
        print('request user',request.user)
        print('@@@@@@@@@@',serializer)
        if serializer.is_valid():  
            serializer.save()
            return Response({"success":True,"data":serializer.data},status=status.HTTP_202_ACCEPTED)
        return response.Response(serializer.errors, status=400)

from rest_framework import generics, permissions
from .models import varasadhar_details
from .serializers import varasadhar_detailSerializer

class VarasadharListCreateView(generics.ListCreateAPIView):
    queryset = varasadhar_details.objects.all()
    serializer_class = varasadhar_detailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Return only current user's records
        return varasadhar_details.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Automatically set user from request
        serializer.save(user=self.request.user)

class VarasadharRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = varasadhar_details.objects.all()
    serializer_class = varasadhar_detailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # User can only update/delete their own records
        return varasadhar_details.objects.filter(user=self.request.user)



class BankDetails(generics.CreateAPIView):

    queryset = bank_details.objects.all()
    serializer_class = bank_detailsSerializer

class BankDetailsUpdate(views.APIView):
    permission_classes = [IsAuthenticated]
    def put(self, request):
        instance = bank_details.objects.get(user=request.user)
        serializer = bank_detailsSerializer(instance, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return response.Response({"success":True,"data":serializer.data},status=status.HTTP_202_ACCEPTED)
        return response.Response(serializer.errors, status=400)
    

# ──────────────────────────────────────────────
#  BANK DETAILS – list, create, retrieve, update, delete
#      These endpoints match the React calls:
#      /member/banks/         (GET, POST)
#      /member/banks/<pk>/    (GET, PUT, DELETE)
# ──────────────────────────────────────────────
from rest_framework import generics, permissions   # make sure already imported
from member.models import bank_details
from member.serializers import bank_detailsSerializer

class BankDetailsListCreateAPIView(generics.ListCreateAPIView):
    queryset = bank_details.objects.all()
    serializer_class = bank_detailsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return bank_details.objects.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class BankDetailRUDAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class   = bank_detailsSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field       = "pk"

    def get_queryset(self):
        return bank_details.objects.filter(user=self.request.user)


        
#class FarmDetails(generics.CreateAPIView):

#    queryset = farm_details.objects.all()
#    serializer_class = farm_detailsSerializer

class FarmDetailsListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = farm_detailsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return farm_details.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class FarmDetailsRUDAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = farm_detailsSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = farm_details.objects.all()

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)


class FarmDetailsUpdateCurrentAPIView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request):
        try:
            instance = farm_details.objects.get(user=request.user)
        except farm_details.DoesNotExist:
            return response.Response({"error": "Farm details not found."}, status=404)

        serializer = farm_detailsSerializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return response.Response({"success": True, "data": serializer.data}, status=status.HTTP_202_ACCEPTED)
        return response.Response(serializer.errors, status=400)
        


class UserLoginView(APIView):
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response({
                'success': False,
                'message': 'Username and password are required'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Try to fetch user by email or mobile
        user = None
        if username.isnumeric():
            user = User.objects.filter(mobile=username).first()
        else:
            user = User.objects.filter(email__iexact=username).first()

        if not user:
            return Response({
                'success': False,
                'message': 'Invalid credentials'
            }, status=status.HTTP_403_FORBIDDEN)

        if not user.check_password(password):
            return Response({
                'success': False,
                'message': 'Incorrect password'
            }, status=status.HTTP_403_FORBIDDEN)

        if user.role.lower() != 'member':
            return Response({
                'success': False,
                'message': 'Only members are allowed to login'
            }, status=status.HTTP_403_FORBIDDEN)

        if not user.is_active:
            return Response({
                'success': False,
                'message': 'Account is deactivated'
            }, status=status.HTTP_403_FORBIDDEN)

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        return Response({
            'success': True,
            'message': 'Login successful',
            'data': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user_id': user.id,
                'email': user.email,
                'mobile': user.mobile,
                'role': user.role
            }
        }, status=status.HTTP_200_OK)
        
###################vehicle list using filters new code #################
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from vendor.serializers import VehicleListSerializer
from vendor.models import VehicleUnavailablePeriod  
from datetime import datetime
from rest_framework.permissions import AllowAny
class VehicleListView(generics.ListAPIView):
    
    permission_classes= [AllowAny]
    serializer_class = VehicleListSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = [
        'district', 'taluka', 'village', 'vehicle_type', 
    ]
    search_fields = ['district', 'taluka', 'village', 'vehicle_type',]
    ordering_fields = ['rental_price_per_hour', 'created_at', 'year']
    ordering = ['-created_at']
    
    def get_queryset(self):
        
        # Filter by location type
        location_type = self.request.query_params.get('location_type')
        location_id = self.request.query_params.get('location_id')
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        start_date= str(start_date)
        end_date= str(end_date)
        
       
        # date_obj = datetime.strptime(start_date, "%d-%m-%Y").date()
        # start_date = date_obj.strftime("%Y-%m-%d")

        # date_obj = datetime.strptime(end_date, "%d-%m-%Y").date()
        # end_date = date_obj.strftime("%Y-%m-%d")
      
        try:
            if isinstance(start_date, str):
                start_date = timezone.datetime.strptime(start_date, "%Y-%m-%d").date()
                end_date = timezone.datetime.strptime(end_date, "%Y-%m-%d").date()
        except ValueError:
            raise ValidationError("Invalid date format. Please use YYYY-MM-DD.")

        # Get all vehicles that are not unavailable during the specified date range
        queryset = Vehicle.objects.filter(
            ~models.Q(id__in=VehicleUnavailablePeriod.objects.filter(
                start_date__lte=end_date,
                end_date__gte=start_date
            ).values('vehicle'))
        )
        
        if location_type and location_id:
            if location_type == 'village':
                queryset = queryset.filter(village__id=location_id)
            elif location_type == 'taluka':
                queryset = queryset.filter(taluka__id=location_id)
            elif location_type == 'district':
                queryset = queryset.filter(district__id=location_id)
            
        # Filter by price range
        #vehicle_type = self.request.query_params.get('vehicle_type')
        
        # if vehicle_type:
        #     queryset=queryset.filter(vehicle_type__id=vehicle_type)


        # Exclude own vehicles
        if self.request.user.is_authenticated:
            queryset = queryset.exclude(user=self.request.user)
        
        return queryset
    
    def list(self, request, *args, **kwargs):
        """
        Override list method to customize the response format.
        """
        vehicles = self.get_queryset()
        serializer = self.get_serializer(vehicles, many=True)
        return Response(serializer.data)

 

###########################old code##############################

class SearchVendorUsingVillage(generics.ListAPIView):
    serializer_class = UserSerializer
    def get_queryset(self):
        Village_name = self.request.query_params.get("Village")
        if Village_name:
            
            Village = User.objects.filter(Village=Village_name,role = 'Vendor')
            return Village
        else:
            return User.objects.none()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if queryset.exists():
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        else:
            return Response({'error': 'No vendor found for the given Village'}, status=404)

class VendorVehicleInfo(generics.ListAPIView):
    serializer_class = VehicleSerializer
    def get_queryset(self):
        vendor_name = self.request.query_params.get("vendor")
        print('vendor_name***********',vendor_name)
        queryset = User.objects.filter(id=vendor_name)
        print('queryset',queryset)
        user = queryset.first()  # Retrieve the first instance from the queryset
        print('user', user)
        if user:
            request = self.context.get("request")
            Village = Vehicle.objects.filter(user__id=vendor_name)
            return Village
        else:
            return Vehicle.objects.none()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if queryset.exists():
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        else:
            return Response({'error': 'No'}, status=404)

class VehicleDetail(generics.RetrieveAPIView):
    serializer_class =  VehicleSerializer
    queryset = Vehicle.objects.all()
    lookup_field = 'pk'
    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        global vehicle_id
        vehicle_id = instance.id  
        request.session['vehicle_id'] = vehicle_id
        print("Vehicle ID stored in session:", request.session.get('vehicle_id'))
        return super().get(request, *args, **kwargs)
    
#######################vehicle booking, or cancell api###################

class VehicleBookingListCreateAPIView(generics.ListCreateAPIView):
    """
    List all bookings for authenticated user or create a new booking
    """
    serializer_class = VehicleBookingSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'vehicle__vehicle_type', 'service_village']
    ordering_fields = ['booking_date', 'created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        return VehicleBooking.objects.select_related(
            'user', 'vehicle', 'assigned_driver', 'service_village'
        ).filter(user=self.request.user)

class VehicleBookingDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a specific booking
    """
    serializer_class = VehicleBookingSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'booking_id'
    
    def get_queryset(self):
        user = self.request.user
        return VehicleBooking.objects.select_related(
            'user', 'vehicle', 'assigned_driver', 'service_village'
        ).filter(
            Q(user=user) | Q(assigned_driver=user)
        )
    

class CancelBookingAPIView(generics.UpdateAPIView):
    """
    Cancel a booking by updating its status to 'cancelled'
    """
    serializer_class = VehicleBookingSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'booking_id'
    http_method_names = ['post', 'patch']  # Allow both POST and PATCH methods
    
    def get_queryset(self):
        return VehicleBooking.objects.select_related(
            'user', 'vehicle', 'assigned_driver', 'service_village'
        ).filter(user=self.request.user)
    
    def get_object(self):
        """
        Override to add custom validation before cancellation
        """
        booking = super().get_object()
        
        # Check if booking can be cancelled
        if booking.status in ['completed', 'cancelled']:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({
                'error': 'Cannot cancel a completed or already cancelled booking'
            })
        
        return booking
    
    def perform_update(self, serializer):
        """
        Override to only update the status to cancelled
        """
        serializer.save(status='cancelled')
    
    def update(self, request, *args, **kwargs):
        """
        Override to return custom success message
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        # Force the status to cancelled regardless of request data
        data = {'status': 'cancelled'}
        serializer = self.get_serializer(instance, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        self.perform_update(serializer)
        
        return Response(
            {
                'message': 'Booking cancelled successfully',
                'booking_id': instance.booking_id,
                'status': 'cancelled'
            },
            status=status.HTTP_200_OK
        )

##############################################vehicle booking#############################################

# from rest_framework.exceptions import NotFound, ValidationError  
# class VehicleBookingCreation(generics.CreateAPIView, generics.ListAPIView):
#     queryset = VehicleBooking.objects.all()
#     serializer_class = VehicleBookingSerializer

#     def perform_create(self, serializer):
#         print("perform_create method called")
#         vehicle_id = self.request.data.get('vehicle_id')

#         if not vehicle_id:
#             raise ValidationError({"vehicle_id": "This field is required."})

#         try:
#             vehicle = Vehicle.objects.get(pk=vehicle_id)
#         except Vehicle.DoesNotExist:
#             raise NotFound(detail=f"Vehicle with id {vehicle_id} does not exist.")

#         # Get service location from request data
#         service_lat = self.request.data.get('service_latitude')
#         service_lon = self.request.data.get('service_longitude')
#         service_address = self.request.data.get('service_address')

#         booking = serializer.save(
#             vehicle=vehicle,
#             service_latitude=service_lat,
#             service_longitude=service_lon,
#             service_address=service_address
#         )

#         # Attempt to assign driver automatically
#         from auto_assign.services import DriverAssignmentService
        
#         assignment_success = DriverAssignmentService.assign_driver_to_booking(booking)
        
#         if assignment_success:
#             # Refresh booking to get assigned driver data
#             booking.refresh_from_db()

#     def list(self, request, *args, **kwargs):
#         queryset = self.get_queryset()
#         serializer = self.get_serializer(queryset, many=True)
#         return Response(serializer.data)

class DisplayCharges(generics.ListAPIView):
    serializer_class = VehicleBookingSerializer

    def get_queryset(self):
        vehicle_id = self.request.session.get('vehicle_id')
        last_created_at = VehicleBooking.objects.filter(vehicle=vehicle_id).aggregate(last_created_at=Max('created_at'))['last_created_at']
        if vehicle_id is not None:
            return VehicleBooking.objects.filter(vehicle=vehicle_id,created_at=last_created_at) 
        else:
            return VehicleBooking.objects.none()

class RatingCreationAPIView(generics.ListCreateAPIView):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer
    permission_classes = [IsAuthenticated]  # <-- only authenticated users can submit/view ratings

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
   
class LoginUserBookingRatingList(generics.ListAPIView):
    serializer_class = VehicleBookingSerializer

    def get_queryset(self):
        user = self.request.user
        #made changes here
        return VehicleBooking.objects.filter(user=user)
    def post(self,request,*args,**kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            booking_id = serializer.data.get('id')
            rating = serializer.data.get('rating')
            try:
                booking = VehicleBooking.objects.get(id=booking_id)
                booking.rating = rating
                booking.save()
                return Response({'message': 'Rating added successfully'}, status=status.HTTP_200_OK)
            except VehicleBooking.DoesNotExist:
                return Response({'error': 'Booking not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class AllMyBookingDashboard(generics.ListAPIView):
    serializer_class = VehicleBookingSerializer

    def get_queryset(self):
        user = self.request.user
        return VehicleBooking.objects.filter(user=user).order_by('-created_at')

class ComplaintDropDownList(generics.ListAPIView):
    queryset = ComplaintDropDownModel.objects.all()
    serializer_class = ComplaintDropDownSerializer

class BookOrderDashboard1(generics.ListAPIView):
    queryset = Vehicle.objects.all()
    serializer_class =  VehicleSerializer

class LoginUserComplaintList(generics.ListAPIView):
    serializer_class = VehicleBookingSerializer

    def get_queryset(self):
        user = self.request.user
        return VehicleBooking.objects.filter(vehicle=user)


    

# class BookOrderDashboard2(generics.RetrieveAPIView):
#     queryset = VehicleBooking.objects.all()
#     serializer_class = VehicleBookingSerializer
#     lookup_field = 'pk'
#     def get(self, request, *args, **kwargs):
#         instance = self.get_object()

################ ADMIN_PANEL #################

class UpdateMemberData(mixins.RetrieveModelMixin,generics.UpdateAPIView):
    member = User.objects.all()
    serializer_class = UserSerializer
    def get(self,request,*args,**kwargs):
        return self.retrieve(self,*args,**kwargs)
    def update(self,request,*args,**kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance,request.data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message":"Member data update successfully"})
 
            
class DeleteMemberData(mixins.DestroyModelMixin,mixins.RetrieveModelMixin,generics.GenericAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    def delete(self,request,*args,**kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"success": True,'message': 'Record deleted successfully.'},status=status.HTTP_200_OK)

class InstrumentList(generics.ListAPIView):
    queryset = instrument.objects.all()
    serializer_class = instrumentSerializer

class ComfirmBookingOrder(generics.ListAPIView):
    queryset = VehicleBooking.objects.all()
    serializer_class = VehicleBookingSerializer
    

class MemberEditAPIView(APIView):
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
class MemberUserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = MemberUserProfileSerializer(request.user)
        return Response(serializer.data)
    
class FarmDetailsListCreateAPIView(generics.ListCreateAPIView):
    queryset           = farm_details.objects.all()
    serializer_class   = farm_detailsSerializer
    permission_classes = [permissions.IsAuthenticated]

    # Only admin sees all rows; a member sees just their own
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:                  # or custom IsAdmin
            return farm_details.objects.all()
        return farm_details.objects.filter(user=user)

    # on POST automatically attach current user
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

# ─────────────────────────────────────────────
# 2. Retrieve / Update / Delete by primary‑key
#    e.g.   /member/farm-details/7/
# ─────────────────────────────────────────────
class FarmDetailsRUDAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset           = farm_details.objects.all()
    serializer_class   = farm_detailsSerializer
    permission_classes = [permissions.IsAuthenticated]

# ─────────────────────────────────────────────
# 3. PUT  /member/farm-details-update/
#    update current logged‑in user’s record without passing id
# ─────────────────────────────────────────────
class FarmDetailsUpdateCurrentAPIView(generics.UpdateAPIView):
    serializer_class   = farm_detailsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        # If record exists return it; else raise 404
        return farm_details.objects.get(user=self.request.user)

#############################complaient create and list view

from django.urls import path
from rest_framework import generics, status, serializers
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.contrib.auth.models import User
class ComplaintCreateView(generics.CreateAPIView):
    """
    API view to register/create a new complaint.
    
    POST: Creates a new complaint for the authenticated user
    """
    
    queryset = ComplaintModel.objects.all()
    serializer_class = ComplaintSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        """
        Save the complaint with the authenticated user
        """
        serializer.save(user=self.request.user)
    
    def create(self, request, *args, **kwargs):
        """
        Create a new complaint with custom response
        """
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            self.perform_create(serializer)
            
            return Response(
                {
                    "message": "Complaint registered successfully",
                    "success": True,
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )
        
        return Response(
            {
                "message": "Failed to register complaint",
                "success": False,
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

class UserComplaintsListView(generics.ListAPIView):
    """
    API view to list all complaints by the authenticated user.
    
    GET: Returns list of all complaints for the authenticated user
    """
    
    serializer_class = ComplaintSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Return complaints for the authenticated user with optional filtering
        """
        queryset = ComplaintModel.objects.filter(user=self.request.user)
        
        # Optional filtering by reason
        reason_filter = self.request.query_params.get('reason', None)
        if reason_filter:
            queryset = queryset.filter(reason__icontains=reason_filter)
        
        # Optional search in description
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                models.Q(reason__icontains=search) | 
                models.Q(description__icontains=search)
            )
        
        return queryset.order_by('-id')
    
    def list(self, request, *args, **kwargs):
        """
        List user's complaints with custom response and filtering
        """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        
        return Response(
            {
                "message": "User complaints retrieved successfully",
                "success": True,
                "total_complaints": queryset.count(),
                "filters_applied": {
                    "reason": request.query_params.get('reason', None),
                    "search": request.query_params.get('search', None),
                },
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

class ComplaintUpdateView(generics.UpdateAPIView):
    queryset = ComplaintModel.objects.all()
    serializer_class = ComplaintSerializer
    permission_classes = [IsAuthenticated]

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)

    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

class ComplaintDeleteView(generics.DestroyAPIView):
    queryset = ComplaintModel.objects.all()
    serializer_class = ComplaintSerializer
    permission_classes = [IsAuthenticated]


#from rest_framework_simplejwt.authentication import JWTAuthentication

class MemberBookingDropdownAPIView(APIView):
    """
    API to return a dropdown list of member's bookings for complaint registration
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        bookings = VehicleBooking.objects.filter(user=request.user).order_by('-booking_id')
        data = [
            {
                "id": booking.booking_id,
                "label": f"बुकिंग #{booking.booking_id} - {booking.vehicle.vehicle_name if booking.vehicle else ''}"
            }
            for booking in bookings
        ]
        return Response({"success": True, "bookings": data})

class MemberBookingListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        bookings = VehicleBooking.objects.filter(user=user)
        serializer = VehicleBookingSerializer(bookings, many=True)
        return Response({"success": True, "data": serializer.data})

