from django.contrib import admin, messages
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from django.contrib.admin.sites import AlreadyRegistered, NotRegistered
from django.db import transaction

User = get_user_model()

# In case another app already registered User, unregister it first
try:
    admin.site.unregister(User)
except NotRegistered:
    pass


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Custom admin list:

    • Shows the first 100 Members plus the current Gat_Adhikari
    • Lets the super-admin promote exactly ONE member to Gat_Adhikari at a time
    """

    # ------------------------------------------------------------------
    #  Table & filters
    # ------------------------------------------------------------------
    list_display  = ("id", "email", "role", "first_name", "last_name", "created_at", "is_active")
    list_filter   = ("role", "is_active")          # <-- (un-commented role filter)
    search_fields = ("email", "first_name", "last_name")
    ordering      = ("id",)
    actions       = ["make_gatadhikari", "remove_gatadhikari"]

    # ------------------------------------------------------------------
    #  Detail / add forms  (your originals)
    # ------------------------------------------------------------------
    fieldsets = (
        (_("Personal Info"), {
            "fields": (
                "first_name", "last_name", "mobile", "email", "password",
                "adhar_no", "pan_no", "dob", "city", "state", "country",
                "zipcode", "address", "house_or_building", "road_or_area",
                "landmark", "role",
            )
        }),
        (_("Permissions"), {"fields": ("is_admin", "is_staff", "is_active", "groups")}),
        (_("Important dates"), {"fields": ("last_login", "created_at")}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "password1", "password2"),
        }),
    )

    filter_horizontal = ("groups",)
    readonly_fields   = ("created_at",)

    # ------------------------------------------------------------------
    #  Limit changelist → first 100 Members + current Gat_Adhikari
    # ------------------------------------------------------------------
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        members = qs.filter(role="Member").order_by("id")[:100]
        try:
            gat = qs.get(role="Gat_Adhikari")
            return members | qs.filter(pk=gat.pk)   # ensures Gat_Adhikari always shows
        except User.DoesNotExist:
            return members

    # ------------------------------------------------------------------
    #  Bulk actions
    # ------------------------------------------------------------------
    @admin.action(description="Set selected member as Gatadhikari (Group Admin)")
    def make_gatadhikari(self, request, queryset):
        if queryset.count() != 1:
            self.message_user(request, "Select exactly ONE member.", level=messages.ERROR)
            return

        member = queryset.first()
        if member.role != "Member":
            self.message_user(request, "Selected user is not a Member.", level=messages.ERROR)
            return

        with transaction.atomic():
            # Demote any existing Gatadhikari
            User.objects.filter(role="Gat_Adhikari").update(role="Member")
            # Promote chosen member
            member.role = "Gat_Adhikari"
            member.save(update_fields=["role"])

        self.message_user(request, f"{member.email} is now Gatadhikari!", level=messages.SUCCESS)

    @admin.action(description="Remove Gatadhikari role")
    def remove_gatadhikari(self, request, queryset):
        updated = queryset.filter(role="Gat_Adhikari").update(role="Member")
        if updated:
            self.message_user(request, "Gatadhikari role removed.", level=messages.SUCCESS)
        else:
            self.message_user(request, "No Gatadhikari selected.", level=messages.WARNING)

