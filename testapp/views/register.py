from django.views import render

from django_login_email.views import use_register


def example_register(request):
  fn = use_register(
    get_template="login_email/register.html", post_template="login_email/register.html"
  )
  return fn(request)
