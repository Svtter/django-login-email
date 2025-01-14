# Create your views here.
import logging
from typing import Any

from django.contrib.auth import get_user_model
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views.generic.edit import FormView

from django_login_email import email, forms

from . import limit
from .mixin import MailRecordModelMixin

logger = logging.getLogger(__name__)


class EmailLoginView(FormView, MailRecordModelMixin):
  """process login by email"""

  template_name = "login_email/login.html"
  form_class = forms.LoginForm
  email_info_class = email.EmailLoginInfo
  tl = limit.LoginTimeLimit()

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
