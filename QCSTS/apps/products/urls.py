from django.urls import path
from apps.products import views

urlpatterns = [
    # Monographs
    path("monographs/", views.MonographListCreateView.as_view(), name="monograph-list-create"),
    path("monographs/<uuid:pk>/", views.MonographDetailView.as_view(), name="monograph-detail"),
    path(
        "monographs/<uuid:pk>/approve/",
        views.MonographApproveView.as_view(),
        name="monograph-approve",
    ),
    path(
        "monographs/<uuid:pk>/tests/",
        views.MonographTestListCreateView.as_view(),
        name="monograph-test-list-create",
    ),
    # Products
    path("", views.ProductListCreateView.as_view(), name="product-list-create"),
    path("<uuid:pk>/", views.ProductDetailView.as_view(), name="product-detail"),
]
