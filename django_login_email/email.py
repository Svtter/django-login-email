from dataclasses import dataclass
import typing as t
import abc
import string
import datetime
from datetime import timezone

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


@dataclass
class MailRecord(object):
    last_time: t.Optional[datetime.datetime]
    email: str


class MailRecordMixin(abc.ABC):

    @abc.abstractmethod
    def get_mail_record(self, mail: str) -> MailRecord:
        # for easy to change. use a function.
        raise NotImplementedError("You must implement get_mail_record")


class SaltSaver(abc.ABC):
    """How to save token?"""

    @abc.abstractmethod
    def save_token(self, token_str: token.TokenDict):
        """to save token in the database or somewhere."""
        raise NotImplementedError("You must implement save_token")

    @abc.abstractmethod
    def get_salt(self, email: str) -> str:
        raise NotImplementedError("You must implement get_token")


class EmailInfoMixin(MailRecordMixin, SaltSaver):
    email_info_class: t.Type[EmailLoginInfo]

    tl: TimeLimit

    def check_user(self, email):
        User = get_user_model()
        u = User.objects.get(email=email)
        return u

    def check_could_send(self, email):
        re = self.get_mail_record(email)
        # TODO: if other user send email, the current user could not sign in.
        if (re.last_time is None) or (
            re.last_time + datetime.timedelta(minutes=self.tl.minutes) <= datetime.datetime.now(tz=timezone.utc)
        ):
            return True
        return False

    def send_valid(self, email: str):
        e = self.email_info_class()
        m = token.TokenManager(self.tl.minutes)

        encrypt_token = m.encrypt_mail(email, self.save_token)
        e.set_token(encrypt_token)

        msg = EmailMessage(e.subject, e.message, e.from_email, [email])
        msg.content_subtype = "html"
        msg.send()

    def send_login_mail(self, email: str):
        self.check_user(email)
        if not self.check_could_send(email=email):
            raise Exception(f"Cannot send. Wait {self.tl.minutes} minutes.")

        self.send_valid(email)


class EmailValidateMixin(SaltSaver):
    tl: TimeLimit

    def verify_login_mail(self, request, token_v: str):
        m = token.TokenManager(self.tl.minutes)
        token_str = m.decrypt_token(token=token_v)
        token_d = m.check_token(token_str, self.get_salt)
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
