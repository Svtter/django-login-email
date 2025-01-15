from django_login_email.email import EmailLoginInfo

sample_system_name = "My System"


class MyLoginInfo(EmailLoginInfo):
  system_name = sample_system_name


def test_custom_system_name():
  e = MyLoginInfo()
  assert (
    e.subject == f"Welcome to {sample_system_name}! Please click the link below to login."
  )
  assert e.from_email == "noreply@example.com"
