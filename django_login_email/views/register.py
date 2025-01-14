import logging
from typing import Callable

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from django_login_email import forms, models, token

from . import utils

logger = logging.getLogger(__name__)


def save_token(token_dict):
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


def send_email(email: str) -> str:
  gen = token.TokenGenerator(10)
  token_str = gen.gen(email, save_token)
  return token_str


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
        return render(request, post_template, {"form": form})
      else:
        return render(request, post_template, {"form": form})

  return register
