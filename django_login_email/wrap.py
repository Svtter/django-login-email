from typing import Callable

from django_login_email.forms import register


def raise_if_registered(func: Callable[[str], str]):
  """Raise an exception if the user is already registered."""

  # check params of func
  assert "email" in func.__code__.co_varnames, "Function has no 'email' parameter."

  def inner(email: str):
    if register.is_registered(email):
      raise Exception("User already registered.")
    return func(email)

  return inner
