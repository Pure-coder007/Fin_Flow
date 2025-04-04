from django.urls import path
from . import views

urlpatterns = [
    path("register", views.RegisterView.as_view(), name="register"),
    path("login", views.LoginView.as_view(), name="login"),
    path("view_profile", views.ViewProfile.as_view(), name="view_profile"),
    
]
