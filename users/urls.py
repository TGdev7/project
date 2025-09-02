
from django.urls import path
from .views import (MemberUserRegisterview, VendorUserRegisterview, DriverUserRegisterview)
from users.views import UserLoginView
from users import views

urlpatterns = [
    path('member/user-register/', views.MemberUserRegisterview.as_view(), name='member_register'),
    path('vendor/user-register/', views.VendorUserRegisterview.as_view(), name='vendor_register'),
    path('driver/user-register/', views.DriverUserRegisterview.as_view(), name='driver_register'),
    path('login/', UserLoginView.as_view(), name='user-login')
]
