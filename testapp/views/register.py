from django_login_email import forms
from django_login_email.views import register


def example_register(request):
  fn = register.use_register(
    get_template="login_email/register.html",
    post_template="login_email/register_success.html",
  )
  return fn(request)


def example_verify(request):
  fn = register.use_verify(details="login_email/register_details.html")
  return fn(request)


def example_register_details(request):
  fn = register.use_register_details(
    details="login_email/register_details.html",
    register_form=forms.RegisterDetails,
  )
  return fn(request)
