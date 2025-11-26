# Compatibility Matrix

This document defines the supported versions of Python, Django, and other dependencies for `django-login-email`.

## Current Version Support

**Package Version**: 0.6.4

### Python Support

| Python Version | Status | Notes |
|----------------|--------|-------|
| 3.13 | ✅ Supported | Tested and working |
| 3.12 | ✅ Supported | Tested and working |
| 3.11 | ✅ Supported | Tested and working |
| 3.10 | ✅ Supported | Minimum required version |
| 3.9 | ⚠️ Not Tested | May work but not officially supported |
| 3.8 and below | ❌ Not Supported | Will not work |

**Minimum Required**: Python 3.10

**Rationale**: Uses modern Python features including type hints, pattern matching capabilities, and improved typing support.

---

### Django Support

| Django Version | Status | Notes |
|----------------|--------|-------|
| 5.2 (upcoming) | 🔄 To Be Tested | Will test when released |
| 5.1 | ✅ Supported | Expected to work (not yet released at time of writing) |
| 5.0 | ✅ Supported | Minimum required version (5.0.4+) |
| 4.2 LTS | ⚠️ Not Tested | May work with modifications |
| 4.1 and below | ❌ Not Supported | Missing required features |

**Minimum Required**: Django 5.0.4

**Why 5.0.4 specifically?**
- Security patches from earlier 5.0 releases
- Stable email backend API
- Improved type hints support

**Future Compatibility**:
- We intend to maintain compatibility with the latest Django stable release
- Django 4.2 LTS support may be added in future if there is demand

---

### Database Support

The package uses Django ORM, so it supports all databases that Django supports:

| Database | Status | Tested | Notes |
|----------|--------|--------|-------|
| SQLite | ✅ Supported | ✅ Yes | Default for development |
| PostgreSQL | ✅ Supported | ✅ Yes | Recommended for production |
| MySQL | ✅ Supported | ⚠️ Not Tested | Should work via Django ORM |
| MariaDB | ✅ Supported | ⚠️ Not Tested | Should work via Django ORM |
| Oracle | 🤷 Unknown | ❌ No | Not tested, may work |

**Models Used**:
- `EmailRecord`: Standard fields, no database-specific features
- `IPBan`: Uses `GenericIPAddressField` (supports IPv4 and IPv6)

**Database-Specific Notes**:

**PostgreSQL**:
- ✅ Full support for all features
- ✅ IPv6 support in `IPBan.ip` field
- ✅ Efficient for large-scale deployments

**SQLite**:
- ✅ Works for development and small deployments
- ⚠️ IPv6 support depends on SQLite version
- ⚠️ Concurrent writes may have issues under high load

**MySQL/MariaDB**:
- ✅ Should work via Django ORM
- ⚠️ Ensure proper character set (utf8mb4) for email fields
- ⚠️ IPv6 support requires MySQL 5.6+ or MariaDB 10.0+

---

### Required Dependencies

| Dependency | Minimum Version | Current Tested | Purpose |
|------------|----------------|----------------|---------|
| Django | 5.0.4 | 5.0.4 | Web framework |
| pycryptodome | 3.20.0 | 3.20.0 | AES encryption for tokens |

**Why pycryptodome?**
- Provides AES encryption for token security
- More actively maintained than pycrypto
- No additional system dependencies

**Security Note**: Keep `pycryptodome` updated to receive security patches.

---

### Optional Dependencies

These are development dependencies, not required for using the package:

| Dependency | Purpose | Required For |
|------------|---------|-------------|
| pytest-django | Testing framework | Running tests |
| ipython | Interactive shell | Development |
| ruff | Linting and formatting | Code quality |
| sphinx | Documentation | Building docs |

---

### Email Backend Compatibility

The package uses Django's email framework and is compatible with:

| Email Backend | Status | Notes |
|---------------|--------|-------|
| SMTP (built-in) | ✅ Supported | Default, works with any SMTP server |
| Console (dev) | ✅ Supported | For development/testing |
| File (dev) | ✅ Supported | For development/testing |
| In-memory (test) | ✅ Supported | For unit testing |
| SendGrid | 🔄 Planned | Via django-anymail (future) |
| Mailgun | 🔄 Planned | Via django-anymail (future) |
| Amazon SES | 🔄 Planned | Via django-anymail (future) |
| django-templated-email | 🔄 Planned | Future enhancement |

**Current Limitation**: Email templates are defined in Python code (string.Template), not in separate template files.

**Future Plan**: Support for `django-templated-email` and `django-anymail` is planned (see README.md).

---

### Web Server Compatibility

As a Django app, it works with:

| Web Server | Status | Notes |
|------------|--------|-------|
| Django Dev Server | ✅ Supported | Development only |
| Gunicorn | ✅ Supported | WSGI, recommended for production |
| uWSGI | ✅ Supported | WSGI |
| Daphne | ⚠️ Not Tested | ASGI (async not used by this package) |
| Uvicorn | ⚠️ Not Tested | ASGI (async not used by this package) |

**Note**: This package does NOT use async features, so it works in both WSGI and ASGI deployments (in sync mode).

---

### Operating System Compatibility

| OS | Status | Notes |
|----|--------|-------|
| Linux | ✅ Supported | Primary development platform |
| macOS | ✅ Supported | Should work without issues |
| Windows | ⚠️ Not Tested | Should work, paths may need adjustment |
| Docker | ✅ Supported | Recommended deployment method |

---

## Version Support Policy

### Active Support

We actively support:
- Latest stable release (0.6.x)
- Django LTS releases when applicable
- Last 3 minor Python versions (currently 3.10, 3.11, 3.12)

### Security Patches

Security patches will be backported to:
- Current major version (0.x.x)
- Previous major version for 6 months after new major release

### End of Life

Versions are considered EOL when:
- 2 major versions behind (e.g., when 2.0.0 is released, 0.x.x becomes EOL)
- Underlying dependencies (Python, Django) reach EOL

---

## Compatibility Testing

### Current Test Matrix

Tests are run against:
- Python: 3.10, 3.11, 3.12
- Django: 5.0.4
- Database: SQLite (primary), PostgreSQL (secondary)

### Adding New Version Support

To request support for a new version:
1. Open an issue on GitHub
2. Specify the version and use case
3. We'll evaluate feasibility and demand

---

## Known Compatibility Issues

### Issue: Django 4.2 LTS

**Status**: Not officially supported

**Reason**: Code uses Django 5.0+ features

**Workaround**: May work with minor modifications, but not tested

**Future**: May add backport support if there is significant demand

---

### Issue: Async Django Views

**Status**: Package uses synchronous views

**Impact**: Works in ASGI apps but runs in sync mode

**Future**: Async support may be added in Django 6.0 release cycle

---

## Breaking Changes History

### Version 0.6.2
- **Change**: Renamed `set_token()` to `build_message()`
- **Impact**: Breaking change for custom email classes
- **Migration**: Update all `email_info.set_token(token)` to `email_info.build_message(token)`

---

## Dependency Version Constraints

Current constraints in `pyproject.toml`:

```toml
[project]
requires-python = ">=3.10"
dependencies = [
    "django>=5.0.4",
    "pycryptodome>=3.20.0",
]
```

**Note**: Upper bounds are NOT specified to allow compatibility with future versions. If a new Django or Python version breaks compatibility, we will:

1. Add upper bound temporarily
2. Release a patch with the constraint
3. Work on compatibility fix for next minor version

---

## Testing Against Multiple Versions

To test against different Python/Django versions:

```bash
# Using tox (if configured)
tox -e py310-django50
tox -e py312-django50

# Using pyenv
pyenv local 3.10.0
pip install django==5.0.4
pytest

pyenv local 3.12.0
pip install django==5.1.0
pytest
```

---

## Reporting Compatibility Issues

If you encounter compatibility issues:

1. Check this document for known issues
2. Search existing GitHub issues
3. Create a new issue with:
   - Python version (`python --version`)
   - Django version (`python -m django --version`)
   - Package version (`pip show django-login-email`)
   - Database backend
   - Error traceback

---

## Future Compatibility Goals

### Short-term (Next 6 months)
- [ ] Test and certify Django 5.1 compatibility
- [ ] Test Python 3.13 compatibility
- [ ] Add MySQL/MariaDB to test matrix

### Medium-term (Next 12 months)
- [ ] Django 4.2 LTS backport (if requested)
- [ ] django-anymail integration
- [ ] ASGI async view support

### Long-term
- [ ] Django 6.0 support when released
- [ ] Python 3.14 support when released
