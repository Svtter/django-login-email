from django.shortcuts import render

from django_login_email import email as e
from django_login_email import views as v

from .register import example_register as register  # noqa

# Create your views here.


class MyInfo(e.EmailLoginInfo):
  def init_variables(self):
    self.subject = "Login request from meterhub"
    self.welcome_text = "Welcome to meterhub! Please click the link below to login.<br>"
    self.from_email = "sandbox.smtp.mailtrap.io"


class LoginView(v.EmailLoginView):
  email_info_class = MyInfo


class VerifyView(v.EmailVerifyView):
  pass


class LogoutView(v.EmailLogoutView):
  pass
