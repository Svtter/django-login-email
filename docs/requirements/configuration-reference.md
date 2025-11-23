# Configuration Reference

This document describes all configuration options for `django-login-email`.

## Django Settings

These settings should be configured in your Django `settings.py`.

### Required Settings

#### `SECRET_KEY`

**Type**: `str`

**Required**: ✅ Yes

**Default**: N/A (Django required setting)

**Purpose**: Used for AES encryption of email tokens

**Requirements**:
- **MUST** be at least 32 characters long (only first 32 characters are used)
- **MUST** be kept secret and not committed to version control
- **MUST** be unique per environment (dev/staging/prod)
- **MUST** remain constant (changing it invalidates all existing tokens)

**Example**:
```python
# settings.py
SECRET_KEY = "your-secret-key-here-at-least-32-chars-long-1234567890"
```

**Security Warning**: If `SECRET_KEY` is less than 32 characters, token encryption will be weak. Django's default key generator produces 50 characters.

---

#### Email Backend Settings

**Required**: ✅ Yes (Django settings for email)

**Settings**:
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'  # Default
EMAIL_HOST = 'smtp.example.com'  # SMTP server
EMAIL_PORT = 587  # Usually 587 (TLS) or 465 (SSL)
EMAIL_USE_TLS = True  # Recommended
EMAIL_HOST_USER = 'your-email@example.com'
EMAIL_HOST_PASSWORD = 'your-password'  # Use environment variable
```

**Development Configuration**:
```python
# For local development with MailHog
EMAIL_HOST = 'localhost'
EMAIL_PORT = 1025
EMAIL_HOST_USER = 'user'
EMAIL_HOST_PASSWORD = ''
```

**Testing Configuration**:
```python
# For unit tests
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
```

**Production Best Practices**:
- Store `EMAIL_HOST_PASSWORD` in environment variable
- Use TLS/SSL encryption
- Consider using a transactional email service (SendGrid, Mailgun, AWS SES)

---

### Optional Django Settings

#### `INSTALLED_APPS`

**Required**: ✅ Yes (must include package)

**Example**:
```python
INSTALLED_APPS = [
    # Django defaults
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',

    # This package
    'django_login_email',

    # Your apps
    'yourapp',
]
```

**Note**: Order matters - `django_login_email` should come before your apps so you can override templates.

---

## View Configuration

These settings are configured on your view classes.

### EmailLoginView Configuration

#### `login_info_class`

**Type**: `Type[EmailLoginInfo]`

**Required**: ✅ Yes

**Default**: None (must be set)

**Purpose**: Class to configure login email content and sending

**Example**:
```python
from django_login_email import email as e

class MyLoginInfo(e.EmailLoginInfo):
    system_name = "MyApp"

    def __init__(self):
        super().__init__()
        self.from_email = "noreply@myapp.com"
        self.url = "https://myapp.com/account/verify?token="

class LoginView(EmailLoginView):
    login_info_class = MyLoginInfo
```

**Customizable Attributes** in `EmailLoginInfo`:
- `system_name`: Your application name (shown in email)
- `from_email`: Sender email address
- `url`: Verification URL (must point to your `EmailVerifyView`)
- `subject`: Email subject line
- `welcome_text`: Text before the login link
- `login_message`: Template for the link (string.Template)

---

#### `register_info_class`

**Type**: `Type[EmailRegisterInfo]`

**Required**: ✅ Yes

**Default**: None (must be set)

**Purpose**: Class to configure registration email content

**Example**:
```python
class MyRegisterInfo(e.EmailRegisterInfo):
    system_name = "MyApp"

    def __init__(self):
        super().__init__()
        self.from_email = "noreply@myapp.com"
        self.url = "https://myapp.com/account/verify?token="

class LoginView(EmailLoginView):
    register_info_class = MyRegisterInfo
```

---

#### `tl` (Time Limit)

**Type**: `TimeLimit`

**Required**: ❌ No

**Default**: `LoginTimeLimit()` (10 minutes)

**Purpose**: Configure rate limiting for email sending

**Example**:
```python
from django_login_email.email import TimeLimit

class LoginView(EmailLoginView):
    tl = TimeLimit(minutes=15)  # 15 minute rate limit
```

**How it works**:
- User can only request a new email once every `minutes` minutes
- Timer starts when email is sent
- Timer resets when user successfully logs in
- Same email cannot be sent multiple times within the window

**Recommended Values**:
- Development: 1-5 minutes (for testing)
- Production: 10-15 minutes (balance security and UX)
- High-security: 30-60 minutes

---

#### `template_name`

**Type**: `str`

**Required**: ❌ No

**Default**: `"login_email/login.html"`

**Purpose**: Template for login form page

**Example**:
```python
class LoginView(EmailLoginView):
    template_name = "myapp/login.html"
```

---

#### `error_template`

**Type**: `str`

**Required**: ❌ No

**Default**: `"login_email/error.html"`

**Purpose**: Template for error messages

**Example**:
```python
class LoginView(EmailLoginView):
    error_template = "myapp/error.html"
```

**Template Context**:
- `error`: Error message string

---

#### `success_template`

**Type**: `str`

**Required**: ❌ No

**Default**: `"login_email/success.html"`

**Purpose**: Template shown after email is sent

**Example**:
```python
class LoginView(EmailLoginView):
    success_template = "myapp/check_email.html"
```

**Template Context**:
- `form`: Submitted form with email address

---

#### `form_class`

**Type**: `Type[Form]`

**Required**: ❌ No

**Default**: `LoginForm`

**Purpose**: Form class for email input

**Example** (custom validation):
```python
from django import forms

class CustomLoginForm(forms.Form):
    email = forms.EmailField()

    def clean_email(self):
        email = self.cleaned_data['email']
        # Custom validation: only allow company emails
        if not email.endswith('@mycompany.com'):
            raise forms.ValidationError("Only company emails allowed")
        return email

class LoginView(EmailLoginView):
    form_class = CustomLoginForm
```

---

### EmailVerifyView Configuration

#### `tl` (Time Limit)

**Type**: `TimeLimit`

**Required**: ❌ No

**Default**: `LoginTimeLimit()` (10 minutes)

**Purpose**: Configure token expiration time

**Example**:
```python
class VerifyView(EmailVerifyView):
    tl = TimeLimit(minutes=30)  # Tokens valid for 30 minutes
```

**IMPORTANT**: This MUST match the `tl` setting in your `EmailLoginView`, otherwise token validation will fail.

---

#### `error_template`

**Type**: `str`

**Required**: ❌ No

**Default**: `"login_email/error.html"`

**Purpose**: Template for token verification errors

---

#### `get_success_url()`

**Type**: Method returning `str`

**Required**: ✅ Yes

**Default**: Returns `"login_email:home"` (you must override this)

**Purpose**: URL to redirect to after successful login

**Example**:
```python
from django.urls import reverse

class VerifyView(EmailVerifyView):
    def get_success_url(self):
        return reverse("dashboard")  # Your app's main page
```

---

### EmailLogoutView Configuration

#### `login_url`

**Type**: `str`

**Required**: ❌ No

**Default**: `"login_email:login"`

**Purpose**: URL to redirect to after logout

**Example**:
```python
class LogoutView(EmailLogoutView):
    login_url = "myapp:login"  # Or just "login" if no namespace
```

---

## Advanced Configuration

### Customizing Email Templates

The email body is generated using Python's `string.Template`. To customize:

```python
import string

class MyLoginInfo(EmailLoginInfo):
    def __init__(self):
        super().__init__()
        self.welcome_text = "Hello! Welcome to MyApp.<br>"
        self.login_message = string.Template(
            '<a href="$url$token" style="color: blue;">Click here to login</a>'
        )
```

**Available Variables**:
- `$url`: Base verification URL
- `$token`: Encrypted token

---

### Disabling Rate Limiting (Development Only)

**WARNING**: Only use this for debugging!

```python
class DebugLoginView(EmailLoginView):
    def check_could_send(self, email) -> bool:
        return True  # ALWAYS allow sending
```

This bypasses the time limit check.

---

### Customizing IP Ban Behavior

Override methods from `IPBanUtils`:

```python
class MyLoginView(EmailLoginView):
    def ban_ip(self, ip: str, reason: str):
        # Custom logic: send notification email
        send_admin_email(f"IP banned: {ip} - {reason}")
        super().ban_ip(ip, reason)
```

---

### Customizing User Creation

By default, new users are created with `username = email`. To customize:

```python
from django_login_email.email import EmailVerifyMixin

class MyVerifyView(EmailVerifyView):
    def verify_token(self, token_v: str):
        # Call parent to get user
        user = super().verify_token(token_v)

        # Customize new users
        if user.date_joined == user.last_login:  # Newly created
            user.first_name = user.email.split('@')[0]
            user.save()

        return user
```

---

## Environment-Specific Configuration

### Development

```python
# settings/dev.py
DEBUG = True
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # Print to console

# Short rate limit for testing
from django_login_email.email import TimeLimit
LOGIN_TIME_LIMIT = TimeLimit(minutes=1)
```

### Testing

```python
# settings/test.py
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
```

### Production

```python
# settings/prod.py
DEBUG = False
EMAIL_USE_TLS = True
EMAIL_HOST = os.getenv('EMAIL_HOST')
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')

# Production rate limit
from django_login_email.email import TimeLimit
LOGIN_TIME_LIMIT = TimeLimit(minutes=15)
```

---

## Configuration Validation

### Checking Your Configuration

Create a management command to validate settings:

```python
# yourapp/management/commands/check_email_login.py
from django.core.management.base import BaseCommand
from django.conf import settings

class Command(BaseCommand):
    def handle(self, *args, **options):
        # Check SECRET_KEY length
        if len(settings.SECRET_KEY) < 32:
            self.stdout.write(self.style.WARNING(
                'SECRET_KEY is less than 32 characters'
            ))

        # Check email settings
        required = ['EMAIL_HOST', 'EMAIL_HOST_USER', 'EMAIL_PORT']
        for setting in required:
            if not hasattr(settings, setting):
                self.stdout.write(self.style.ERROR(
                    f'Missing setting: {setting}'
                ))

        self.stdout.write(self.style.SUCCESS('Configuration OK'))
```

---

## Configuration Examples

### Minimal Configuration

```python
# settings.py
INSTALLED_APPS = ['django_login_email', ...]
SECRET_KEY = 'your-secret-key-here-min-32-chars-long-abc123'
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# views.py
from django_login_email import views, email

LoginInfo, RegisterInfo = email.get_info_class("MyApp")

class LoginView(views.EmailLoginView):
    login_info_class = LoginInfo
    register_info_class = RegisterInfo

class VerifyView(views.EmailVerifyView):
    def get_success_url(self):
        return '/'
```

### Production Configuration

```python
# settings.py
import os

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'apikey'
EMAIL_HOST_PASSWORD = os.getenv('SENDGRID_API_KEY')

# views.py
from django_login_email import views, email

class ProductionLoginInfo(email.EmailLoginInfo):
    system_name = "MyApp"

    def __init__(self):
        super().__init__()
        self.from_email = "noreply@myapp.com"
        self.url = "https://myapp.com/account/verify?token="

class ProductionRegisterInfo(email.EmailRegisterInfo):
    system_name = "MyApp"

    def __init__(self):
        super().__init__()
        self.from_email = "noreply@myapp.com"
        self.url = "https://myapp.com/account/verify?token="

class LoginView(views.EmailLoginView):
    login_info_class = ProductionLoginInfo
    register_info_class = ProductionRegisterInfo
    tl = email.TimeLimit(minutes=15)
```

---

## Troubleshooting

### Email Not Sending

1. Check EMAIL_BACKEND is SMTP in production
2. Verify EMAIL_HOST_PASSWORD is correct
3. Check SMTP server logs
4. Test with Django shell:
   ```python
   from django.core.mail import send_mail
   send_mail('Test', 'Body', 'from@example.com', ['to@example.com'])
   ```

### Token Validation Failing

1. Ensure `tl` settings match between LoginView and VerifyView
2. Check SECRET_KEY hasn't changed
3. Verify token hasn't expired
4. Check for clock skew if using multiple servers

### Rate Limiting Too Aggressive

1. Adjust `tl.minutes` to a higher value
2. Check EmailRecord table for stale entries
3. Consider implementing cleanup for old records

---

## Next Steps

- See [Extension Points](./extension-points.md) for customization options
- See [API Specification](./api-specification.md) for detailed API reference
