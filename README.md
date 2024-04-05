# Django Login Email

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
- [ ] More easier and customizable login link.

## Future

- Academically prove the safety of this method.

## Related project

- [django-login-with-email](https://github.com/wsvincent/django-login-with-email)
- [django-unique-user-email](https://github.com/carltongibson/django-unique-user-email)
