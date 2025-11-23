# Create your views here.
import logging
from typing import Any

from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views.generic.edit import FormView

from django_login_email import email, errors, forms, iputils

from . import limit
from .mixin import MailRecordModelMixin

logger = logging.getLogger(__name__)


class MyEmailLoginInfo(email.EmailLoginInfo):
  def __init__(self):
    super().__init__()
    self.from_email = settings.EMAIL_HOST_USER


class EmailLoginView(FormView, MailRecordModelMixin, iputils.IPBanUtils):
  """process login by email"""

  template_name = "login_email/login.html"
  error_template: str = "login_email/error.html"
  success_template: str = "login_email/success.html"

  form_class = forms.LoginForm

  login_info_class = MyEmailLoginInfo
  register_info_class = email.EmailRegisterInfo

  tl = limit.LoginTimeLimit()

  def get(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
    if self.request.user.is_authenticated:
      return redirect("home")
    return super().get(request, *args, **kwargs)

  def form_valid(self, form):
    """check the email"""

    if self.is_ip_banned(self.get_client_ip(self.request)):
      return render(self.request, self.error_template, {"error": "Your IP is banned."})

    # Not allow to login if the user is already authenticated.
    if self.request.user.is_authenticated:
      return redirect("home")

    # Record the send attempt and check if rate limit is exceeded (before sending email)
    if not self.record_send(self.request):
      logger.warning(f"IP rate limit exceeded for {self.get_client_ip(self.request)}")
      return render(
        self.request,
        self.error_template,
        {"error": "Too many requests. Please try again later."},
      )

    try:
      # send login mail. If user not exist, send register mail.
      self.send_login_mail(form.cleaned_data["email"])
    except errors.RateLimitError as e:
      logger.warning(f"Rate limit exceeded: {e}")
      return render(self.request, self.error_template, {"error": e})
    except errors.EmailSendError as e:
      logger.error(f"Email sending failed: {e}")
      return render(
        self.request,
        self.error_template,
        {"error": "Failed to send email. Please try again later."},
      )
    except ValueError as e:
      logger.error(f"Invalid mail type: {e}")
      return render(
        self.request, self.error_template, {"error": "Internal error occurred."}
      )
    return render(self.request, self.success_template, {"form": form})
