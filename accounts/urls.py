from django.urls import path
from django.contrib.auth.views import LogoutView

from . import views

urlpatterns = [
    path("signup/", views.signup, name="signup"),
    path("login/", views.log_in, name="login"),
    path('logout/', LogoutView.as_view(), name='logout'),
]
