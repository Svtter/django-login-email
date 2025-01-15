import pytest

from django_login_email import email
from django_login_email.views import mixin

loginInfo, registerInfo = email.get_info_class("system")


class MixinTest(mixin.MailRecordModelMixin):
  login_info_class = loginInfo
  register_info_class = registerInfo
  tl = email.TimeLimit()


@pytest.fixture
def mx_send():
  return MixinTest()
