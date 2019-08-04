from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("cart/addorder/", views.addorder, name="addorder"),
    path("cart/deleteorder/", views.deleteorder, name="deleteorder"),
]
