from django.urls import path

from . import views

urlpatterns = [
    path("", views.reports_home, name="reports_home"),
    path("processing/", views.processing_report, name="processing_report"),
    path("audits/", views.procedure_audit_report_list, name="procedure_audit_report_list"),
    path("audits/<int:pk>/", views.procedure_audit_report, name="procedure_audit_report"),
]