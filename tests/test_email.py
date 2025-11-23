import datetime

import pytest

from django_login_email.email import EmailFunc, MailRecord, TimeLimit
from django_login_email.token import TokenDict

sample_mail = "svtter@163.com"


class MyTimeLit(TimeLimit):
  minutes = 10


class Mixin(EmailFunc):
  tl = MyTimeLit()

  def get_mail_record(self, mail: str) -> MailRecord:
    r1 = MailRecord(
      email=sample_mail,
      expired_time=datetime.datetime.now(tz=datetime.timezone.utc)
      - datetime.timedelta(minutes=10),
      validated=False,
      salt="",
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


class Mixin2(EmailFunc):
  tl = MyTimeLit()

  def get_mail_record(self, mail: str) -> MailRecord:
    r2 = MailRecord(email=sample_mail, expired_time=None, validated=False, salt="")
    return r2

  def save_token(self, token: TokenDict):
    pass

  def disable_token(self, token: TokenDict):
    pass


def test_none_of_mixin():
  e = Mixin2()
  re = e.get_mail_record(sample_mail)
  assert re.expired_time is None
  assert e.check_could_send(email=sample_mail)
