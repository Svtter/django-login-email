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
  try:
    models.EmailRegister.objects.filter(email=token_dict["email"]).update(
      sault=token_dict["salt"],
      expired_time=utils.transform_timestamp(token_dict["expired_time"]),
    )
  except models.EmailRegister.DoesNotExist:
    models.EmailRegister.objects.create(
      email=token_dict["email"],
      sault=token_dict["salt"],
      expired_time=utils.transform_timestamp(token_dict["expired_time"]),
    )


class MailSender(object):
  def __init__(self):
    self.token_manager = token.TokenManager(time_limit)

  def gen_mail_message(self, token_str: str, email: str) -> EmailMessage:
    return EmailMessage(
      subject="Meterhub Register",
      body=f"Click <a href='http://127.0.0.1:8000/account/verify?token={token_str}'>Link</a>",
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

  def disable_token(self, token_d: dict):
    """disable the token."""
    models.EmailRegister.objects.filter(email=token_d["email"]).update(
      validated=True,
      expired_time=utils.transform_timestamp(token_d["expired_time"]),
    )

  def validate_register_email(self, token_v: str) -> User:
    """validate the register details."""
    m = token.TokenManager(time_limit)
    token_str = m.decrypt_token(token=token_v)
    token_d = m.transform_token(token_str)

    mr = get_mail_record(token_d)
    if mr.validated:
      raise Exception("Already validated.")

    token_d = m.check_token(token_d, lambda: mr.sault)
    if token_d is None:
      raise Exception("Invalid token.")

    self.disable_token(token=token_d)
    u = User.objects.filter(email=token_d["email"])
    if u.exists():
      return u.first()
    else:
      u = User.objects.create_user(
        username=token_d["email"],  # using email as username.
        email=token_d["email"],
        is_active=False,
      )
      return u


def verify_register_token(
  success_url: str = "login_email:register_details",
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
        return redirect(success_url)
      except Exception as e:
        return HttpResponse(status=404, content=str(e))

  return verify_token


def register_details(
  details: str = "login_email/register_details.html",
  register_form=forms.RegisterDetails,
) -> HttpResponse:
  tv = TokenValidator()

  def fn(request: HttpRequest) -> HttpResponse:
    """validate the register details."""
    if request.method == "GET":
      try:
        if request.user.is_authenticated and not request.user.is_active:
          return render(request, details, {"form": register_form()})
        else:
          return HttpResponse(status=404, content="Invalid token.")
      except Exception as e:
        messages.error(request, str(e))
        return render(request, details, {"form": register_form()})

    elif request.method == "POST":
      form = register_form(request.POST)
      if form.is_valid():
        tv.validate_register_email(form.cleaned_data["token"])
        form.save()
        return render(request, details, {"form": form})
      else:
        return render(request, details, {"form": form})

  return fn
