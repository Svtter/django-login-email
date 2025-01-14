from typing import Callable

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from django_login_email import forms


def send_email():
  pass


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
