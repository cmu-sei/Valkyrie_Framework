from . import views
from django.urls import path
from .views import WhoisApiView, MappingApiView, StatsApiView, LogsApiView
from drf_yasg import openapi
from rest_framework import permissions
from drf_yasg.views import get_schema_view

schema_view = get_schema_view(
    openapi.Info(
        title="IP Maven API",
        default_version='v1',
        description="Test description",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@ipmaven.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)
urlpatterns = [
    path('', views.home, name='home'),
    path('help', views.help, name='help'),
    path('about', views.about, name='about'),
    path('configure', views.configure, name='configure'),
    path('mappings/', views.mappings, name='mappings'),
    path('whois/', views.whois, name='whois'),
    path('whois/<str:detail>/', views.detail, name='detail'),
    path('configure/', views.configure, name='configure'),
    path('upload_log_file/', views.upload_log_file, name='upload_log_file'),

    # API (JSON)# L)
    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    path('api/whois/', WhoisApiView.as_view(), name='api_whois'),
    path('api/mappings/', MappingApiView.as_view(), name='api_mappings'),
    path('api/stats/', StatsApiView.as_view(), name='stats_mappings'),
    path('api/logs/', LogsApiView.as_view(), name='logs_mappings'),
]
