from django import forms
from django.contrib.auth import get_user_model

from . import register


class LoginForm(forms.Form):
  """Just check the login request."""

  email = forms.EmailField(label="email")


class RegisterForm(forms.Form):
  """Just check the register request."""

  email = forms.EmailField(label="email")

  def is_valid(self) -> bool:
    res = super().is_valid()
    if register.is_registered(self.cleaned_data["email"]):
      self.add_error("email", "User already registered.")
      return False
    return res


class RegisterDetails(forms.Form):
  """Just check the register details."""

  email = forms.EmailField(label="email")
  user = forms.CharField(label="user")

  def save(self):
    """save with is_active=True."""
    User = get_user_model()
    u = User(email=self.cleaned_data["email"], username=self.cleaned_data["user"])
    u.is_active = True
    u.save()
