import logging
from typing import Callable

from django.contrib import messages
from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from django_login_email import forms, models, token

from . import utils

logger = logging.getLogger(__name__)
time_limit = 10


def save_token(token_dict: dict):
  """When generate new token, should call this method."""
  logger.info(f"save token: {token_dict}")
  models.EmailRegister.objects.update_or_create(
    email=token_dict["email"],
    defaults={
      "sault": token_dict["salt"],
      "expired_time": utils.transform_timestamp(token_dict["expired_time"]),
      "validated": False,
    },
  )


class MailSender(object):
  def __init__(self):
    self.token_manager = token.TokenManager(time_limit)

  def gen_mail_message(self, token_str: str, email: str) -> EmailMessage:
    return EmailMessage(
      subject="Meterhub Register",
      body=f"Click <a href='http://127.0.0.1:8000/account/register/verify?token={token_str}'>Link</a>",
      from_email="noreply@example.com",
      to=[email],
    )

  def send_email(self, email: str) -> str:
    url = self.token_manager.encrypt_mail(email, save_token)
    mail = self.gen_mail_message(url, email)
    mail.send()
    return url


def use_register(
  get_template: str,
  post_template: str,
) -> Callable[[HttpRequest], HttpResponse]:
  """generate a email register function."""

  def register(request: HttpRequest) -> HttpResponse:
    if request.method == "GET":
      return render(request, get_template, {"form": forms.RegisterForm()})

    elif request.method == "POST":
      form = forms.RegisterForm(request.POST)
      if form.is_valid():
        logger.info(f"{request.path} post register form, {form.cleaned_data}")
        ms = MailSender()
        ms.send_email(form.cleaned_data["email"])
        return render(request, post_template, {"form": form})
      else:
        return render(request, post_template, {"form": form})

  return register


def get_mail_record(token_d: dict):
  """get the mail record."""
  return models.EmailRegister.objects.get(email=token_d["email"])


class TokenValidator(object):
  """Token validator."""

  def __init__(self):
    self.token_manager = token.TokenManager(time_limit)

  def disable_token(self, token_d: dict):
    """disable the token."""
    models.EmailRegister.objects.filter(email=token_d["email"]).update(
      validated=True,
      expired_time=utils.transform_timestamp(token_d["expired_time"]),
    )

  def validate_register_email(self, token_v: str) -> User:
    """validate the register details."""
    token_str = self.token_manager.decrypt_token(token=token_v)
    token_d = self.token_manager.transform_token(token_str)

    mr = get_mail_record(token_d)
    if mr.validated:
      raise Exception("Token already validated.")

    token_d = self.token_manager.check_token(token_d, lambda: mr.sault)
    if token_d is None:
      raise Exception("Invalid token.")

    self.disable_token(token_d=token_d)
    u = User.objects.filter(email=token_d["email"])
    if u.exists():
      raise Exception("User already exists.")

    u = User.objects.create_user(
      username=token_d["email"],  # using email as username.
      email=token_d["email"],
    )
    return u


def use_verify(
  success_url: str = "home",
) -> HttpResponse:
  """
  Verify the register token.
  If success, login the user and redirect to the register details page.
  """
  tv = TokenValidator()

  def verify_token(request: HttpRequest):
    if request.method == "GET":
      try:
        u = tv.validate_register_email(request.GET.get("token"))
        login(request, u)
        logger.info(f"user: {u.email} logined.")
        return redirect(success_url)

      except Exception as e:
        logger.error(f"verify token error: {e}")
        return HttpResponse(status=403, content=str(e))

  return verify_token
