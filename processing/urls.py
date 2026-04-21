from django.urls import path

from . import views

urlpatterns = [
    path("", views.processing_list, name="processing_list"),
    path("create/", views.processing_create, name="processing_create"),
    path("<int:pk>/", views.processing_detail, name="processing_detail"),
    path("<int:pk>/edit/", views.processing_edit, name="processing_edit"),
    path("<int:pk>/archive/", views.processing_archive, name="processing_archive"),
    path("<int:pk>/reactivate/", views.processing_reactivate, name="processing_reactivate"),
    path(
        "<int:pk>/mark-third-party-requested/",
        views.processing_mark_third_party_requested,
        name="processing_mark_third_party_requested",
    ),
]