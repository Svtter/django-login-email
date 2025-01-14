# Create your views here.
import logging
from typing import Any

from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import TemplateView

from django_login_email import email

from . import limit
from .login import EmailLoginView  # noqa
from .mixin import MailRecordModelMixin
from .register import use_register  # noqa

logger = logging.getLogger(__name__)


class EmailVerifyView(TemplateView, email.EmailValidateMixin, MailRecordModelMixin):
  """verify token in url"""

  tl = limit.LoginTimeLimit()

  def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
    token = request.GET.get("token", None)
    if token is None:
      raise Http404("Invalid Request")
    try:
      self.verify_login_mail(request=request, token_v=token)
    except Exception as e:
      logger.error(e)
      raise Http404("Invalid Request")
    return redirect(self.get_success_url())

  def get_success_url(self):
    return reverse("login_email:home")


class EmailLogoutView(TemplateView, email.EmailLogoutMixin):
  def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
    self.logout(request=request)
    return redirect("login_email:login")


class HomeView(TemplateView):
  template_name = "login_email/home.html"

  def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
    if not self.request.user.is_anonymous and self.request.user.is_authenticated:
      return super().get(request, *args, **kwargs)
    else:
      return redirect("login")
