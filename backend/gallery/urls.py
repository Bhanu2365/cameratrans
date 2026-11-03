from django.urls import path
from . import views

urlpatterns = [
    path("batches/", views.batches),
    path("batches/<uuid:batch_id>/", views.batch_detail),
    path("batches/<uuid:batch_id>/close/", views.close_batch),
    path("photos/<int:photo_id>/download/", views.download_photo),
    path("photos/<int:photo_id>/preview/", views.preview_photo),
    path("photos/<int:photo_id>/framed/", views.framed_photo),
    path("network-info/", views.network_info),
]
