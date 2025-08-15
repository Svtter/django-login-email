from django_login_email import email


class MyLoginInfo(email.EmailLoginInfo):
  system_name = "meterhub"


def test_email_info():
  e = MyLoginInfo()
  e.build_message("1234567890")
  assert (
    e.message
    == """Welcome to meterhub! Please click the link below to login.<br>Click <a href="http://127.0.0.1:8000/account/verify?token=1234567890">Link</a>"""
  )
