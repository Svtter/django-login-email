class LoginMailError(Exception):
  pass


class ValidatedError(LoginMailError):
  """When validated, raise this error"""

  pass


class TokenError(LoginMailError):
  """When token error, raise this error"""

  pass
