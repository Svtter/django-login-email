# Django Login Email

[![PyPI](https://img.shields.io/pypi/v/django-login-email.svg)](https://pypi.python.org/pypi/django-login-email/)
[![Documentation Status](https://readthedocs.org/projects/django-login-email/badge/?version=latest)](https://django-login-email.readthedocs.io/en/latest/?badge=latest) [![Downloads](https://pepy.tech/badge/django-login-email/week)](https://pepy.tech/project/django-login-email)

Allow user to login and register with email address.

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
- [x] Register new user.
- [x] Support multiple user.
- [ ] Change email address.
- [ ] Ban the IP to send mail frequently without login.
- [ ] Enable 2FA.
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
from django.urls import reverse

from django_login_email import email as e
from django_login_email import views as v

# Create your views here.

loginInfo, registerInfo = e.get_info_class("meterhub")


class LoginView(v.EmailLoginView):
  login_info_class = loginInfo
  register_info_class = registerInfo


class VerifyView(v.EmailVerifyView):
  def get_success_url(self):
    return reverse("home")


class LogoutView(v.EmailLogoutView):
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

Debug the email with `docker run -d --name mailhog -p 1025:1025 -p 8025:8025 mailhog/mailhog`

## Settings

1. Config `LoginView.tl` to disable login attempts check.
2. View [settings/settings.py](./settings/settings.py) to config the email server account. As same as django official settings.
3. Disable login check:

```python
class YouLoginView(LoginView):
  def check_could_send(self, email) -> bool:
    # FOR DEBUG
    return True
```

## Future

- Academically prove the safety of this method.

## Related project

- [django-login-with-email](https://github.com/wsvincent/django-login-with-email)
- [django-unique-user-email](https://github.com/carltongibson/django-unique-user-email)
