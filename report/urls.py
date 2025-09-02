from django.urls import path
from report.views import *

urlpatterns = [
   
    path("district-report/", DistrictReportView.as_view(), name="district-report"),
    path("taluka-report/", TalukaReportView.as_view(), name="district-report"),
    path("village-report/", VillageReportView.as_view(), name="district-report"),
    path("user-report/", UserReportView.as_view(), name="district-report"),

]


