from django.shortcuts import render
from django_login_email import views as v
from django_login_email import email as e

# Create your views here.


class MyInfo(e.EmailLoginInfo):
    def set_variables(self):
        self.subject = "Login request from meterhub"
        self.message = "If you request to login, <br>"
        self.from_email = "admin@sunpraise.com"


class LoginView(v.EmailLoginView):
    email_info_class: MyInfo


class VerifyView(v.EmailVerifyView):
    pass


class LogoutView(v.EmailLogoutView):
    pass
