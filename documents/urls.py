from django.urls import path

from . import views

urlpatterns = [
    path("", views.document_list, name="document_list"),
    path("upload/", views.document_upload, name="document_upload"),
    path("from-template/", views.document_create_from_template, name="document_create_from_template"),
    path("upload/folder/create/", views.document_folder_create, name="document_folder_create"),
    path("upload/label/create/", views.document_label_create, name="document_label_create"),
    path("<int:pk>/download/", views.document_download, name="document_download"),
    path("<int:pk>/edit/", views.document_edit, name="document_edit"),
]