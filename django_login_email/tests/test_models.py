import datetime
from django_login_email import models


def test_models_in_django(live_server):
    now_t = datetime.datetime.now()
    e = models.EmailLogin.set_email_last_time(email="svtter@163.com", datetime=now_t)

    now_t2 = datetime.datetime.now() + datetime.timedelta(minutes=10)
    e.set_last_time(now_t2)

    assert e.is_send(email="svtter@163.com") == False
