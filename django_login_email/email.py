import abc
import datetime
import string
import typing as t
from dataclasses import dataclass
from datetime import timezone

from django.contrib.auth import get_user_model, login, logout
from django.core.mail import EmailMessage

from . import errors, token


class EmailInfo(object):
  """Email info."""

  subject: str
  message: str
  from_email: str
  welcome_text: str
  system_name: str

  url: str = "http://127.0.0.1:8000/account/verify?token="
  login_message: string.Template = string.Template('Click <a href="$url$token">Link</a>')

  def set_token(self, value):
    self.message = self.welcome_text + self.login_message.substitute(
      url=self.url, token=value
    )


class EmailLoginInfo(EmailInfo):
  """Email info for login."""

  def __init__(self):
    self.subject = f"Welcome to {self.system_name}! Please click the link below to login."
    self.from_email = "noreply@example.com"
    self.welcome_text: str = (
      f"Welcome to {self.system_name}! Please click the link below to login.<br>"
    )


class EmailRegisterInfo(EmailInfo):
  """Email info for register."""

  def __init__(self):
    self.subject = (
      f"Welcome to {self.system_name}! Please click the link below to register."
    )
    self.from_email = "noreply@example.com"
    self.welcome_text: str = (
      f"Welcome to {self.system_name}! Please click the link below to register.<br>"
    )


def get_info_class(sys_name: str) -> t.Tuple[EmailLoginInfo, EmailRegisterInfo]:
  class MyLoginInfo(EmailLoginInfo):
    system_name = sys_name

  class MyRegisterInfo(EmailRegisterInfo):
    system_name = sys_name

  return MyLoginInfo, MyRegisterInfo


@dataclass
class TimeLimit(object):
  minutes: int = 10


@dataclass
class MailRecord(object):
  expired_time: t.Optional[datetime.datetime]
  email: str
  validated: bool
  sault: str


class MailRecordAPI(abc.ABC):
  """Mixin to get mail record."""

  @abc.abstractmethod
  def get_mail_record(self, mail: str) -> MailRecord:
    """Get the mail record from the database."""
    raise NotImplementedError("You must implement get_mail_record")

  @abc.abstractmethod
  def save_token(self, token: token.TokenDict):
    """to save token in the database or somewhere."""
    raise NotImplementedError("You must implement save_token")

  @abc.abstractmethod
  def disable_token(self, token: token.TokenDict):
    """Every token should only login once"""
    raise NotImplementedError("")


class EmailFunc(MailRecordAPI):
  """Mixin to send email."""

  login_info_class: t.Type[EmailLoginInfo]
  register_info_class: t.Type[EmailRegisterInfo]

  tl: TimeLimit

  def check_user(self, email) -> bool:
    """check if the user exists."""
    User = get_user_model()
    u = User.objects.filter(email=email)
    return u.exists()

  def check_could_send(self, email) -> bool:
    """check if the email could send."""
    re = self.get_mail_record(email)
    # TODO: if other user send email, the current user could not sign in.
    if (re.expired_time is None) or (
      re.expired_time <= datetime.datetime.now(tz=timezone.utc)
    ):
      return True
    return False

  def get_token_manager(self) -> token.TokenManager:
    return token.TokenManager(self.tl.minutes)

  def send_valid(self, email: str, mail_type: str):
    """send login/register mail."""
    if mail_type == "login":
      e = self.login_info_class()
    elif mail_type == "register":
      e = self.register_info_class()
    else:
      raise ValueError(f"Invalid mail type: {mail_type}")

    m = self.get_token_manager()
    encrypt_token = m.encrypt_mail(email, mail_type, self.save_token)
    e.set_token(encrypt_token)

    msg = EmailMessage(e.subject, e.message, e.from_email, [email])
    msg.content_subtype = "html"
    msg.send()

  def send_login_mail(self, email: str):
    """
    send login mail.
    """
    # if user not exist, send register mail.
    if not self.check_user(email):
      mail_type = "register"
    else:
      mail_type = "login"

    # if the email could not send, raise exception.
    if not self.check_could_send(email=email):
      raise Exception(f"Cannot send. Wait {self.tl.minutes} minutes.")

    self.send_valid(email, mail_type)


class EmailVerifyMixin(MailRecordAPI):
  """verify the token in url"""

  tl: TimeLimit

  def verify_token(self, token_v: str):
    m = token.TokenManager(self.tl.minutes)
    token_str = m.decrypt_token(token=token_v)
    token_d = m.transform_token(token_str)

    mr = self.get_mail_record(m.get_mail(token_d))
    if mr.validated:
      raise errors.ValidatedError("Token already validated.")

    token_d = m.check_token(token_d, lambda: mr.sault)
    if token_d is None:
      raise errors.TokenError("Invalid token.")

    User = get_user_model()
    u = User.objects.filter(email=m.get_mail(token_d)).first()
    if not u:
      # if user not exist, create a new user.
      # support register by email.
      u = User.objects.create(username=m.get_mail(token_d), email=m.get_mail(token_d))

    if not u.is_active:
      raise Exception("Inactive user, disallow login.")

    self.disable_token(token=token_d)
    return u

  def verify_login_mail(self, request, token_v: str):
    """
    verify the login mail.
    if user not exist, create a new user.
    """
    u = self.verify_token(token_v=token_v)
    login(request, u)


class EmailLogoutMixin(object):
  def logout(self, request):
    logout(request)
