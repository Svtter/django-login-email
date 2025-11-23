class LoginMailError(Exception):
  pass


class ValidatedError(LoginMailError):
  """When validated, raise this error"""

  pass


class TokenError(LoginMailError):
  """When token error, raise this error"""

  pass


class RateLimitError(LoginMailError):
  """When rate limit is exceeded, raise this error"""

  pass


class InactiveUserError(LoginMailError):
  """When user is inactive, raise this error"""

  pass
