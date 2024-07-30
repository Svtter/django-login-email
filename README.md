# Django Login Email

[![PyPI](https://img.shields.io/pypi/v/django-login-email.svg)](https://pypi.python.org/pypi/django-login-email/)
[![Documentation Status](https://readthedocs.org/projects/django-login-email/badge/?version=latest)](https://django-login-email.readthedocs.io/en/latest/?badge=latest) [![Downloads](https://pepy.tech/badge/django-login-email/week)](https://pepy.tech/project/django-login-email)

Allow user to login with only email.

## Install

`pip install django-login-email`

List of the urls for exmaple project:

- `/home` for protected url.
- `/account/login` for login.
- `/account/logout` for logout.
- `/account/verify` for email verify.

## Feature

- [x] The developer could define their own `User` model.
- [x] Time-limited of login link.
- [x] limited of sending email. Using TimeLimt to set minutes.
- [x] The link could be used for Login once.
- [ ] Ban the IP to send mail frequently without login.
- [ ] Multiple user.
- [ ] More easier and customizable login link.

## Usage

- add `django_login_email` to your app `settings.py`.

```python
INSTALLED_APP = [
    ...,
    'django_login_email',
    ...
]
```

- Implement the LoginView, for example, like this:

```python
from django.shortcuts import render
from django_login_email import views as v
from django_login_email import email as e

# Create your views here.


class MyInfo(e.EmailLoginInfo):
    def set_variables(self):
        self.subject = "Login request from meterhub"
        self.welcome_text = "Welcome to meterhub! Please click the link below to login.<br>"
        self.from_email = "sandbox.smtp.mailtrap.io"


class LoginView(v.EmailLoginView):
    email_info_class = MyInfo


class VerifyView(v.EmailVerifyView):
    pass

```

- set the view in your `urls.py`.

```python
from django.contrib import admin
from django.urls import path
from <yourapp> import views as v
from django_login_email.views import HomeView

urlpatterns = [
    ...,
    path("account/login", v.LoginView.as_view(), name="login"),
    path("account/verify", v.VerifyView.as_view(), name="verify"),
    path("account/logout", v.LogoutView.as_view(), name="logout"),
    path("", HomeView.as_view(), name="home"),
]
```

That's all.

## Future

- Academically prove the safety of this method.

## Related project

- [django-login-with-email](https://github.com/wsvincent/django-login-with-email)
- [django-unique-user-email](https://github.com/carltongibson/django-unique-user-email)
