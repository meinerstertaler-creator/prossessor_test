from django.urls import path
from .views import dpia_detail, dpia_delete_risk, dpia_delete_measure

app_name = "dpia"

urlpatterns = [
    path("processing/<int:processing_id>/", dpia_detail, name="dpia_detail"),
    path("risk/<int:pk>/delete/", dpia_delete_risk, name="dpia_delete_risk"),
    path("measure/<int:pk>/delete/", dpia_delete_measure, name="dpia_delete_measure"),
]