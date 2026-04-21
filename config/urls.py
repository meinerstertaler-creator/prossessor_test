from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    path("", RedirectView.as_view(url="/core/", permanent=False), name="home"),

    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),

    path("core/", include("core.urls")),
    path("processing/", include("processing.urls")),
    path("legal/", include("legal.urls")),
    path("knowledge/", include("knowledge.urls")),
    path("dpia/", include("dpia.urls")),

    path("actions/", include("actions.urls")),
    path("audits/", include("audits.urls")),
    path("documents/", include("documents.urls")),
    path("processors/", include("processors.urls")),
    path("reports/", include("reports.urls")),
]