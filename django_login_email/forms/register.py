from django.contrib.auth import get_user_model


def is_registered(email: str) -> bool:
  """
  check if the user is already registered.
  If user is not active, return False.
  """
  User = get_user_model()
  u = User.objects.filter(email=email)
  if u.exists():
    user = u.first()
    if user.is_active:
      return True
  return False
