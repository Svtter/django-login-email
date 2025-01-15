from django.contrib.auth import get_user_model


def test_email_mixin(db, mx_send):
  mr = mx_send.get_mail_record("svtter@163.com")
  assert mr.expired_time is None


def test_is_send(db, mx_send):
  is_call = False

  def fake_fn(*arg, **kwargs):
    nonlocal is_call
    is_call = True

  mx_send.save_token = fake_fn
  mx_send.send_valid("svtter@163.com", "login")

  assert is_call


def test_send_valid(db, mx_send):
  mx_send.send_valid("svtter@163.com", "login")

  # check mail record
  mr = mx_send.get_mail_record("svtter@163.com")
  assert mr.expired_time is not None
  assert mr.validated is False


def test_user_exist(db, mx_send):
  User = get_user_model()
  User.objects.create_user(username="svtter", email="svtter@163.com", password="123456")

  mx_send.send_valid("svtter@163.com", "login")
  mr = mx_send.get_mail_record("svtter@163.com")
  assert mr.validated is False
