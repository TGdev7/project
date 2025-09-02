from django.urls import path
from django.urls import include
from admin_panel import views
from .views import First100MembersView, AssignGatAdhikariView
from .views import AllBookingsAPIView

urlpatterns = [
    path('login/', views.AdminUserLoginView.as_view(),name="dashboard-details") ,
    ################ Dashboard ###########################
    path("Village/count/", views.VillageCountView.as_view(), name="Village_count"),
    path("district/count/", views.DistrictCountView.as_view(), name="district_count"),
    path("taluka/count/", views.TalukaCountView.as_view(), name="taluka_count"),

    
    #################  District #############################
    path("district-list/", views.GetDistrictListView.as_view(), name="district_list"),
    path("create-district/",views.CreateDistrictView.as_view(),name="create_disrtict"),
    path("<int:pk>/update-district/",views.UpdateDistrictView.as_view(),name="update_district"),
    path("<int:pk>/delete-district/",views.DeleteDistrictView.as_view(),name="delete_district"),

    #################  Taluka #############################
    path("taluka-list/", views.GetTalukaListView.as_view(), name="taluka_list"),
    path("create-taluka/",views.CreateTalukaView.as_view(),name="create_taluka"),
    path("<int:pk>/update-taluka/",views.UpdateTalukaView.as_view(),name="update_taluka"),
    path("<int:pk>/delete-taluka/",views.DeleteTalukaView.as_view(),name="delete_taluka"),

    #################  Village #############################
    path("Village-list/", views.GetVillageListView.as_view(), name="Village_list"),
    path("create-Village/",views.CreateVillageView.as_view(),name="create_Village"),
    path("<int:pk>/update-Village/",views.UpdateVillageView.as_view(),name="update_Village"),
    path("<int:pk>/delete-Village/",views.DeleteVillageView.as_view(),name="delete_Village"),

     #################  count #############################
    path("DriverCount/", views.DriverCountView.as_view(), name="DriverCount"),
    path("MemberCount/",views.MemberCountView.as_view(),name="MemberCount"),
    path("VendorCount/",views.VendorCountView.as_view(),name="VendorCount"),

    #################  serch and assign #############################
    path("Search-Driver/",views.SearchDriverUsingVillage.as_view(),name="Serchdriver"),
    #path("Assign=driver/",views.AssignUserDriverToBookingView.as_view(),name="AssignDriver"),
    
    
    # All complaints (Admin only)
    path('complaints/all/', views.AllComplaintsListView.as_view(), name='all-complaints-list'),
    
    # Complaint details
    path('complaints/<int:pk>/', views.ComplaintDetailView.as_view(), name='complaint-detail'),

    path("first-100-members/", First100MembersView.as_view(), name="first-100-members"),
    path("assign-gat-adhikari/", AssignGatAdhikariView.as_view(), name="assign-gat-adhikari"),

    path('all-bookings/', AllBookingsAPIView.as_view(), name='admin-all-bookings'),
    
]
