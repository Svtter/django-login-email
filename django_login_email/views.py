import datetime
from typing import Any
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.generic.edit import FormView
from django.views.generic import TemplateView
from django.contrib.auth import get_user_model
from . import forms
from . import email
from . import models

# Create your views here.


class TimeLimit(email.TimeLimit):
    minutes = 10


class MailRecordModelMixin(email.EmailInfoMixin):
    """Here is an example for MailRecord, using django model. You could implement yourself."""

    def set_mail_record(self, mail: str):
        models.EmailLogin.set_email_last_time(mail, datetime.datetime.now(tz=datetime.timezone.utc))

    def reset_mail(self, mail: str):
        # models.EmailLogin.objects.filter(email=mail).delete()
        e = models.EmailLogin.objects.get(email=mail)
        e.last_time = e.last_time - datetime.timedelta(minutes=self.tl.minutes)
        e.save()

    def get_mail_record(self, mail: str) -> email.MailRecord:
        # for easy to change. use a function.
        try:
            e = models.EmailLogin.objects.get(email=mail)
        except models.EmailLogin.DoesNotExist:
            return email.MailRecord(email=mail, last_time=None)
        return email.MailRecord(email=e.email, last_time=e.last_time)


class EmailLoginView(FormView, MailRecordModelMixin):
    template_name = "login_email/login.html"
    form_class = forms.LoginForm
    email_info_class = email.EmailLoginInfo
    tl = TimeLimit()

    def form_valid(self, form):
        """check the email"""
        User = get_user_model()
        try:
            self.send_login_mail(form.cleaned_data["email"])
        except User.DoesNotExist as e:
            # ignore user missing problem.
            print(e, form.cleaned_data["email"])
            return render(self.request, "login_email/success.html", {"form": form})
        except Exception as e:
            # raise Exception(e)
            print(e)
            return render(self.request, "login_email/error.html", {"error": e})
        return render(self.request, "login_email/success.html", {"form": form})


class EmailVerifyView(TemplateView, email.EmailValidateMixin):
    tl = TimeLimit()

    def post(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        raise Http404("Invalid Request.")

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        token = request.GET.get("token", None)
        if token is None:
            raise Http404("Invalid Request")
        try:
            self.verify_login_mail(request=request, token_v=token)
        except Exception as e:
            # TODO: log the error
            print(e)
            raise Http404("Invalid Request")
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse("home")


class EmailLogoutView(TemplateView, email.EmailLogoutMixin):
    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        self.logout(request=request)
        return redirect("login")


class HomeView(TemplateView):
    template_name = "login_email/home.html"

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if not self.request.user.is_anonymous and self.request.user.is_authenticated:
            return super().get(request, *args, **kwargs)
        else:
            return redirect("login")
