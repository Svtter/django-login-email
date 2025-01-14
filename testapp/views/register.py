from django_login_email.views import register


def example_register(request):
  fn = register.use_register(
    get_template="login_email/register.html",
    post_template="login_email/register_success.html",
  )
  return fn(request)


def example_verify(request):
  fn = register.use_verify(
    success_url="login_email:register_details",
  )
  return fn(request)


def example_register_details(request):
  fn = register.use_register_details(
    get_template="login_email/register_details.html",
    post_template="login_email/register_details_success.html",
  )
  return fn(request)
