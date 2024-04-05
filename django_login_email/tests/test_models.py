import pytest
import datetime
from django_login_email import models


@pytest.mark.django_db
def test_models_in_django():
    now_t = datetime.datetime.now()
    e = models.EmailLogin.set_email_last_time(email="svtter@163.com", datetime=now_t)
    assert models.EmailLogin.objects.get(email="svtter@163.com")

    now_t2 = datetime.datetime.now() + datetime.timedelta(minutes=10)
    e.set_last_time(now_t2)
    assert e.last_time == now_t2
