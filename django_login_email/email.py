import typing as t

from django.core.mail import EmailMessage
from django.contrib.auth import get_user_model

from django.contrib.auth import login
from . import token


class EmailLoginInfo(object):
    subject: str
    message: str
    url = "http://127.0.0.1:8000/account/verify?token="
    login_message: str = '<a href="{url}{token}"></a>'
    from_email: str

    def __init__(self) -> None:
        self.set_variables()

    def set_variables(self):
        raise NotImplementedError("You must set the subject and from_email.")

    def set_token(self, value):
        self.login_message.format(url=self.url, token=value)


class EmailInfoMixin(object):
    email_info_class: t.Type[EmailLoginInfo]

    def check_user(self, email):
        User = get_user_model()
        u = User.objects.get(email=email)
        return u

    def send_login_mail(self, email: str):
        self.check_user(email)
        e = self.email_info_class()
        m = token.TokenManager()

        token_v = m.encrypt_mail(email)
        e.set_token(token_v)

        msg = EmailMessage(e.subject, e.message, e.from_email, [email])
        msg.content_subtype = "html"
        msg.send()


class EmailValidateMixin(object):
    def verify_login_mail(self, request, token_v: str):
        m = token.TokenManager()
        emailAndSalt = m.decrypt_token(token=token_v)
        if not m.check_salt(emailAndSalt):
            raise Exception("Invalid salt")

        User = get_user_model()
        u = User.objects.get(email=m.get_mail(emailAndSalt))
        if not u.is_active:
            raise Exception("Inactive user, disallow login.")

        login(request, u)
