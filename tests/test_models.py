import datetime

import pytest

from django_login_email import models


@pytest.mark.django_db
def test_set_expired_time():
  now_t = datetime.datetime.now()
  e = models.EmailRecord.set_email_expired_time(email="svtter@163.com", datetime=now_t)
  assert models.EmailRecord.objects.get(email="svtter@163.com")

  now_t2 = datetime.datetime.now() + datetime.timedelta(minutes=10)
  e.set_expired_time(now_t2)
  assert e.expired_time == now_t2
