# member/urls.py
from django.urls import path
from member import views
from .views import (
    FarmDetailsListCreateAPIView,
    FarmDetailsRUDAPIView,
    FarmDetailsUpdateCurrentAPIView,
    BankDetailListCreateAPIView,   # NEW
    BankDetailRUDAPIView           # NEW
)
from .views import (
    VarasadharListCreateView,
    VarasadharRetrieveUpdateDestroyView
)

from .views import ComplaintCreateView, UserComplaintsListView
from member.views import ComplaintCreateView, UserComplaintsListView, ComplaintUpdateView, ComplaintDeleteView, MemberBookingDropdownAPIView
from .views import RatingCreationAPIView
from .views import MemberBookingListView, MemberEditAPIView

urlpatterns = [

    #path("",views..as_view(),name=)   

    #############New vehicle list and booking##################
    path('vehicles/', views.VehicleListView.as_view(), name='vehicle-list'),
    path('bookings/', views.VehicleBookingListCreateAPIView.as_view(), name='booking-list-create'),
    path('bookings/<int:booking_id>/', views.VehicleBookingDetailAPIView.as_view(), name='booking-detail'),
    path('bookings/<int:booking_id>/cancel/', views.CancelBookingAPIView.as_view(), name='cancel-booking'),

    # ----------------------------------------
    #  Registration / profile
    # ----------------------------------------
    path("member-registration-update/", views.MemberRegistrationUpdate.as_view(),
         name="member-registration"),

    path('varasadhar/', VarasadharListCreateView.as_view(), name='varasadhar-list'),
    path('varasadhar/<int:pk>/', VarasadharRetrieveUpdateDestroyView.as_view(), name='varasadhar-detail'),

    # ----------------------------------------
    #  BANK DETAIL CRUD  (matches React)
    # ----------------------------------------
    path("banks/",           BankDetailListCreateAPIView.as_view(),
         name="bank-list-create"),
    path("banks/<int:pk>/",  BankDetailRUDAPIView.as_view(),
         name="bank-rud"),

    # ----------------------------------------
    #  FARM DETAILS
    # ----------------------------------------
    path("farm-details/",           FarmDetailsListCreateAPIView.as_view(),
         name="farm-details"),
    path("farm-details/<int:pk>/",  FarmDetailsRUDAPIView.as_view(),
         name="farm-details-detail"),
    path("farm-details-update/",    FarmDetailsUpdateCurrentAPIView.as_view(),
         name="farm-details-update-current"),

    # ----------------------------------------
    #  Login & look‑ups
    # ----------------------------------------
    path("user-login-view/",              views.UserLoginView.as_view(),
         name="user-login"),

    path("Search-Vendor-Using-Village/",  views.SearchVendorUsingVillage.as_view(),
         name="search-vendor"),

    # ----------------------------------------
    #  Vendor & vehicle
    # ----------------------------------------
    path("vendor-list/",views.VendorVehicleInfo.as_view(),name="vendor-list"),
    path("vehicle-detail/<int:pk>/", views.VehicleDetail.as_view(), name="vehicle-detail"),
    path("vehicle-booking-creation/", views.VehicleBookingListCreateAPIView.as_view(),
         name="vehicle-booking-create"),
    path("display-charges/",         views.DisplayCharges.as_view(),
         name="display-charges"), 

    # ----------------------------------------
    #  Booking & complaint dashboards
    # ----------------------------------------
    path("login-user-booking-rating-list/", views.LoginUserBookingRatingList.as_view(),
         name="login-user-booking"),
    path("login-user-complaint-list/", views.UserComplaintsListView.as_view(),
         name="login-user-complaints"),
    path("all-my-booking-dashboard/", views.AllMyBookingDashboard.as_view(),
         name="all-my-bookings"),

    # ----------------------------------------
    #  Instruments & dropdowns
    # ----------------------------------------
    path("instrument-list/",           views.InstrumentList.as_view(),
         name="instrument-list"),


    path("complaints/create/", ComplaintCreateView.as_view(), name="create-complaint"),
    path("complaints/list/", UserComplaintsListView.as_view(), name="list-complaints"),
    path("complaints/update/<int:pk>/", ComplaintUpdateView.as_view()),
    path("complaints/delete/<int:pk>/", ComplaintDeleteView.as_view()),
    path("complaints/bookings-dropdown/", MemberBookingDropdownAPIView.as_view(), name="bookings-dropdown"),



    path('ratings/', RatingCreationAPIView.as_view(), name='member-ratings'),

    # ----------------------------------------
    #  Misc
    # ----------------------------------------
     path("profile/", views.MemberUserProfileView.as_view(),
         name="profile"),
     path("member-edit-profile/",    views.MemberEditAPIView.as_view(),
         name="member-edit-profile"),

     path("member-bookings/", MemberBookingListView.as_view(), name="member-bookings"),

 
    
]
