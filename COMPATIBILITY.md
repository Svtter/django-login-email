# Compatibility

## Supported Versions

### Python

- **Minimum**: Python 3.10
- **Recommended**: Python 3.12
- **Tested**: 3.10, 3.11, 3.12

### Django

- **Minimum**: Django 5.0.4
- **Tested**: Django 5.0.x
- **Future**: Will support Django 5.1+ when released

### Databases

- **SQLite**: ✅ Fully supported (development)
- **PostgreSQL**: ✅ Fully supported (recommended for production)
- **MySQL/MariaDB**: ✅ Supported via Django ORM (not explicitly tested)

## Quick Compatibility Check

```python
# Check your versions
python --version  # Should be >= 3.10
python -m django --version  # Should be >= 5.0.4
```

## Version Support Policy

- **Active support**: Latest stable release (0.6.x)
- **Security patches**: Backported to current major version
- **EOL**: When 2 major versions behind

## Detailed Information

For complete compatibility information, including:
- Database compatibility matrix
- Email backend support
- Web server compatibility
- Breaking changes history

See: [docs/requirements/compatibility-matrix.md](./docs/requirements/compatibility-matrix.md)

## Reporting Issues

If you encounter compatibility issues:

1. Check [compatibility-matrix.md](./docs/requirements/compatibility-matrix.md) for known issues
2. Search [GitHub Issues](https://github.com/Svtter/django-login-email/issues)
3. Create a new issue with:
   - Python version
   - Django version
   - Database backend
   - Error traceback
