
from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.conf import settings # Import settings
from django.conf.urls.static import static 
from django.contrib.auth import views as auth_views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

# Swagger schema setup
schema_view = get_schema_view(
   openapi.Info(
      title="AwjarBank API",
      default_version='v1',
      description="API documentation for AwjarBank platform",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="support@awjarbank.com"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('admin_panel/', include("admin_panel.urls")),
    path('vendor/', include('vendor.urls')),
    path('users/', include('users.urls')),
    path('member/', include('member.urls')),
    path('driver/', include("driver.urls")),
    path('auto_assign/', include("auto_assign.urls")),

    path("report/", include("report.urls")),

    path('notifications/', include("notifications.urls")),


    path('password-reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),



    # 🔹 Swagger & Redoc
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('report/', include("report.urls")),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)