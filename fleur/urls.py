# fleur/urls.py
from django.urls import path
from . import views, api_views

urlpatterns = [
    path("", views.home, name="home"),
    path("bouquets/", views.bouquets_list, name="bouquets_list"),
    path("order/<int:slot_id>/create/", views.create_order, name="create_order"),
    path("payment/<int:order_id>/", views.payment_page, name="payment_page"),

    # API
    path("api/bill-acceptor/credit/", api_views.bill_credit_view, name="bill_credit"),
    path("api/orders/<int:order_id>/status/", api_views.order_status_view, name="order_status"),
    path("test-doors/", views.test_doors_view, name="test_doors"),

]
