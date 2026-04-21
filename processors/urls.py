from django.urls import path
from . import views

urlpatterns = [
    path("", views.processor_list, name="processor_list"),
    path("create/", views.processor_create, name="processor_create"),
    path("<int:pk>/", views.processor_detail, name="processor_detail"),
    path("<int:pk>/edit/", views.processor_edit, name="processor_edit"),
]