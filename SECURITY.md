# Security Policy

## Supported Versions

Security updates are provided for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 0.6.x   | :white_check_mark: |
| < 0.6   | :x:                |

## Reporting a Vulnerability

**Please do NOT report security vulnerabilities through public GitHub issues.**

### How to Report

To report a security vulnerability, please email:

**svtter@qq.com**

Please include:

1. **Description** of the vulnerability
2. **Steps to reproduce** the issue
3. **Potential impact** assessment
4. **Suggested fix** (if available)

### What to Expect

- **Initial Response**: Within 48 hours
- **Status Update**: Within 7 days with assessment
- **Fix Timeline**: Depends on severity
  - Critical: Within 7 days
  - High: Within 30 days
  - Medium: Within 90 days
  - Low: Next minor release

### Disclosure Policy

- We will coordinate disclosure with you
- Security advisories will be published on GitHub
- Credit will be given to reporters (unless you prefer to remain anonymous)

## Security Features

### Token Security

- **Encryption**: AES-EAX mode (authenticated encryption)
- **Key Source**: Django's `SECRET_KEY` (first 32 bytes)
- **Expiration**: Time-limited tokens (default: 10 minutes)
- **One-time Use**: Tokens are invalidated after successful login
- **Salt**: Random salt prevents token reuse across sessions

### Rate Limiting

- **Time-based**: Prevents email flooding (default: 10 minutes between emails)
- **IP Banning**: Automatic banning for abusive IPs
- **Validation**: Tokens can only be validated once

### User Account Security

- **Inactive Users**: `is_active=False` users cannot login
- **Email Verification**: Users must verify email to complete registration
- **No Password Storage**: Passwordless authentication (no password vulnerabilities)

## Security Best Practices

### For Users of This Package

1. **SECRET_KEY Management**
   ```python
   # ✅ Good - use environment variable
   SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')

   # ❌ Bad - hardcoded
   SECRET_KEY = "my-secret-key-123"
   ```

2. **Email Security**
   ```python
   # ✅ Good - use TLS
   EMAIL_USE_TLS = True
   EMAIL_PORT = 587

   # ❌ Bad - unencrypted
   EMAIL_USE_TLS = False
   EMAIL_PORT = 25
   ```

3. **HTTPS in Production**
   ```python
   # settings/production.py
   SECURE_SSL_REDIRECT = True
   SESSION_COOKIE_SECURE = True
   CSRF_COOKIE_SECURE = True
   ```

4. **Token Expiration**
   ```python
   # ✅ Good - short expiration
   tl = TimeLimit(minutes=10)

   # ⚠️ Risky - too long
   tl = TimeLimit(minutes=1440)  # 24 hours
   ```

5. **Verify URL Security**
   ```python
   # ✅ Good - HTTPS in production
   class ProductionLoginInfo(EmailLoginInfo):
       def __init__(self):
           super().__init__()
           self.url = "https://myapp.com/account/verify?token="

   # ❌ Bad - HTTP allows token interception
   self.url = "http://myapp.com/account/verify?token="
   ```

### Security Checklist

Before deploying to production:

- [ ] `SECRET_KEY` is at least 32 characters and stored securely
- [ ] `DEBUG = False` in production
- [ ] Email uses TLS/SSL encryption
- [ ] Verify URLs use HTTPS
- [ ] Token expiration is set appropriately (10-15 minutes recommended)
- [ ] Rate limiting is enabled
- [ ] Django security middleware is active
- [ ] Database credentials are secured
- [ ] CSRF protection is enabled

## Known Security Considerations

### Token Security Model

**Assumptions:**
- Django's `SECRET_KEY` remains secret
- HTTPS is used in production (tokens in URL parameters)
- Email transport is reasonably secure (TLS to mail server)
- User's email account is secure

**Threats Mitigated:**
- ✅ Token replay attacks (one-time use + salt)
- ✅ Token forgery (AES encryption with secret key)
- ✅ Brute force (rate limiting + IP banning)
- ✅ Token expiration (time-limited validity)

**Threats NOT Mitigated:**
- ❌ Email account compromise (if attacker has email access, they can login)
- ❌ SECRET_KEY compromise (invalidates all security)
- ❌ MITM attacks if not using HTTPS
- ❌ Physical access to user's device with active session

### IP Banning Limitations

- IP bans are stored in database (can be bypassed by changing IP)
- IPv6 support means many IPs per device
- Shared IPs (corporate, VPN) may affect legitimate users
- No automatic un-banning mechanism

### Email Security

- Email is not end-to-end encrypted
- Email servers may log token URLs
- Email may be forwarded or accessed by others

## Secure Configuration Examples

### Minimal Secure Production Config

```python
# settings/production.py
import os

# Core security
SECRET_KEY = os.environ['DJANGO_SECRET_KEY']
DEBUG = False
ALLOWED_HOSTS = ['myapp.com', 'www.myapp.com']

# HTTPS
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Email
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ['EMAIL_HOST']
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ['EMAIL_HOST_USER']
EMAIL_HOST_PASSWORD = os.environ['EMAIL_HOST_PASSWORD']
```

### Secure View Configuration

```python
from django_login_email import views, email

class SecureLoginInfo(email.EmailLoginInfo):
    system_name = "MyApp"

    def __init__(self):
        super().__init__()
        self.from_email = settings.EMAIL_HOST_USER
        # Use HTTPS for verification URL
        self.url = "https://myapp.com/account/verify?token="

class SecureLoginView(views.EmailLoginView):
    login_info_class = SecureLoginInfo
    register_info_class = SecureRegisterInfo
    tl = email.TimeLimit(minutes=10)  # Short expiration

    # Additional security: log attempts
    def send_login_mail(self, email: str):
        logger.info(f"Login attempt for {email} from {self.get_client_ip(self.request)}")
        super().send_login_mail(email)
```

## Security Audits

This package has NOT undergone formal security audit.

**Contributions welcome:**
- Security code review
- Penetration testing
- Formal verification of cryptographic implementation

## Dependencies Security

Monitor dependencies for vulnerabilities:

```bash
# Check for known vulnerabilities
pip install safety
safety check

# Or use GitHub's Dependabot (enabled in this repo)
```

**Critical Dependencies:**
- `pycryptodome`: Keep updated for crypto security patches
- `Django`: Follow Django security announcements

## Security Roadmap

### Planned Security Enhancements

- [ ] Formal security audit
- [ ] CAPTCHA support for rate limiting
- [ ] Webhook for suspicious activity
- [ ] Token rotation mechanism
- [ ] Enhanced IP ban strategies (temporary bans, graduated responses)
- [ ] Security headers middleware
- [ ] Audit logging

### Research Areas

- [ ] Academic proof of security model (mentioned in README)
- [ ] Formal threat modeling documentation
- [ ] Comparison with other passwordless auth methods

## Responsible Disclosure Examples

We appreciate responsible disclosure. Past examples (none yet, but format):

### Example Format

**CVE-YYYY-XXXXX** - Token Validation Bypass

- **Severity**: High
- **Affected Versions**: < 0.6.0
- **Fixed In**: 0.6.1
- **Reported By**: John Doe
- **Description**: Brief description
- **Mitigation**: Upgrade to 0.6.1+

## Additional Resources

- [Django Security Documentation](https://docs.djangoproject.com/en/stable/topics/security/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)

## Contact

For security concerns: **svtter@qq.com**

For general issues: [GitHub Issues](https://github.com/Svtter/django-login-email/issues)
