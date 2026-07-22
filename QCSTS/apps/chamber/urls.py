from django.urls import path
from apps.chamber import views

urlpatterns = [
    path("", views.ChamberInventoryView.as_view(), name="chamber-inventory"),
    path("pulls/", views.SamplePullListCreateView.as_view(), name="sample-pull-list-create"),
    path("move/", views.ChangeBatchLocationView.as_view(), name="change-location"),
    path("locations/<uuid:pk>/", views.LocationHistoryView.as_view(), name="location-history"),
]
