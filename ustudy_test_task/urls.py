from django.contrib import admin
from django.urls import path, include, re_path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions


# Schema view for API documentation
schema_view = get_schema_view(
    openapi.Info(
        title="Ustudy Test TaskModel API",
        default_version='v1',
        description="API for AralHub Restaurant Booking System",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@aralhub.local"),
        license=openapi.License(name="BSD License"),
    ),
    # url='https://niagara.aralhub.uz/',
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # API schema
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    # Include your users URLs
    path('users/', include('users.urls')),

    path('tasks/', include('tasks.urls')),
]
