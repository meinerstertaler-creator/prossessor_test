from django.urls import path
from .views import legal_assessment_upsert

app_name = "legal"

urlpatterns = [
    path(
        "processing/<int:processing_id>/assessment/",
        legal_assessment_upsert,
        name="legal_assessment_edit",
    ),
]