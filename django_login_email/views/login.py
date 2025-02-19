# Create your views here.
import logging
from typing import Any

from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views.generic.edit import FormView

from django_login_email import email, forms, iputils

from . import limit
from .mixin import MailRecordModelMixin

logger = logging.getLogger(__name__)


class EmailLoginView(FormView, MailRecordModelMixin, iputils.IPBanUtils):
  """process login by email"""

  template_name = "login_email/login.html"
  error_template: str = "login_email/error.html"
  success_template: str = "login_email/success.html"

  form_class = forms.LoginForm

  login_info_class = email.EmailLoginInfo
  register_info_class = email.EmailRegisterInfo

  tl = limit.LoginTimeLimit()

  def get(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
    if self.request.user.is_authenticated:
      return redirect("home")
    return super().get(request, *args, **kwargs)

  def form_valid(self, form):
    """check the email"""

    if self.is_ip_banned(self.get_client_ip()):
      return render(self.request, self.error_template, {"error": "Your IP is banned."})

    # Not allow to login if the user is already authenticated.
    if self.request.user.is_authenticated:
      return redirect("home")

    try:
      # send login mail. If user not exist, send register mail.
      self.send_login_mail(form.cleaned_data["email"])
      self.record_send(self.request)
    except Exception as e:
      logger.error(e)
      return render(self.request, self.error_template, {"error": e})
    return render(self.request, self.success_template, {"form": form})
