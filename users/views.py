#from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserLoginSerializer
from rest_framework import generics
from users.models import *
from users import serializers as user_serializers
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny

from users.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings


class MemberUserRegisterview(generics.CreateAPIView):
    permission_classes = [AllowAny]
    queryset = User.objects.all()
    serializer_class = user_serializers.MemberUserRegisterSerializer

    def get_serializer_context(self,*args,**kwargs):

        return {
            "request":self.request,
            "args":self.args,
            "kwargs":self.kwargs
        }

class VendorUserRegisterview(generics.CreateAPIView):
    permission_classes = [AllowAny]
    queryset = User.objects.all()
    serializer_class = user_serializers.VendorUserRegisterSerializer

    def get_serializer_context(self,*args,**kwargs):

        return {
            "request":self.request,
            "args":self.args,
            "kwargs":self.kwargs
        }

class DriverUserRegisterview(generics.CreateAPIView):
    permission_classes = [AllowAny]
    queryset = User.objects.all()
    serializer_class = user_serializers.DriverUserRegisterSerializer

    def get_serializer_context(self,*args,**kwargs):

        return {
            "request":self.request,
            "args":self.args,
            "kwargs":self.kwargs
        }

class UserLoginView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        role = request.data.get('role')  # Member, Vendor, Driver

        # Validate input
        if not email or not password or not role:
            return Response({'success': False, 'message': 'email, password, and role are required'}, status=400)

        # Enforce valid role
        valid_roles = ['Member', 'Vendor', 'Driver', 'Gat_Adhikari']
        if role not in valid_roles:
            return Response({'success': False, 'message': 'Invalid role'}, status=400)

        # Get user by email & role
        user = User.objects.filter(email__iexact=email, role=role).first()

        if not user or not user.check_password(password):
            return Response({'success': False, 'message': 'Invalid credentials'}, status=401)

        if not user.is_active:
            return Response({'success': False, 'message': 'User is deactivated'}, status=403)

        # Generate tokens
        refresh = RefreshToken.for_user(user)
        access = refresh.access_token

        token_data = {
            'refresh': str(refresh),
            'access': str(access),
        }
        response = Response({
            'success': True,
            'message': 'Successfully Logged In!',
            'data':  {
                'user_id': user.id,
                'email': user.email,
                'role': user.role
            },
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
        

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet  
from .serializers import *
class UserLocationViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserLocationSerializer
    
    @action(detail=True, methods=['post'])
    def update_coordinates(self, request, pk=None):
        """Manually trigger coordinate update"""
        user = self.get_object()
        force = request.data.get('force', False)
        
        success, message = user.update_coordinates(force=force)
        
        if success:
            serializer = self.get_serializer(user)
            return Response({
                'success': True,
                'message': message,
                'data': serializer.data
            })
        
        return Response({
            'success': False,
            'message': message
        }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def set_manual_coordinates(self, request, pk=None):
        """Set coordinates manually"""
        user = self.get_object()
        
        try:
            latitude = request.data['latitude']
            longitude = request.data['longitude']
        except KeyError as e:
            return Response({
                'success': False,
                'message': f'Missing required field: {e}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        success, message = user.set_manual_coordinates(latitude, longitude)
        
        if success:
            serializer = self.get_serializer(user)
            return Response({
                'success': True,
                'message': message,
                'data': serializer.data
            })
        
        return Response({
            'success': False,
            'message': message
        }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def reset_auto_geocoding(self, request, pk=None):
        """Reset to automatic geocoding"""
        user = self.get_object()
        success, message = user.reset_to_auto_geocoding()
        
        serializer = self.get_serializer(user)
        return Response({
            'success': success,
            'message': message,
            'data': serializer.data
        })
    
    @action(detail=True, methods=['get'])
    def nearby_users(self, request, pk=None):
        """Get nearby users within specified radius"""
        user = self.get_object()
        radius = float(request.query_params.get('radius', 10))  # Default 10km
        
        if not user.has_coordinates:
            return Response({
                'success': False,
                'message': 'User coordinates not available'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        nearby_users = user.get_nearby_users(radius_km=radius)
        serializer = self.get_serializer(nearby_users, many=True)
        
        return Response({
            'success': True,
            'count': len(nearby_users),
            'radius_km': radius,
            'users': serializer.data
        })
