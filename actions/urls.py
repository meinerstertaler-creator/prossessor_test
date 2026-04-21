from django.urls import path
from . import views

urlpatterns = [
    path("", views.action_list, name="action_list"),
    path("create/", views.action_create, name="action_create"),
    path("<int:pk>/", views.action_detail, name="action_detail"),
    path("<int:pk>/edit/", views.action_edit, name="action_edit"),
    path(
        "generate-from-legal/<int:pk>/",
        views.generate_actions_from_legal_assessment_view,
        name="generate_actions_from_legal",
),
]