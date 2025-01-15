import datetime

import pytest

from django_login_email.email import EmailInfoMixin, MailRecord, TimeLimit
from django_login_email.token import TokenDict

sample_mail = "svtter@163.com"


class MyTimeLit(TimeLimit):
  minutes = 10


class Mixin(EmailInfoMixin):
  tl = MyTimeLit()

  def get_mail_record(self, mail: str) -> MailRecord:
    r1 = MailRecord(
      email=sample_mail,
      expired_time=datetime.datetime.now(tz=datetime.timezone.utc)
      - datetime.timedelta(minutes=10),
      validated=False,
      sault="",
    )
    return r1

  def save_token(self, token: TokenDict):
    pass

  def disable_mail(self, mail: str):
    pass

  def disable_token(self, token: TokenDict):
    pass


@pytest.mark.django_db
def test_mixin():
  e = Mixin()
  re = e.get_mail_record(sample_mail)
  assert re.expired_time
  assert e.check_could_send(email=sample_mail)


class Mixin2(EmailInfoMixin):
  tl = MyTimeLit()

  def get_mail_record(self, mail: str) -> MailRecord:
    r2 = MailRecord(
      email="svtter@163.com", expired_time=None, validated=False, sault=""
    )
    return r2

  def save_token(self, token: TokenDict):
    pass

  def disable_token(self, token: TokenDict):
    pass


def test_none_of_mixin():
  mail = "svtter@163.com"
  e = Mixin2()
  re = e.get_mail_record(mail=mail)
  assert re.expired_time is None
