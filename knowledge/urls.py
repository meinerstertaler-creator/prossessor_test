from django.urls import path
from .views import (
    analyse_text_create,
    analyse_text_delete,
    analyse_text_edit,
    analyse_text_list,
)

app_name = "knowledge"

urlpatterns = [
    path("analyse-texte/", analyse_text_list, name="analyse_text_list"),
    path("analyse-texte/neu/", analyse_text_create, name="analyse_text_create"),
    path("analyse-texte/<int:pk>/bearbeiten/", analyse_text_edit, name="analyse_text_edit"),
    path("analyse-texte/<int:pk>/loeschen/", analyse_text_delete, name="analyse_text_delete"),
]