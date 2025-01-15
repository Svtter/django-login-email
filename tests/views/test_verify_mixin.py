import pytest
from django.contrib.auth import get_user_model

from django_login_email import email, token
from django_login_email.views import mixin


class MyVerify(email.EmailVerifyMixin, mixin.MailRecordModelMixin):
  tl = email.TimeLimit(10)


@pytest.fixture
def mx_verify():
  return MyVerify()


def wrap_token_manager(mx_send):
  token_b = None

  class TokenManager(token.TokenManager):
    def encrypt_mail(self, *args, **kwargs):
      nonlocal token_b
      token_b = super().encrypt_mail(*args, **kwargs)
      return token_b

  def get_token_manager():
    return TokenManager(10)

  def get_token_b():
    return token_b

  mx_send.get_token_manager = get_token_manager
  return get_token_b


def test_verify(db, mx_send, mx_verify):
  """test token validate"""
  # no user
  get_token_b = wrap_token_manager(mx_send)
  mx_send.send_valid("svtter@163.com", "login")

  u = mx_verify.verify_token(get_token_b())
  assert u.email == "svtter@163.com"


def test_has_user(db, mx_send, mx_verify):
  # exist user
  User = get_user_model()
  User.objects.create(email="svtter@163.com", password="123456")

  # verify token
  get_token_b = wrap_token_manager(mx_send)
  mx_send.send_valid("svtter@163.com", "login")
  mx_verify.verify_token(get_token_b())

  mr = mx_send.get_mail_record("svtter@163.com")
  assert mr.validated

  assert User.objects.filter(email="svtter@163.com").exists()
