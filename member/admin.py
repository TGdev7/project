from django.contrib import admin
from member.models import *
from users.models import DistrictModel,TalukaModel,VillageModel

# admin.site.register(varasadhar_details)
# admin.site.register(bank_details)
# admin.site.register(farm_details)
admin.site.register(DistrictModel)
admin.site.register(TalukaModel)
admin.site.register(VillageModel)
# admin.site.register(VehicleBooking)
# admin.site.register(instrument)
# admin.site.register(Rating)
# admin.site.register(ComplaintDropDownModel)
# admin.site.register(complaintModel)
