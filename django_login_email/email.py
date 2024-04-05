import typing as t
import string

from django.core.mail import EmailMessage
from django.contrib.auth import get_user_model

from django.contrib.auth import login, logout
from . import token


class EmailLoginInfo(object):
    subject: str
    message: str
    welcome_text = "Welcome to meterhub! Please click the link below to login.<br>"
    url: str = "http://127.0.0.1:8000/account/verify?token="
    login_message: string.Template = string.Template('Click <a href="$url$token">Link</a>')
    from_email: str

    def __init__(self) -> None:
        self.set_variables()

    def set_variables(self):
        raise NotImplementedError("You must set the subject and from_email.")

    def set_token(self, value):
        self.message = self.welcome_text + self.login_message.substitute(url=self.url, token=value)


class TimeLimit(object):
    minutes: int = 10


class EmailInfoMixin(TimeLimit):
    email_info_class: t.Type[EmailLoginInfo]

    def check_user(self, email):
        User = get_user_model()
        u = User.objects.get(email=email)
        return u

    def send_login_mail(self, email: str):
        self.check_user(email)
        e = self.email_info_class()
        m = token.TokenManager(self.minutes)

        token_v = m.encrypt_mail(email)
        e.set_token(token_v)

        msg = EmailMessage(e.subject, e.message, e.from_email, [email])
        msg.content_subtype = "html"
        msg.send()


class EmailValidateMixin(TimeLimit):
    def verify_login_mail(self, request, token_v: str):
        m = token.TokenManager(self.minutes)
        emailAndSalt = m.decrypt_token(token=token_v)
        token_d = m.check_token(emailAndSalt)
        if token_d is None:
            raise Exception("Invalid token.")

        User = get_user_model()
        u = User.objects.get(email=m.get_mail(token_d))
        if not u.is_active:
            raise Exception("Inactive user, disallow login.")

        login(request, u)


class EmailLogoutMixin(object):
    def logout(self, request):
        logout(request)
