class LoginMailError(Exception):
  """Base exception for login email errors"""

  pass


class ValidatedError(LoginMailError):
  """When validated, raise this error"""

  pass


class TokenError(LoginMailError):
  """When token error, raise this error"""

  pass


class RateLimitError(LoginMailError):
  """When rate limit is exceeded"""

  pass


class InactiveUserError(LoginMailError):
  """When user account is inactive"""

  pass


class EmailSendError(LoginMailError):
  """When email sending fails"""

  pass
