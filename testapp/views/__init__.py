from django.shortcuts import render

from django_login_email import email as e
from django_login_email import views as v

# Create your views here.

loginInfo, registerInfo = e.get_info_class("meterhub")


class LoginView(v.EmailLoginView):
  login_info_class = loginInfo
  register_info_class = registerInfo


class VerifyView(v.EmailVerifyView):
  pass


class LogoutView(v.EmailLogoutView):
  pass
