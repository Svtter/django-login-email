from django_login_email.email import EmailLoginInfo

system_name = "My System"


class MyLoginInfo(EmailLoginInfo):
  def init_variables(self):
    self.subject = f"Welcome to {system_name}! Please click the link below to login."
    self.from_email = "svtter@163.com"


def test_custom_system_name():
  e = MyLoginInfo()
  e.init_variables()
  assert e.subject == f"Welcome to {system_name}! Please click the link below to login."
  assert e.from_email == "svtter@163.com"
