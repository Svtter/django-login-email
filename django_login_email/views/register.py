from typing import Callable

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from django_login_email import forms, models, token

from .utils import transform_timestamp


def save_token(token_dict):
  """When generate new token, should call this method."""
  try:
    models.EmailLogin.objects.filter(email=token["email"]).update(
      sault=token["salt"],
      expired_time=transform_timestamp(token["expired_time"]),
    )
  except models.EmailLogin.DoesNotExist:
    models.EmailLogin.objects.create(
      email=token["email"],
      sault=token["salt"],
      expired_time=transform_timestamp(token["expired_time"]),
    )


def send_email():
  gen = token.TokenGenerator(10)
  token_str = gen.gen("svtter@163.com", save_token)
  print(token_str)


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
        return render(request, post_template, {"form": form})
      else:
        return render(request, post_template, {"form": form})

  return register
