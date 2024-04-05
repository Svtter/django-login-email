from typing import Any
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.generic.edit import FormView
from django.views.generic import TemplateView
from django.contrib.auth import get_user_model
from . import forms
from . import email
from . import token

# Create your views here.

m = token.TokenManager()


class EmailLoginView(FormView, email.EmailInfoMixin):
    template_name = "login_email/login.html"
    form_class = forms.LoginForm
    email_info_class = email.EmailLoginInfo

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
            print(e)
            return render(self.request, "login_email/error.html", {"error": e})
        return render(self.request, "login_email/success.html", {"form": form})


class EmailVerifyView(TemplateView, email.EmailValidateMixin):
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
