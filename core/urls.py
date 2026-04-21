from django.urls import path
from .views import dashboard, set_active_tenant

app_name = "core"

urlpatterns = [
    path("", dashboard, name="dashboard"),
    path("set-active-tenant/", set_active_tenant, name="set_active_tenant"),
]