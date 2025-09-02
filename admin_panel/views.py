from django.shortcuts import get_object_or_404, render
from rest_framework import generics,mixins,viewsets,response,status,views, permissions, filters
from rest_framework.response import Response 
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from member.serializers import UserSerializer
from django.db import transaction


#from users.models import User,
from rest_framework.authtoken.models import Token
from django.contrib.auth import logout
from django.db.models import Q
from datetime import date
from django.utils import timezone
from rest_framework.permissions import IsAdminUser

from users.models import DistrictModel,TalukaModel,VillageModel
from admin_panel import serializers as adminpanel_serializer
from admin_panel.permissions import IsAdminUser
#from member.models import VehicleBooking
#from member.serializers import VehicleBookingSerializer
#from driver.serializers import UserSerializer
from users.models import User
from admin_panel.serializers import *

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny
from django.conf import settings


############ login page for admin ##############
class AdminUserLoginView(views.APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        data = request.data
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return Response({'success': False, 'message': 'Provide username or password'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(mobile=username).first() if username.isnumeric() \
            else User.objects.filter(email__iexact=username).first()

        if not user or not user.check_password(password):
            return Response({'success': False, 'message': 'Invalid credentials!'}, status=status.HTTP_403_FORBIDDEN)

        if not user.is_admin:
            return Response({'success': False, 'message': 'You do not have permission to perform this action!'}, status=status.HTTP_403_FORBIDDEN)

        if not user.is_active:
            return Response({'success': False, 'message': 'Account deactivated! Contact Admin.'}, status=status.HTTP_403_FORBIDDEN)

        # Generate tokens
        refresh = RefreshToken.for_user(user)
        access = refresh.access_token

        # Token data for frontend
        token_data = {
            'refresh': str(refresh),
            'access': str(access),
        }

        # User data
        user_data = {
            'user_id': user.id,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'mobile': user.mobile,
            'email': user.email,
            'city': user.city,
            'state': user.state,
            'country': user.country,
            'zipcode': user.zipcode,
            'active': user.is_active,
        }

        # Final response
        response = Response({
            'success': True,
            'message': 'Successfully Logged In!',
            'data': user_data,
            'token': token_data
        }, status=status.HTTP_200_OK)

        # Set HttpOnly cookies for security
        response.set_cookie(
            key='access',
            value=str(access),
            httponly=True,
            secure=not settings.DEBUG,
            samesite='Lax',
            max_age=3600
        )
        response.set_cookie(
            key='refresh',
            value=str(refresh),
            httponly=True,
            secure=not settings.DEBUG,
            samesite='Lax',
            max_age=7 * 24 * 3600
        )

        return response


################# Dashboard ########################
class VillageCountView(generics.ListAPIView):
    def get(self, request, *args, **kwargs):
        Village_count = VillageModel.objects.count()
        response_data = {"success": True,"total_count": Village_count}
        return Response(response_data,status=status.HTTP_200_OK)

class DistrictCountView(generics.ListAPIView):
    def get(self, request, *args, **kwargs):
        district_count = DistrictModel.objects.count()
        response_data = {"success": True,"total_count": district_count}
        return Response(response_data,status=status.HTTP_200_OK)
    
class TalukaCountView(generics.ListAPIView):
    def get(self, request, *args, **kwargs):
        Taluka_count = TalukaModel.objects.count()
        response_data = {"success": True,"total_count": Taluka_count}
        return Response(response_data,status=status.HTTP_200_OK)


#################  District #############################
class GetDistrictListView(generics.ListAPIView):
    queryset = DistrictModel.objects.all()
    serializer_class = adminpanel_serializer.DistrictSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        search = self.request.query_params.get('search',None)
        queryset = DistrictModel.objects.all()

        if search:
            queryset = queryset.filter(name__icontains=search)          
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        response_data = {"success": True,"data": serializer.data}
        return Response(response_data,status=status.HTTP_200_OK)


class CreateDistrictView(generics.CreateAPIView):

    queryset = DistrictModel.objects.all()
    serializer_class = adminpanel_serializer.DistrictSerializer
    permission_classes = [IsAdminUser]

    def get_serializer_context(self, *args, **kwargs):
        return {
            "request": self.request,
            "args": self.args,
            "kwargs": self.kwargs
        }
    
class UpdateDistrictView(generics.UpdateAPIView, mixins.RetrieveModelMixin):
    queryset = DistrictModel.objects.all()
    serializer_class = adminpanel_serializer.DistrictSerializer
    permission_classes = [IsAdminUser]

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"success": True,"message": "District updated successfully"}, status=status.HTTP_200_OK)

class DeleteDistrictView(mixins.RetrieveModelMixin,mixins.DestroyModelMixin,generics.GenericAPIView):
    queryset = DistrictModel.objects.all()
    serializer_class = adminpanel_serializer.DistrictSerializer
    permission_classes = [IsAdminUser,]

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"success": True,'message': 'Record deleted successfully.'},status=status.HTTP_200_OK)

#################  Taluka #############################

class GetTalukaListView(generics.ListAPIView):
    queryset = TalukaModel.objects.all()
    serializer_class = adminpanel_serializer.TalukaSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        search = self.request.query_params.get('search',None)
        queryset = TalukaModel.objects.all()

        if search:
            queryset = queryset.filter(name__icontains=search)          
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        response_data = {"success": True,"data": serializer.data}
        return Response(response_data,status=status.HTTP_200_OK)


class CreateTalukaView(generics.CreateAPIView):

    queryset = TalukaModel.objects.all()
    serializer_class = adminpanel_serializer.TalukaSerializer
    permission_classes = [IsAdminUser]

    def get_serializer_context(self, *args, **kwargs):
        return {
            "request": self.request,
            "args": self.args,
            "kwargs": self.kwargs
        }
    
class UpdateTalukaView(generics.UpdateAPIView, mixins.RetrieveModelMixin):
    queryset = TalukaModel.objects.all()
    serializer_class = adminpanel_serializer.TalukaSerializer
    permission_classes = [IsAdminUser]

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'message': 'Taluka updated successfully'}, status=status.HTTP_200_OK)

class DeleteTalukaView(mixins.RetrieveModelMixin,mixins.DestroyModelMixin,generics.GenericAPIView):
    queryset = TalukaModel.objects.all()
    serializer_class = adminpanel_serializer.TalukaSerializer
    permission_classes = [IsAdminUser,]

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"success": True,'message': 'Record deleted successfully.'},status=status.HTTP_200_OK)
    
##################  Village #############################

class GetVillageListView(generics.ListAPIView):
    queryset = VillageModel.objects.all()
    serializer_class = adminpanel_serializer.VillageSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        search = self.request.query_params.get('search',None)
        queryset = VillageModel.objects.all()

        if search:
            queryset = queryset.filter(name__icontains=search)          
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        response_data = {"success": True,"data": serializer.data}
        return Response(response_data,status=status.HTTP_200_OK)


class CreateVillageView(generics.CreateAPIView):

    queryset = VillageModel.objects.all()
    serializer_class = adminpanel_serializer.VillageSerializer
    permission_classes = [IsAdminUser]

    def get_serializer_context(self, *args, **kwargs):
        return {
            "request": self.request,
            "args": self.args,
            "kwargs": self.kwargs
        }
    
class UpdateVillageView(generics.UpdateAPIView, mixins.RetrieveModelMixin):
    queryset = VillageModel.objects.all()
    serializer_class = adminpanel_serializer.VillageSerializer
    permission_classes = [IsAdminUser]

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'message': 'Village updated successfully'}, status=status.HTTP_200_OK)

class DeleteVillageView(mixins.RetrieveModelMixin,mixins.DestroyModelMixin,generics.GenericAPIView):
    queryset = VillageModel.objects.all()
    serializer_class = adminpanel_serializer.VillageSerializer
    permission_classes = [IsAdminUser,]

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"success": True,'message': 'Record deleted successfully.'},status=status.HTTP_200_OK)
    
######################################## groups search#################################################

class SearchGroupUsingVillage(generics.ListAPIView):
    serializer_class = GroupModelSerializer
    def get_queryset(self):
        Village_name = self.request.query_params.get("Village")
        if Village_name:
            
            Village = GroupModel.objects.filter(Village_name=Village_name)
            return Village
        else:
            return GroupModel.objects.none()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if queryset.exists():
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        else:
            return Response({'error': 'No Group found for the given Village'}, status=404)



class MemberListInGroup(generics.ListAPIView):
    serializer_class = GroupModelSerializer
    def get_queryset(self):
        group_name = self.request.query_params.get("group")
        queryset = User.objects.filter(id=group_name)
        user = queryset.first()  
        print('user', user)
        if user:
            Village = GroupModel.objects.filter(group_name=user)
            return Village
        else:
            return GroupModel.objects.none()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if queryset.exists():
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        else:
            return Response({'error': 'No'}, status=404)
        
class First100MembersView(generics.ListAPIView):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = UserSerializer

    def get_queryset(self):
        return User.objects.filter(role="Member").order_by("created_at")[:100]
    
class AssignGatAdhikariView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        user_id = request.data.get("user_id")

        if not user_id:
            return Response({"error": "user_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Demote existing Gat_Adhikari if exists
            existing = User.objects.filter(role="Gat_Adhikari").first()
            if existing:
                existing.role = "Member"
                existing.save()

            # Promote the selected user
            user = User.objects.get(id=user_id)
            if user.role != "Member":
                return Response({"error": "Only Member can be promoted"}, status=status.HTTP_400_BAD_REQUEST)
            
            if "Gat_Adhikari" not in user.role:
                user.role += ",Gat_Adhikari"  # Append role as a comma-separated string
                user.save()
            

            return Response({"success": f"{user.full_name or user.email} is now Gat Adhikari."}, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)



################# Confirm Order Booking #################

# class ConfirmOrderBookingList(generics.ListAPIView):
#     queryset = VehicleBooking.objects.all().objects.all()
#     serializer_class = 
"""
class BookingUpdate(generics.UpdateAPIView, mixins.RetrieveModelMixin):
    queryset = Booking.objects.all()
    serializer_class = DriverAssignSerilizer
    lookup_field = 'booking_id'

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"success": True, "message": "data updated successfully", "data": serializer.data}, status=status.HTTP_200_OK)


    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if queryset.exists():
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        else:
            return Response({'error': 'No Driver found for the given Village'}, status=404)
"""
# class BookingList(generics.RetrieveAPIView):
#     queryset = VehicleBooking.objects.all()
#     serializer_class = 

#     lookup_field = 'pk'
    
#     def list(self, request, *args, **kwargs):
#         queryset = self.get_queryset()
#         serializer = self.get_serializer(queryset,many=True)
#         return Response({'data': serializer.data})
    
######################count#######################
class DriverCountView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        total = User.objects.filter(role='Driver').count()
        
        return Response({"success": True, "total": total})

class MemberCountView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        queryset = User.objects.filter(role='Member').count()
        return Response({"success": True, "total": queryset})

class VendorCountView(APIView):
    permission_classes = [IsAdminUser]
    def get(self, request):
        total= User.objects.filter(role='Vendor').count()
        return Response({"success": True, "total": total})


 ########################assign and    

from rest_framework.exceptions import ValidationError

from django.db import models
from django_filters.rest_framework import DjangoFilterBackend

class SearchDriverUsingVillage(generics.ListAPIView):
    
    permission_classes =[AllowAny]
    serializer_class = UserSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = [
        'district', 'taluka', 'village', 'vehicle_type', 
    ]
    search_fields = ['district', 'taluka', 'village','name', 'email']
    ordering_fields = ['created_at', 'year']
    ordering = ['-created_at']
    
   
    def get_queryset(self):
        
        # Filter by location type
        location_type = self.request.query_params.get('location_type')
        location_id = self.request.query_params.get('location_id')
        start_date = str(self.request.query_params.get('start_date', timezone.now().date()))
        end_date = str(self.request.query_params.get('end_date', timezone.now().date()))

        try:
            start_date = timezone.datetime.strptime(start_date, "%Y-%m-%d").date()
            end_date = timezone.datetime.strptime(end_date, "%Y-%m-%d").date()
        except ValueError:
            raise ValidationError("Invalid date format. Please use YYYY-MM-DD.")

        # Get all vehicles that are not unavailable during the specified date range
        queryset = User.objects.filter(
            ~models.Q(id__in=DriverUnavailablePeriod.objects.filter(
                start_date__lte=end_date,
                end_date__gte=start_date
            ).values('driver')),role = 'Driver'
        )
        
        if location_type and location_id:
            if location_type == 'village':
                queryset = queryset.filter(village__id=location_id)
            elif location_type == 'taluka':
                queryset = queryset.filter(taluka__id=location_id)
            elif location_type == 'district':
                queryset = queryset.filter(district__id=location_id)
            
        # Filter by price range
    


        # Exclude own vehicles
        if self.request.user.is_authenticated:
            queryset = queryset.exclude(pk=self.request.user.pk)
        
        return queryset
    
    def list(self, request, *args, **kwargs):
        """
        Override list method to customize the response format.
        """
        driver = self.get_queryset()
        serializer = self.get_serializer(driver, many=True)
        return Response(serializer.data)


        
#############################complaint count###################
from member.models import ComplaintModel
from member.serializers import ComplaintSerializer
from rest_framework.pagination import PageNumberPagination
from rest_framework import generics
from rest_framework.response import Response
from datetime import timedelta, datetime
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend



class ComplaintCount(APIView):
    
    def get(self, request):
        Total= ComplaintModel.objects.count()
        return response({"success": True, "total": Total})
    

class ComplaintsPagination(PageNumberPagination):
    """Custom pagination for complaints"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100



class AllComplaintsListView(generics.ListAPIView):
    """
    API view to list all complaints in the system (Admin only).
    
    GET: Returns list of all complaints with advanced filtering options
    """
    
    serializer_class = ComplaintSerializer
    permission_classes = [IsAdminUser]
    pagination_class = ComplaintsPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    # Filter fields
    filterset_fields = ['status', 'priority', 'category', 'is_resolved', 'user']
    
    # Search fields
    search_fields = ['title', 'description', 'complaint_id', 'user__username', 'user__email']
    
    # Ordering fields
    ordering_fields = ['created_at', 'updated_at', 'priority', 'status']
    ordering = ['created_at']
    
    def get_queryset(self):
        """
        Get all complaints with advanced filtering options
        """
        queryset = ComplaintModel.objects.all()
        
        # Additional custom filters
        user_id = self.request.query_params.get('user_id', None)
        status_filter = self.request.query_params.get('status', None)
        priority_filter = self.request.query_params.get('priority', None)
        category_filter = self.request.query_params.get('category', None)
        is_resolved = self.request.query_params.get('is_resolved', None)
        date_from = self.request.query_params.get('date_from', None)
        date_to = self.request.query_params.get('date_to', None)
        days_old = self.request.query_params.get('days_old', None)
        
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        if status_filter:
            queryset = queryset.filter(status__iexact=status_filter)
        
        if priority_filter:
            queryset = queryset.filter(priority__iexact=priority_filter)
        
        if category_filter:
            queryset = queryset.filter(category__iexact=category_filter)
        
        if is_resolved is not None:
            queryset = queryset.filter(is_resolved=is_resolved.lower() == 'true')
        
        # Date range filtering
        if date_from:
            try:
                date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
                queryset = queryset.filter(created_at__date__gte=date_from_obj)
            except ValueError:
                pass
        
        if date_to:
            try:
                date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
                queryset = queryset.filter(created_at__date__lte=date_to_obj)
            except ValueError:
                pass
        
        # Filter by complaints older than specified days
        if days_old:
            try:
                days_old_int = int(days_old)
                cutoff_date = datetime.now().date() - timedelta(days=days_old_int)
                queryset = queryset.filter(created_at__date__lte=cutoff_date)
            except ValueError:
                pass
        
        return queryset.select_related('user', 'category').prefetch_related('attachments')
    
    def list(self, request, *args, **kwargs):
        """
        List all complaints with custom response format and statistics
        """
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        
        # Generate statistics
        total_complaints = queryset.count()
        resolved_complaints = queryset.filter(is_resolved=True).count()
        pending_complaints = queryset.filter(is_resolved=False).count()
        high_priority = queryset.filter(priority='high').count()
        
        statistics = {
            "total_complaints": total_complaints,
            "resolved_complaints": resolved_complaints,
            "pending_complaints": pending_complaints,
            "high_priority_complaints": high_priority,
            "resolution_rate": f"{(resolved_complaints/total_complaints*100):.1f}%" if total_complaints > 0 else "0%"
        }
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            paginated_response = self.get_paginated_response(serializer.data)
            
            return Response({
                "message": "All complaints retrieved successfully",
                "statistics": statistics,
                "results": paginated_response.data,
            }, status=status.HTTP_200_OK)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "message": "All complaints retrieved successfully",
            "statistics": statistics,
            "data": serializer.data,
        }, status=status.HTTP_200_OK)


class ComplaintDetailView(generics.RetrieveAPIView):
    """
    API view to retrieve details of a specific complaint.
    
    GET: Returns details of a specific complaint
    """
    
    queryset = ComplaintModel.objects.all()
    serializer_class = ComplaintSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'pk'
    
    def get_queryset(self):
        """
        Filter complaints based on user permissions
        """
        user = self.request.user
        if user.is_staff or user.is_superuser:
            # Admin can see all complaints
            return ComplaintModel.objects.all()
        else:
            # Regular users can only see their own complaints
            return ComplaintModel.objects.filter(user=user)
    
    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve complaint details with custom response
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        
        return Response({
            "message": "Complaint details retrieved successfully",
            "data": serializer.data,
        }, status=status.HTTP_200_OK)



"""
API Endpoints and Usage:

1. Get user's own complaints:
   GET /api/complaints/my-complaints/
   
   With filters:
   GET /api/complaints/my-complaints/?status=pending&priority=high&page=1&page_size=10
   GET /api/complaints/my-complaints/?search=billing&ordering=-created_at
   GET /api/complaints/my-complaints/?date_from=2024-01-01&date_to=2024-12-31
   GET /api/complaints/my-complaints/?is_resolved=false&category=technical

2. Get all complaints (Admin only):
   GET /api/complaints/all/
   
   With filters:
   GET /api/complaints/all/?user_id=123&status=resolved&priority=medium
   GET /api/complaints/all/?search=john&days_old=30
   GET /api/complaints/all/?category=billing&is_resolved=true

3. Get specific complaint details:
   GET /api/complaints/123/

Available Filters:
- status: pending, in_progress, resolved, closed
- priority: low, medium, high, urgent
- category: technical, billing, general, feature_request
- is_resolved: true, false
- date_from: YYYY-MM-DD format
- date_to: YYYY-MM-DD format
- days_old: number of days (for admin only)
- user_id: specific user ID (for admin only)
- search: searches in title, description, complaint_id, username, email
- ordering: created_at, -created_at, updated_at, -updated_at, priority, status
- page: page number for pagination
- page_size: number of items per page (max 100)

Response Format:
{
    "message": "Success message",
    "total_complaints": 150,
    "statistics": {  // Only for admin endpoint
        "total_complaints": 150,
        "resolved_complaints": 120,
        "pending_complaints": 30,
        "high_priority_complaints": 25,
        "resolution_rate": "80.0%"
    },
    "results": {  // Paginated response
        "count": 150,
        "next": "http://api/complaints/my-complaints/?page=2",
        "previous": null,
        "results": [...]
    }
}
"""

from member.serializers import VehicleBookingSerializer

class AllBookingsAPIView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        bookings = VehicleBooking.objects.select_related('user', 'vehicle').all().order_by('-created_at')
        serializer = VehicleBookingSerializer(bookings, many=True)
        return Response({"success": True, "data": serializer.data})