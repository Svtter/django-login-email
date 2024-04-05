import pytest
import datetime
from django_login_email import models
from django_login_email.email import EmailInfoMixin, MailRecord, TimeLimit


class MyTimeLit(TimeLimit):
    minutes = 10


class Mixin(EmailInfoMixin):
    tl = MyTimeLit()

    def get_mail_record(self, mail: str) -> MailRecord:
        r1 = MailRecord(
            email="svtter@163.com",
            last_time=datetime.datetime.now(tz=datetime.timezone.utc) - datetime.timedelta(minutes=10),
        )
        # r2 = MailRecord(email="svtter@163.com", last_time=datetime.datetime.now(tz=datetime.timezone.utc))
        return r1

    def set_mail_record(self, mail: str):
        pass


@pytest.mark.django_db
def test_mixin():
    mail = "svtter@163.com"
    e = Mixin()
    re = e.get_mail_record(mail)
    assert re.last_time
    # assert re.last_time + datetime.timedelta(minutes=10) <= datetime.datetime.now(tz=datetime.timezone.utc)
    assert e.check_could_send(email=mail)


class Mixin2(EmailInfoMixin):
    tl = MyTimeLit()

    def get_mail_record(self, mail: str) -> MailRecord:
        r2 = MailRecord(email="svtter@163.com", last_time=None)
        return r2

    def set_mail_record(self, mail: str):
        pass


def test_none_of_mixin():
    mail = "svtter@163.com"
    e = Mixin2()
    re = e.get_mail_record(mail=mail)
    assert re.last_time is None
