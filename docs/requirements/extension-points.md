# Extension Points

This document describes the stable extension points in `django-login-email` that are designed for customization.

## What is an Extension Point?

An **extension point** is a class method or hook that is:
- ✅ Designed to be overridden by users
- ✅ Has a stable interface (signature won't change without major version bump)
- ✅ Documented behavior and expectations
- ✅ Safe to customize without breaking the package

**Extension points are part of the public API.**

---

## View Extension Points

### EmailLoginView Extension Points

#### `check_could_send(email: str) -> bool`

**Purpose**: Determine if an email can be sent to the given address

**Default Behavior**:
- Checks if email was sent within `tl.minutes` minutes
- Returns `False` if still within rate limit window
- Returns `True` if enough time has passed

**When to Override**:
- Custom rate limiting logic
- Per-user rate limits
- Whitelist certain email addresses
- Disable rate limiting for testing

**Example 1: Disable rate limiting for admins**
```python
class MyLoginView(EmailLoginView):
    def check_could_send(self, email: str) -> bool:
        # Admins can always send
        if email.endswith('@admin.myapp.com'):
            return True
        return super().check_could_send(email)
```

**Example 2: Custom rate limiting per domain**
```python
class MyLoginView(EmailLoginView):
    DOMAIN_LIMITS = {
        'fastdomain.com': 5,   # 5 minutes
        'slowdomain.com': 30,  # 30 minutes
    }

    def check_could_send(self, email: str) -> bool:
        domain = email.split('@')[1]
        minutes = self.DOMAIN_LIMITS.get(domain, 10)  # Default 10

        # Custom logic with different time limits
        re = self.get_mail_record(email)
        if re.expired_time is None:
            return True

        from datetime import datetime, timedelta, timezone
        threshold = datetime.now(tz=timezone.utc) - timedelta(minutes=minutes)
        return re.expired_time <= threshold
```

**Signature**: Must return `bool`, takes `email: str`

---

#### `send_login_mail(email: str) -> None`

**Purpose**: Send login or register email

**Default Behavior**:
- Checks if user exists (sends "login" or "register" email accordingly)
- Validates rate limiting
- Generates token
- Sends email

**When to Override**:
- Add logging
- Add analytics tracking
- Custom email type detection
- Send notification to admins

**Example: Add logging**
```python
import logging

logger = logging.getLogger(__name__)

class MyLoginView(EmailLoginView):
    def send_login_mail(self, email: str):
        user_exists = self.check_user(email)
        mail_type = "login" if user_exists else "register"

        logger.info(f"Sending {mail_type} email to {email}")

        try:
            super().send_login_mail(email)
            logger.info(f"Email sent successfully to {email}")
        except Exception as e:
            logger.error(f"Failed to send email to {email}: {e}")
            raise
```

**Signature**: Returns `None`, takes `email: str`, may raise exceptions

---

#### `check_user(email: str) -> bool`

**Purpose**: Check if a user with the given email already exists

**Default Behavior**:
- Queries `User.objects.filter(email=email)`
- Returns `True` if exists, `False` otherwise

**When to Override**:
- Use different field for lookup
- Multi-tenant user filtering
- Case-insensitive email matching
- Custom user model logic

**Example: Case-insensitive email lookup**
```python
from django.contrib.auth import get_user_model

class MyLoginView(EmailLoginView):
    def check_user(self, email: str) -> bool:
        User = get_user_model()
        return User.objects.filter(email__iexact=email).exists()
```

**Example: Multi-tenant filtering**
```python
class MyLoginView(EmailLoginView):
    tenant_id = None  # Set this in dispatch() or get()

    def check_user(self, email: str) -> bool:
        User = get_user_model()
        return User.objects.filter(
            email=email,
            tenant_id=self.tenant_id
        ).exists()
```

**Signature**: Returns `bool`, takes `email: str`

---

#### `get(request, *args, **kwargs) -> HttpResponse`

**Purpose**: Handle GET requests (display login form)

**Default Behavior**:
- Redirect to "home" if user already authenticated
- Otherwise, display login form

**When to Override**:
- Custom redirect for authenticated users
- Add extra context to template
- Pre-fill form fields
- Add analytics tracking

**Example: Add extra context**
```python
class MyLoginView(EmailLoginView):
    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)

        # Add extra context if rendering template
        if hasattr(response, 'context_data'):
            response.context_data['site_name'] = 'MyApp'
            response.context_data['support_email'] = 'support@myapp.com'

        return response
```

**Signature**: Standard Django view signature

---

#### `form_valid(form) -> HttpResponse`

**Purpose**: Process valid login form submission

**Default Behavior**:
1. Check if IP is banned
2. Check if user is already authenticated
3. Send login/register email
4. Record the send attempt
5. Render success template

**When to Override**:
- Add custom validation
- Track analytics
- Add logging
- Custom success behavior

**Example: Track analytics**
```python
class MyLoginView(EmailLoginView):
    def form_valid(self, form):
        email = form.cleaned_data['email']

        # Track analytics
        track_event('login_email_sent', {
            'email_domain': email.split('@')[1],
            'is_new_user': not self.check_user(email)
        })

        return super().form_valid(form)
```

**Signature**: Standard Django `FormView.form_valid()` signature

---

### EmailVerifyView Extension Points

#### `verify_token(token_v: str) -> User`

**Purpose**: Verify token and return user (creates user if doesn't exist)

**Default Behavior**:
1. Decrypt and validate token
2. Check token hasn't been used
3. Verify salt and expiration
4. Create user if doesn't exist (username = email)
5. Check user is active
6. Mark token as used
7. Return user object

**When to Override**:
- Custom user creation logic
- Set additional user fields
- Send welcome email
- Add user to groups
- Track analytics

**Example: Set user fields on registration**
```python
class MyVerifyView(EmailVerifyView):
    def verify_token(self, token_v: str):
        # Get user from parent
        user = super().verify_token(token_v)

        # Check if newly created (date_joined = last_login for new users)
        from django.utils import timezone
        time_diff = (user.last_login - user.date_joined).total_seconds()

        if time_diff < 1:  # Newly created within 1 second
            # Set additional fields
            user.first_name = user.email.split('@')[0].title()
            user.is_active = True
            user.save()

            # Add to default group
            from django.contrib.auth.models import Group
            default_group, _ = Group.objects.get_or_create(name='Users')
            user.groups.add(default_group)

            # Send welcome email
            from django.core.mail import send_mail
            send_mail(
                'Welcome!',
                'Welcome to our platform!',
                'noreply@myapp.com',
                [user.email]
            )

        return user
```

**Signature**: Returns `User` instance, takes `token_v: str`, may raise exceptions

---

#### `verify_login_mail(request, token_v: str) -> None`

**Purpose**: Verify token and log user in

**Default Behavior**:
1. Call `verify_token(token_v)` to get user
2. Call Django's `login(request, user)`

**When to Override**:
- Custom login behavior
- Track login analytics
- Set session variables
- Redirect logic

**Example: Set session variables**
```python
class MyVerifyView(EmailVerifyView):
    def verify_login_mail(self, request, token_v: str):
        # Call parent to login
        super().verify_login_mail(request, token_v)

        # Set custom session variables
        request.session['login_method'] = 'email'
        request.session['login_time'] = timezone.now().isoformat()
```

**Signature**: Returns `None`, takes `request` and `token_v: str`

---

#### `get_success_url() -> str`

**Purpose**: Return URL to redirect to after successful login

**Default Behavior**:
- Returns `"login_email:home"` (you should override this)

**When to Override**:
- **Always** - this is required for production use
- Redirect to user dashboard
- Redirect based on user type
- Redirect to original destination (if stored in session)

**Example: Redirect based on user type**
```python
from django.urls import reverse

class MyVerifyView(EmailVerifyView):
    def get_success_url(self):
        user = self.request.user

        if user.is_staff:
            return reverse('admin_dashboard')
        elif user.groups.filter(name='Premium').exists():
            return reverse('premium_dashboard')
        else:
            return reverse('user_dashboard')
```

**Example: Redirect to intended destination**
```python
class MyVerifyView(EmailVerifyView):
    def get_success_url(self):
        # Check if there's a 'next' parameter
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url

        return reverse('dashboard')
```

**Signature**: Returns `str` (URL), takes `self` only

---

#### `get(request, *args, **kwargs) -> HttpResponse`

**Purpose**: Handle GET request with token parameter

**Default Behavior**:
1. Extract token from query parameter
2. Verify and login user
3. Handle exceptions (show error template)
4. Redirect to success URL

**When to Override**:
- Custom error handling
- Add logging
- Track analytics
- Custom response format (API mode)

**Example: API mode (return JSON)**
```python
from django.http import JsonResponse

class APIVerifyView(EmailVerifyView):
    def get(self, request, *args, **kwargs):
        token = request.GET.get('token')
        if not token:
            return JsonResponse({'error': 'Missing token'}, status=400)

        try:
            self.verify_login_mail(request=request, token_v=token)
            return JsonResponse({
                'success': True,
                'redirect_url': self.get_success_url()
            })
        except errors.ValidatedError:
            return JsonResponse({'error': 'Token already used'}, status=400)
        except errors.TokenError:
            return JsonResponse({'error': 'Invalid token'}, status=400)
```

**Signature**: Standard Django view signature

---

### EmailLogoutView Extension Points

#### `logout(request) -> None`

**Purpose**: Log user out

**Default Behavior**:
- Calls Django's `logout(request)`

**When to Override**:
- Clear custom session data
- Track logout analytics
- Cleanup user-specific caches

**Example: Track logout**
```python
class MyLogoutView(EmailLogoutView):
    def logout(self, request):
        user_email = request.user.email if request.user.is_authenticated else 'anonymous'

        # Log the logout
        logger.info(f"User {user_email} logged out")

        # Track analytics
        track_event('user_logout', {'email': user_email})

        # Call parent
        super().logout(request)
```

**Signature**: Returns `None`, takes `request`

---

## Email Info Extension Points

### EmailLoginInfo / EmailRegisterInfo

These classes are designed to be subclassed for customization.

#### Customizable Attributes

```python
class MyLoginInfo(EmailLoginInfo):
    system_name = "MyApp"  # Your app name

    def __init__(self):
        super().__init__()

        # Customize these attributes
        self.from_email = "noreply@myapp.com"
        self.url = "https://myapp.com/account/verify?token="
        self.subject = "Login to MyApp"
        self.welcome_text = "Welcome back to MyApp!<br>"

        # Advanced: custom template
        import string
        self.login_message = string.Template(
            '<div style="padding:20px;">'
            '<a href="$url$token" style="color:#007bff;">Click to Login</a>'
            '</div>'
        )
```

#### `build_message(token: str) -> None`

**Purpose**: Build email message from token

**Default Behavior**:
- Substitutes token into `login_message` template
- Sets `self.message` attribute

**When to Override**:
- Completely custom email HTML
- Multi-language support
- Include additional data in email

**Example: Multi-language emails**
```python
class MultiLangLoginInfo(EmailLoginInfo):
    language = 'en'  # Set this based on user preference

    MESSAGES = {
        'en': 'Click <a href="$url$token">here</a> to login',
        'es': 'Haga clic <a href="$url$token">aquí</a> para iniciar sesión',
        'fr': 'Cliquez <a href="$url$token">ici</a> pour vous connecter',
    }

    def build_message(self, token):
        template = string.Template(self.MESSAGES[self.language])
        self.message = self.welcome_text + template.substitute(
            url=self.url,
            token=token
        )
```

**Signature**: Returns `None`, takes `token: str`

---

## Mixin Extension Points

### MailRecordAPI (Abstract Methods)

If you create a custom view without inheriting from `MailRecordModelMixin`, you must implement:

#### `get_mail_record(mail: str) -> MailRecord`

**Purpose**: Retrieve email record for rate limiting

**Required Implementation**: Yes (if not using `MailRecordModelMixin`)

**Example**:
```python
from django_login_email.models import EmailRecord
from django_login_email.email import MailRecord

class MyMixin:
    def get_mail_record(self, mail: str) -> MailRecord:
        try:
            record = EmailRecord.objects.get(email=mail)
            return MailRecord(
                expired_time=record.expired_time,
                email=record.email,
                validated=record.validated,
                salt=record.salt
            )
        except EmailRecord.DoesNotExist:
            return MailRecord(
                expired_time=None,
                email=mail,
                validated=False,
                salt=""
            )
```

---

#### `save_token(token: TokenDict) -> None`

**Purpose**: Save token to database

**Required Implementation**: Yes (if not using `MailRecordModelMixin`)

**Example**:
```python
from datetime import datetime, timezone as tz

class MyMixin:
    def save_token(self, token: TokenDict) -> None:
        from django_login_email.models import EmailRecord

        obj, created = EmailRecord.objects.get_or_create(email=token['email'])
        obj.expired_time = datetime.fromtimestamp(token['expired_time'], tz=tz.utc)
        obj.mail_type = token['mail_type']
        obj.salt = token['salt']
        obj.validated = False
        obj.save()
```

---

#### `disable_token(token: TokenDict) -> None`

**Purpose**: Mark token as used (prevents reuse)

**Required Implementation**: Yes (if not using `MailRecordModelMixin`)

**Example**:
```python
class MyMixin:
    def disable_token(self, token: TokenDict) -> None:
        from django_login_email.models import EmailRecord

        obj = EmailRecord.objects.get(email=token['email'])
        obj.validated = True
        obj.save()
```

---

## Best Practices

### 1. Always Call `super()`

When overriding methods, call the parent implementation unless you're completely replacing behavior:

```python
# ✅ Good
def send_login_mail(self, email: str):
    logger.info(f"Sending to {email}")
    super().send_login_mail(email)  # Call parent

# ❌ Bad (unless you really want to replace everything)
def send_login_mail(self, email: str):
    # Custom implementation, parent not called
    send_mail('Subject', 'Body', 'from@ex.com', [email])
```

---

### 2. Handle Exceptions Appropriately

Don't silently swallow exceptions from the parent:

```python
# ✅ Good
def verify_token(self, token_v: str):
    try:
        user = super().verify_token(token_v)
    except errors.TokenError:
        logger.error(f"Invalid token: {token_v}")
        raise  # Re-raise for proper handling

    return user

# ❌ Bad
def verify_token(self, token_v: str):
    try:
        return super().verify_token(token_v)
    except:
        return None  # Hides errors!
```

---

### 3. Don't Depend on Internal Implementation

Only override documented extension points:

```python
# ✅ Good - documented extension point
def check_could_send(self, email: str) -> bool:
    return super().check_could_send(email)

# ❌ Bad - internal method, may change
def get_token_manager(self):
    return custom_token_manager()  # May break in future
```

---

### 4. Maintain Signature Compatibility

Don't change method signatures:

```python
# ✅ Good
def check_user(self, email: str) -> bool:
    # Custom logic
    return True

# ❌ Bad - changed signature
def check_user(self, email: str, tenant_id: int) -> bool:
    # Parent calls won't pass tenant_id!
    return True
```

---

## Extension Examples

### Complete Example: Multi-Tenant Application

```python
from django_login_email import views, email, errors
from django.shortcuts import redirect

class TenantLoginView(views.EmailLoginView):
    def dispatch(self, request, *args, **kwargs):
        # Extract tenant from subdomain
        self.tenant = request.get_host().split('.')[0]
        return super().dispatch(request, *args, **kwargs)

    def check_user(self, email: str) -> bool:
        User = get_user_model()
        return User.objects.filter(email=email, tenant=self.tenant).exists()


class TenantVerifyView(views.EmailVerifyView):
    def verify_token(self, token_v: str):
        user = super().verify_token(token_v)

        # Set tenant on new users
        if not user.tenant:
            tenant = self.request.get_host().split('.')[0]
            user.tenant = tenant
            user.save()

        return user

    def get_success_url(self):
        return f"https://{user.tenant}.myapp.com/dashboard"
```

---

## Not Extension Points

These are **internal implementation details** and should NOT be overridden:

- `get_token_manager()` - internal token handling
- `send_valid()` - internal email sending
- Any method in `token.py` module
- Template rendering internals

If you need to customize these, open an issue to discuss adding a proper extension point.

---

## Future Extension Points

Planned for future versions:

- [ ] `pre_send_email()` / `post_send_email()` hooks
- [ ] `pre_login()` / `post_login()` hooks
- [ ] Signal system for events
- [ ] Custom token generator interface

See [GitHub Issues](https://github.com/Svtter/django-login-email/issues) for discussions.
