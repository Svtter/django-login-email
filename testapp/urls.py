from django.urls import path

from . import views as v

app_name = "login_email"

urlpatterns = [
  path("login", v.LoginView.as_view(), name="login"),
  path("verify", v.VerifyView.as_view(), name="verify"),
  path("logout", v.LogoutView.as_view(), name="logout"),
]
