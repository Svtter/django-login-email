# Integration Requirements

This document describes the requirements for integrating `django-login-email` into your Django project.

## Django Project Prerequisites

### Required Django Settings

Your Django project **MUST** have the following settings configured:

1. **Email Backend Configuration**
   - `EMAIL_HOST`: SMTP server hostname
   - `EMAIL_HOST_USER`: SMTP username
   - `EMAIL_HOST_PASSWORD`: SMTP password
   - `EMAIL_PORT`: SMTP port (default: 587 for TLS, 465 for SSL)
   - `EMAIL_USE_TLS` or `EMAIL_USE_SSL`: Email encryption (recommended)

2. **Secret Key**
   - `SECRET_KEY`: Must be at least 32 characters long for AES encryption
   - MUST be kept secret and unique per environment
   - Used for token encryption/decryption

3. **Installed Apps**
   - `django.contrib.auth`: Required for user authentication
   - `django.contrib.sessions`: Required for login sessions
   - `django.contrib.contenttypes`: Required for generic relations

4. **Middleware**
   - `django.contrib.sessions.middleware.SessionMiddleware`: Required
   - `django.contrib.auth.middleware.AuthenticationMiddleware`: Required
   - `django.middleware.csrf.CsrfViewMiddleware`: Recommended for security

### User Model Requirements

The User model (either Django's default or a custom model) **MUST** have:

- `email` field: EmailField, should be unique
- `username` field: CharField (can be auto-generated from email)
- `is_active` field: BooleanField (to support account deactivation)
- `is_authenticated` property: To check login status

**Note**: When a user registers via email, the system automatically creates:
- `username = email`
- `email = email`

You can customize this behavior by overriding `EmailVerifyMixin.verify_token()`.

## Installation Steps

### 1. Install the Package

```bash
pip install django-login-email
```

### 2. Add to INSTALLED_APPS

Add `'django_login_email'` to your `INSTALLED_APPS` in `settings.py`:

```python
INSTALLED_APPS = [
    # Django defaults
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party apps
    'django_login_email',  # Add this

    # Your apps
    'yourapp',
]
```

### 3. Run Database Migrations

The package requires database tables for `EmailRecord` and `IPBan`:

```bash
python manage.py migrate django_login_email
```

### 4. Create Views

Create your login/verify/logout views by inheriting from the provided base classes:

```python
# yourapp/views.py
from django.shortcuts import render
from django.urls import reverse
from django_login_email import email as e
from django_login_email import views as v

# Get email info classes with your system name
loginInfo, registerInfo = e.get_info_class("YourSystemName")

class LoginView(v.EmailLoginView):
    login_info_class = loginInfo
    register_info_class = registerInfo

class VerifyView(v.EmailVerifyView):
    def get_success_url(self):
        return reverse("home")  # Redirect after successful login

class LogoutView(v.EmailLogoutView):
    pass
```

### 5. Configure URL Patterns

Add the views to your `urls.py`:

```python
# yourapp/urls.py or project/urls.py
from django.urls import path
from yourapp import views

urlpatterns = [
    path("account/login", views.LoginView.as_view(), name="login"),
    path("account/verify", views.VerifyView.as_view(), name="verify"),
    path("account/logout", views.LogoutView.as_view(), name="logout"),
    # ... other patterns
]
```

**IMPORTANT**: The verify URL path MUST match the URL configured in your `EmailInfo` class (default: `/account/verify`).

## Integration with Existing Authentication

### Relationship with Django's Auth System

`django-login-email` is designed to **complement** Django's authentication system:

- ✅ Works alongside Django's `django.contrib.auth`
- ✅ Uses Django's `login()` and `logout()` functions internally
- ✅ Compatible with Django's authentication backends
- ✅ Respects `User.is_active` flag
- ⚠️ Does NOT use passwords (passwordless authentication)
- ⚠️ Does NOT integrate with Django admin login (use separate authentication)

### Coexistence with Password Authentication

You can use `django-login-email` alongside traditional password authentication:

```python
# urls.py
urlpatterns = [
    # Email-based login
    path("account/email-login", views.EmailLoginView.as_view(), name="email-login"),

    # Traditional password login
    path("account/password-login", auth_views.LoginView.as_view(), name="password-login"),

    # Shared verify endpoint
    path("account/verify", views.VerifyView.as_view(), name="verify"),
]
```

Users can choose their preferred authentication method.

## URL Namespace Considerations

The package does NOT enforce URL namespacing. You can:

1. **Use app namespace** (recommended):
```python
# project/urls.py
urlpatterns = [
    path('account/', include(('yourapp.urls', 'account'), namespace='account')),
]

# yourapp/urls.py
urlpatterns = [
    path("login", views.LoginView.as_view(), name="login"),
    path("verify", views.VerifyView.as_view(), name="verify"),
]

# Access as: reverse('account:login')
```

2. **Use global namespace**:
```python
# project/urls.py
urlpatterns = [
    path("account/login", views.LoginView.as_view(), name="login"),
    path("account/verify", views.VerifyView.as_view(), name="verify"),
]

# Access as: reverse('login')
```

## Template Requirements

The package provides default templates in `django_login_email/templates/login_email/`:

- `login.html`: Login form page
- `success.html`: Email sent confirmation page
- `error.html`: Error message page
- `home.html`: Example protected page

### Customizing Templates

You can override these templates by creating files with the same names in your project's `templates/login_email/` directory. Your templates will take precedence due to Django's template loader order.

**Required template context variables**:

- `login.html`: Receives `form` (LoginForm instance)
- `success.html`: Receives `form` (submitted form data)
- `error.html`: Receives `error` (error message string)
- `home.html`: Receives `user` (current authenticated user)

## Static Files

The package does NOT include static files (CSS/JS). You are responsible for styling the templates according to your project's design.

## Database Considerations

### Required Tables

The migration creates two tables:

1. `django_login_email_emailrecord`:
   - Stores email verification tokens and their status
   - One record per email address (unique constraint)

2. `django_login_email_ipban`:
   - Stores banned IP addresses
   - One record per IP (unique constraint)

### Data Retention

The package does NOT automatically clean up old records. You should:

1. Implement periodic cleanup of expired `EmailRecord` entries
2. Decide on IP ban expiration policy
3. Consider adding cleanup as a Django management command or cron job

Example cleanup logic:
```python
from datetime import timedelta
from django.utils import timezone
from django_login_email.models import EmailRecord

# Delete validated records older than 30 days
threshold = timezone.now() - timedelta(days=30)
EmailRecord.objects.filter(validated=True, expired_time__lt=threshold).delete()
```

## Middleware Compatibility

The package works with standard Django middleware. No additional middleware is required.

**Compatible with**:
- Session middleware (required)
- CSRF middleware (recommended)
- Authentication middleware (required)
- CORS middleware (if needed for API access)

## Admin Integration

The package registers `EmailRecord` and `IPBan` models with Django admin:

- Viewable in admin interface at `/admin/django_login_email/`
- Requires staff/superuser permissions
- Useful for monitoring login attempts and managing IP bans

## Multi-Tenancy Considerations

For multi-tenant applications:

1. Email records are global (not tenant-specific)
2. IP bans are global (affect all tenants)
3. User creation happens in the default User model

If you need tenant-specific behavior, you should override:
- `EmailFunc.check_user()` to filter by tenant
- `EmailFunc.send_login_mail()` to include tenant context
- `EmailVerifyMixin.verify_token()` to validate tenant membership

## Testing Integration

To test email functionality in your project:

1. **Development**: Use MailHog or similar SMTP testing tool
   ```bash
   docker run -d --name mailhog -p 1025:1025 -p 8025:8025 mailhog/mailhog
   ```

2. **Testing**: Use Django's console email backend
   ```python
   # test_settings.py
   EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
   ```

3. **CI/CD**: Use in-memory email backend
   ```python
   EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
   ```

## Next Steps

After integration, refer to:

- [Configuration Reference](./configuration-reference.md) for customization options
- [API Specification](./api-specification.md) for extending functionality
- [Extension Points](./extension-points.md) for advanced customization
