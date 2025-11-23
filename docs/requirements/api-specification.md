# API Specification

This document defines the public API of `django-login-email`. Only items listed here are considered stable and safe to use in your application.

## API Stability Guarantee

### Semantic Versioning

This package follows [Semantic Versioning 2.0.0](https://semver.org/):

- **MAJOR**: Incompatible API changes (e.g., 1.x.x → 2.0.0)
- **MINOR**: Backwards-compatible functionality additions (e.g., 0.6.x → 0.7.0)
- **PATCH**: Backwards-compatible bug fixes (e.g., 0.6.3 → 0.6.4)

### Stability Levels

- 🟢 **Stable**: Public API, will not break without major version bump
- 🟡 **Provisional**: May change in minor versions with deprecation warnings
- 🔴 **Internal**: Not for external use, may change at any time

## Public API

### Views (🟢 Stable)

#### `EmailLoginView`

**Location**: `django_login_email.views.EmailLoginView`

**Purpose**: Display login form and send login/register email

**Base Classes**: `FormView`, `MailRecordModelMixin`, `IPBanUtils`

**Attributes**:
```python
class EmailLoginView:
    template_name: str = "login_email/login.html"
    error_template: str = "login_email/error.html"
    success_template: str = "login_email/success.html"
    form_class: Type[Form] = LoginForm
    login_info_class: Type[EmailLoginInfo]  # REQUIRED to set
    register_info_class: Type[EmailRegisterInfo]  # REQUIRED to set
    tl: TimeLimit = LoginTimeLimit()  # Default: 10 minutes
```

**Methods** (Override Points):
- `get(request, *args, **kwargs) -> HttpResponse`: Handle GET requests
- `form_valid(form) -> HttpResponse`: Process valid login form
- `send_login_mail(email: str) -> None`: Inherited from `EmailFunc`
- `check_could_send(email: str) -> bool`: Check rate limiting

**Exceptions Raised**:
- `errors.RateLimitError`: Too many emails sent
- `errors.EmailSendError`: Email sending failed
- `ValueError`: Invalid mail type

---

#### `EmailVerifyView`

**Location**: `django_login_email.views.EmailVerifyView`

**Purpose**: Verify email token and log user in

**Base Classes**: `TemplateView`, `EmailVerifyMixin`, `MailRecordModelMixin`

**Attributes**:
```python
class EmailVerifyView:
    tl: TimeLimit = LoginTimeLimit()
    error_template: str = "login_email/error.html"
```

**Methods** (Override Points):
- `get(request, *args, **kwargs) -> HttpResponse`: Handle token verification
- `get_success_url() -> str`: **REQUIRED** to override - redirect URL after successful login
- `verify_login_mail(request, token_v: str) -> None`: Inherited from `EmailVerifyMixin`

**Exceptions Raised**:
- `errors.ValidatedError`: Token already used
- `errors.TokenError`: Invalid or expired token
- `errors.InactiveUserError`: User account is inactive
- `ValueError`, `KeyError`: Token parsing error
- `Http404`: Missing or malformed token parameter

---

#### `EmailLogoutView`

**Location**: `django_login_email.views.EmailLogoutView`

**Purpose**: Log user out and redirect

**Base Classes**: `TemplateView`, `EmailLogoutMixin`

**Attributes**:
```python
class EmailLogoutView:
    login_url: str = "login_email:login"  # Redirect after logout
```

**Methods**:
- `get(request, *args, **kwargs) -> HttpResponse`: Handle logout
- `logout(request) -> None`: Inherited from `EmailLogoutMixin`

---

#### `HomeView`

**Location**: `django_login_email.views.HomeView`

**Purpose**: Example of a protected page (for demonstration only)

**Stability**: 🟡 Provisional - provided as example, may be removed in future

---

### Email Classes (🟢 Stable)

#### `EmailInfo`

**Location**: `django_login_email.email.EmailInfo`

**Purpose**: Base class for email configuration

**Attributes**:
```python
class EmailInfo:
    subject: str  # Email subject line
    message: str  # Email HTML body (auto-generated)
    from_email: str  # Sender email address
    welcome_text: str  # Text before the login link
    system_name: str  # Your application name
    url: str = "http://127.0.0.1:8000/account/verify?token="  # Verify URL
    login_message: Template  # Link template
```

**Methods**:
- `build_message(token: str) -> None`: Constructs email message with token

**Note**: This is an abstract base. Use `EmailLoginInfo` or `EmailRegisterInfo`.

---

#### `EmailLoginInfo`

**Location**: `django_login_email.email.EmailLoginInfo`

**Purpose**: Email configuration for login emails

**Example**:
```python
class MyLoginInfo(EmailLoginInfo):
    system_name = "MyApp"

    def __init__(self):
        super().__init__()
        self.from_email = settings.EMAIL_HOST_USER
        self.url = "https://myapp.com/account/verify?token="
```

---

#### `EmailRegisterInfo`

**Location**: `django_login_email.email.EmailRegisterInfo`

**Purpose**: Email configuration for registration emails

**Example**:
```python
class MyRegisterInfo(EmailRegisterInfo):
    system_name = "MyApp"

    def __init__(self):
        super().__init__()
        self.from_email = settings.EMAIL_HOST_USER
        self.url = "https://myapp.com/account/verify?token="
```

---

#### `get_info_class()`

**Location**: `django_login_email.email.get_info_class`

**Signature**: `get_info_class(sys_name: str) -> Tuple[Type[EmailLoginInfo], Type[EmailRegisterInfo]]`

**Purpose**: Helper to create email info classes with system name

**Example**:
```python
loginInfo, registerInfo = get_info_class("MyApp")

class LoginView(EmailLoginView):
    login_info_class = loginInfo
    register_info_class = registerInfo
```

---

### Mixins (🟢 Stable)

#### `EmailFunc`

**Location**: `django_login_email.email.EmailFunc`

**Purpose**: Core email sending functionality

**Abstract Methods** (must implement):
- `get_mail_record(mail: str) -> MailRecord`: Get email record from database
- `save_token(token: TokenDict) -> None`: Save token to database
- `disable_token(token: TokenDict) -> None`: Mark token as used

**Public Methods**:
- `check_user(email: str) -> bool`: Check if user exists
- `check_could_send(email: str) -> bool`: Check rate limiting
- `send_login_mail(email: str) -> None`: Send login or register email
- `send_valid(email: str, mail_type: str) -> None`: Send validation email
- `get_token_manager() -> TokenManager`: Get token manager instance

---

#### `EmailVerifyMixin`

**Location**: `django_login_email.email.EmailVerifyMixin`

**Purpose**: Token verification and user login

**Abstract Methods** (must implement):
- `get_mail_record(mail: str) -> MailRecord`
- `disable_token(token: TokenDict) -> None`

**Public Methods**:
- `verify_token(token_v: str) -> User`: Verify token and return user (creates user if not exists)
- `verify_login_mail(request, token_v: str) -> None`: Verify and log user in

---

#### `EmailLogoutMixin`

**Location**: `django_login_email.email.EmailLogoutMixin`

**Purpose**: User logout functionality

**Public Methods**:
- `logout(request) -> None`: Log user out

---

### Models (🟢 Stable)

#### `EmailRecord`

**Location**: `django_login_email.models.EmailRecord`

**Purpose**: Store email verification tokens and status

**Fields**:
```python
class EmailRecord(models.Model):
    email: EmailField  # Unique
    expired_time: DateTimeField  # Token expiration time
    validated: BooleanField  # Whether token has been used
    mail_type: CharField  # "login" or "register"
    salt: CharField  # Token salt for validation
```

**Class Methods**:
- `set_email_expired_time(email: str, datetime) -> EmailRecord`: Update expiration time

**Instance Methods**:
- `set_expired_time(datetime) -> None`: Set expiration and reset validation

---

#### `IPBan`

**Location**: `django_login_email.models.IPBan`

**Purpose**: Store banned IP addresses

**Fields**:
```python
class IPBan(models.Model):
    ip: GenericIPAddressField  # Unique, supports IPv4 and IPv6
    reason: TextField  # Ban reason
    created_at: DateTimeField  # Ban timestamp
```

**Class Methods**:
- `add_ip_ban(ip: str, reason: str) -> IPBan`: Add or update IP ban

---

### Exceptions (🟢 Stable)

**Location**: `django_login_email.errors`

All exceptions inherit from `LoginMailError`:

```python
class LoginMailError(Exception):
    """Base exception for login email errors"""

class ValidatedError(LoginMailError):
    """Token has already been validated"""

class TokenError(LoginMailError):
    """Token is invalid or expired"""

class RateLimitError(LoginMailError):
    """Rate limit exceeded"""

class InactiveUserError(LoginMailError):
    """User account is inactive"""

class EmailSendError(LoginMailError):
    """Email sending failed"""
```

**Usage**:
```python
from django_login_email import errors

try:
    self.send_login_mail(email)
except errors.RateLimitError as e:
    # Handle rate limiting
    pass
except errors.EmailSendError as e:
    # Handle email failure
    pass
```

---

### Forms (🟢 Stable)

#### `LoginForm`

**Location**: `django_login_email.forms.LoginForm`

**Fields**:
- `email`: EmailField (required)

**Validation**:
- Email format validation
- No additional custom validation

---

### Utilities (🟡 Provisional)

#### `IPBanUtils`

**Location**: `django_login_email.iputils.IPBanUtils`

**Purpose**: IP banning utilities

**Methods**:
- `get_client_ip(request: HttpRequest) -> str`: Extract client IP from request
- `is_ip_banned(ip: str) -> bool`: Check if IP is banned
- `ban_ip(ip: str, reason: str) -> None`: Ban an IP address

**Note**: IP banning logic may be enhanced in future versions.

---

### Token Management (🔴 Internal)

**Location**: `django_login_email.token`

These classes are used internally and should NOT be directly instantiated:

- `TokenManager`: Handles token encryption/decryption
- `TokenGenerator`: Generates time-limited tokens
- `TokenDict`: TypedDict for token structure

**Rationale**: Token implementation details may change for security improvements.

**If you need custom tokens**: Override methods in `EmailFunc` and `EmailVerifyMixin` instead.

---

## Data Classes (🟢 Stable)

### `TimeLimit`

**Location**: `django_login_email.email.TimeLimit`

**Purpose**: Configure rate limiting

**Attributes**:
```python
@dataclass
class TimeLimit:
    minutes: int = 10  # Minutes between allowed emails
```

**Example**:
```python
from django_login_email.email import TimeLimit

class MyLoginView(EmailLoginView):
    tl = TimeLimit(minutes=5)  # 5 minute rate limit
```

---

### `MailRecord`

**Location**: `django_login_email.email.MailRecord`

**Purpose**: Data class for email record information

**Attributes**:
```python
@dataclass
class MailRecord:
    expired_time: Optional[datetime]
    email: str
    validated: bool
    salt: str
```

**Note**: This is returned by `get_mail_record()` abstract method.

---

## Deprecation Policy

When we need to make breaking changes:

1. **Minor Version**: Mark as deprecated with warnings
   ```python
   warnings.warn("old_method() is deprecated, use new_method()", DeprecationWarning)
   ```

2. **Next Minor Version**: Continue showing warnings

3. **Major Version**: Remove deprecated functionality

**Minimum Deprecation Period**: 2 minor versions or 6 months, whichever is longer.

---

## Version Migration Examples

### 0.6.2 → 0.6.3: Renaming `set_token` to `build_message`

**Breaking Change**: YES (method rename)

**Migration**:
```python
# Old (0.6.1 and earlier)
email_info.set_token(token)

# New (0.6.2+)
email_info.build_message(token)
```

**Note**: This change did NOT follow proper deprecation policy. Future changes will include deprecation warnings.

---

## Extending the API

For guidance on extending functionality, see:
- [Extension Points](./extension-points.md)
- [Configuration Reference](./configuration-reference.md)
