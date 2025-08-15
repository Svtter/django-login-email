django-login-email documentation
================================

.. image:: https://img.shields.io/pypi/v/django-login-email.svg
   :target: https://pypi.python.org/pypi/django-login-email/
.. image:: https://readthedocs.org/projects/django-login-email/badge/?version=latest
   :target: https://django-login-email.readthedocs.io/en/latest/?badge=latest
.. image:: https://pepy.tech/badge/django-login-email/week
   :target: https://pepy.tech/project/django-login-email

Allow user to login and register with email address.

NOTICE: We are currently in the development stage. If you use this library, please upgrade to the latest version. Issues are welcome.

You can view the documentation `here <https://deepwiki.com/Svtter/django-login-email>`_.

Install
-------

.. code-block:: bash

   pip install django-login-email

Feature
-------

- [x] The developer could define their own ``User`` model
- [x] Time-limited of login link
- [x] Limited of sending email (using TimeLimit to set minutes)
- [x] The link could be used for Login once
- [x] Register new user
- [x] Support multiple user
- [x] Ban the IP to send mail frequently without login
- [ ] Support `django-templated-email <https://github.com/vintasoftware/django-templated-email>`_
- [ ] Support Django Anymail
- [ ] Allow users to change their email address
- [ ] Enable 2FA
- [ ] More easier and customizable login link

Usage
-----

Add ``django_login_email`` to your app ``settings.py``:

.. code-block:: python

   INSTALLED_APP = [
       ...,
       'django_login_email',
       ...
   ]

Implement the LoginView:

.. code-block:: python

   from django.shortcuts import render
   from django.urls import reverse

   from django_login_email import email as e
   from django_login_email import views as v

   loginInfo, registerInfo = e.get_info_class("meterhub")

   class LoginView(v.EmailLoginView):
       login_info_class = loginInfo
       register_info_class = registerInfo

   class VerifyView(v.EmailVerifyView):
       def get_success_url(self):
           return reverse("home")

   class LogoutView(v.EmailLogoutView):
       pass

Set the view in your ``urls.py``:

.. code-block:: python

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

Debug the email with:

.. code-block:: bash

   docker run -d --name mailhog -p 1025:1025 -p 8025:8025 mailhog/mailhog

Settings
--------

1. Config ``LoginView.tl`` to disable login attempts check
2. View `settings/settings.py <./settings/settings.py>`_ to config the email server account (same as Django official settings)
3. Disable login check:

.. code-block:: python

   class YouLoginView(LoginView):
       def check_could_send(self, email) -> bool:
           # FOR DEBUG
           return True

Future
------

- Academically prove the safety of this method

Related project
---------------

- `django-email-verification <https://github.com/LeoneBacciu/django-email-verification>`_
- `django-login-with-email <https://github.com/wsvincent/django-login-with-email>`_
- `django-unique-user-email <https://github.com/carltongibson/django-unique-user-email>`_

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   developer
