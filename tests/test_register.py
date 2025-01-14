from django_login_email.views.register import is_registered


def test_is_registered(db):
  assert is_registered("svtter@163.com")
