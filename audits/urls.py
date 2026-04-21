from django.urls import path

from . import views

urlpatterns = [
    path("", views.audit_dashboard, name="audit_dashboard"),

    path("procedure/", views.procedure_audit_list, name="procedure_audit_list"),
    path("procedure/create/", views.procedure_audit_create, name="procedure_audit_create"),
    path("procedure/<int:pk>/", views.procedure_audit_detail, name="procedure_audit_detail"),
    path("procedure/<int:pk>/edit/", views.procedure_audit_edit, name="procedure_audit_edit"),

    path("procedure/<int:pk>/items/", views.procedure_audit_items, name="procedure_audit_items"),
    path("procedure/<int:pk>/items/complete/", views.procedure_audit_items_complete, name="procedure_audit_items_complete"),
    path("procedure/<int:pk>/items/final-complete/", views.procedure_review_final_complete, name="procedure_review_final_complete"),

    path("procedure/<int:pk>/new-activities/", views.procedure_audit_new_activities, name="procedure_audit_new_activities"),
    path("procedure/<int:pk>/new-activities/create/", views.procedure_audit_new_activity_create, name="procedure_audit_new_activity_create"),
    path("procedure/<int:pk>/new-activities/complete/", views.procedure_audit_new_activities_complete, name="procedure_audit_new_activities_complete"),

    path("procedure/<int:pk>/checklist/", views.procedure_audit_checklist, name="procedure_audit_checklist"),
    path("procedure/<int:pk>/checklist/complete/", views.procedure_audit_checklist_complete, name="procedure_audit_checklist_complete"),

    path("procedure/<int:pk>/preliminary-complete/", views.procedure_audit_preliminary_complete, name="procedure_audit_preliminary_complete"),
    path("procedure/<int:pk>/final-complete/", views.procedure_audit_final_complete, name="procedure_audit_final_complete"),

    path("special/", views.audit_list, name="audit_list"),
    path("special/create/", views.audit_create, name="audit_create"),
    path("special/<int:pk>/", views.audit_detail, name="audit_detail"),
    path("special/<int:pk>/edit/", views.audit_edit, name="audit_edit"),
    path("special/<int:pk>/responses/", views.audit_responses, name="audit_responses"),
    path("special/<int:pk>/create-actions/", views.create_actions_from_audit, name="create_actions_from_audit"),
]