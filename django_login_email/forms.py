from django import forms


class LoginForm(forms.Form):
  """Just check the login request."""

  email = forms.EmailField(label="email")


class RegisterForm(forms.Form):
  """Just check the register request."""

  email = forms.EmailField(label="email")
