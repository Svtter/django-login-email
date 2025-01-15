import pytest
from django.contrib.auth import get_user_model

from django_login_email import email
from django_login_email.views import mixin

loginInfo, registerInfo = email.get_info_class("system")


class MixinTest(mixin.MailRecordModelMixin):
  login_info_class = loginInfo
  register_info_class = registerInfo
  tl = email.TimeLimit()


@pytest.fixture
def mx():
  return MixinTest()


def test_email_mixin(db, mx):
  mr = mx.get_mail_record("svtter@163.com")
  assert mr.expired_time is None


def test_is_send(db, mx):
  is_call = False

  def fake_fn(*arg, **kwargs):
    nonlocal is_call
    is_call = True

  mx.save_token = fake_fn
  mx.send_valid("svtter@163.com", "login")

  assert is_call


def test_send_valid(db, mx):
  mx.send_valid("svtter@163.com", "login")

  # check mail record
  mr = mx.get_mail_record("svtter@163.com")
  assert mr.expired_time is not None
  assert mr.validated is False


def test_user_exist(db, mx):
  User = get_user_model()
  User.objects.create_user(username="svtter", email="svtter@163.com", password="123456")

  mx.send_valid("svtter@163.com", "login")
  mr = mx.get_mail_record("svtter@163.com")
  assert mr.validated is False
