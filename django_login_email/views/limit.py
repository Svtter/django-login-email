from django_login_email import email


class LoginTimeLimit(email.TimeLimit):
  minutes = 10
