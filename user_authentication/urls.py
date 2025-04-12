from django.urls import path
from . import views

urlpatterns = [
    path("register", views.RegisterView.as_view(), name="register"),
    path("login", views.LoginView.as_view(), name="login"),
    path("view_profile", views.ViewProfile.as_view(), name="view_profile"),
    path("update_profile", views.UpdateProfile.as_view(), name="update_profile"),
    path("change_password", views.ChangePassword.as_view(), name="change_password"),
    path("verify_email", views.VerifyEmail.as_view(), name="verify_email"),
]
