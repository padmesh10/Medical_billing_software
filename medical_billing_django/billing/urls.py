from django.urls import path
from . import views

app_name = "billing"
urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("claim/<int:claim_id>/", views.claim_detail, name="claim_detail"),
    path("eob/<int:eob_id>/", views.eob_detail, name="eob_detail"),
    path("notes/add/", views.add_note, name="add_note"),
    path("claim/<int:claim_id>/status/", views.update_claim_status, name="update_claim_status"),
]
