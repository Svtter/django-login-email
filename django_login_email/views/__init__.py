# Create your views here.
import logging
from typing import Any

from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.generic import TemplateView

from django_login_email import email, errors

from . import limit
from .login import EmailLoginView  # noqa
from .mixin import MailRecordModelMixin

logger = logging.getLogger(__name__)


class EmailVerifyView(TemplateView, email.EmailVerifyMixin, MailRecordModelMixin):
  """verify token in url"""

  tl = limit.LoginTimeLimit()
  error_template: str = "login_email/error.html"

  def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
    token = request.GET.get("token", None)
    if token is None:
      raise Http404("Invalid Request")
    try:
      self.verify_login_mail(request=request, token_v=token)
    except errors.ValidatedError as e:
      return render(self.request, self.error_template, {"error": e})
    except errors.TokenError as e:
      logger.error(f"Token error: {e}")
      return render(
        self.request, self.error_template, {"error": "Invalid or expired token."}
      )
    except errors.InactiveUserError as e:
      logger.warning(f"Inactive user attempted login: {e}")
      return render(
        self.request, self.error_template, {"error": "Your account is inactive."}
      )
    except (ValueError, KeyError) as e:
      logger.error(f"Token decryption/parsing error: {e}")
      raise Http404("Invalid Request")
    return redirect(self.get_success_url())

  def get_success_url(self):
    return reverse("login_email:home")


class EmailLogoutView(TemplateView, email.EmailLogoutMixin):
  login_url: str = "login_email:login"

  def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
    self.logout(request=request)
    return redirect(self.login_url)


class HomeView(TemplateView):
  template_name = "login_email/home.html"

  def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
    if not self.request.user.is_anonymous and self.request.user.is_authenticated:
      return super().get(request, *args, **kwargs)
    else:
      return redirect("login_email:login")
