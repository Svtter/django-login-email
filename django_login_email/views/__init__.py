import datetime

# Create your views here.
import logging
from typing import Any

from django.contrib.auth import get_user_model
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.generic import TemplateView
from django.views.generic.edit import FormView

from django_login_email import email, forms

from .mixin import MailRecordModelMixin
from .register import use_register  # noqa

logger = logging.getLogger(__name__)


class TimeLimit(email.TimeLimit):
  minutes = 10


class EmailLoginView(FormView, MailRecordModelMixin):
  template_name = "login_email/login.html"
  form_class = forms.LoginForm
  email_info_class = email.EmailLoginInfo
  tl = TimeLimit()

  def get(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
    if self.request.user.is_authenticated:
      return redirect("home")
    return super().get(request, *args, **kwargs)

  def form_valid(self, form):
    """check the email"""

    # Not allow to login if the user is already authenticated.
    if self.request.user.is_authenticated:
      return redirect("home")

    User = get_user_model()
    try:
      self.send_login_mail(form.cleaned_data["email"])
    except User.DoesNotExist:
      # ignore user missing problem.
      logger.warning(f"user {form.cleaned_data['email']} does not exist")
      return render(self.request, "login_email/success.html", {"form": form})
    except Exception as e:
      logger.error(e)
      return render(self.request, "login_email/error.html", {"error": e})
    return render(self.request, "login_email/success.html", {"form": form})


class EmailVerifyView(TemplateView, email.EmailValidateMixin, MailRecordModelMixin):
  tl = TimeLimit()

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
      return redirect("login_email:login")
