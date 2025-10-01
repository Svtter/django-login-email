# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Django Login Email is a Django package that enables passwordless authentication through email links. Users can register and login by clicking a time-sensitive link sent to their email address. The package includes security features like rate limiting, IP banning, and token validation.

## Development Commands

### Project Setup
- **Install dependencies**: `pdm install` (uses PDM as package manager)
- **Install in development mode**: `pip install -e .`

### Testing
- **Run all tests**: `pytest` (uses pytest-django)
- **Run specific test file**: `pytest tests/test_models.py`
- **Run with verbose output**: `pytest -v`
- **Test settings module**: Configured in `pyproject.toml` as `settings.settings`

### Code Quality
- **Lint code**: `ruff check .`
- **Format code**: `ruff format .`
- **Line length**: 90 characters (configured in pyproject.toml)

### Django Management
- **Run migrations**: `python manage.py migrate`
- **Create migrations**: `python manage.py makemigrations`
- **Run development server**: `python manage.py runserver`
- **Create superuser**: `python manage.py createsuperuser`

### Documentation
- **Build docs**: `cd docs && make html`
- **Clean docs**: `cd docs && make clean`

### Email Testing
- **Start MailHog for email testing**: `docker run -d --name mailhog -p 1025:1025 -p 8025:8025 mailhog/mailhog`
- **MailHog web interface**: http://localhost:8025

## Architecture

### Core Components

1. **Email System** (`django_login_email/email.py`)
   - `EmailInfo`: Base class for email configuration
   - `EmailLoginInfo`/`EmailRegisterInfo`: Specific implementations for login/register emails
   - `EmailFunc`: Handles email sending logic and user existence checking
   - `EmailVerifyMixin`: Handles token verification and user login
   - `EmailLogoutMixin`: Handles user logout

2. **Token Management** (`django_login_email/token.py`)
   - `TokenManager`: Encrypts/decrypts email tokens using AES
   - `TokenGenerator`: Creates time-limited tokens with salt
   - Tokens contain email, expiration time, salt, and mail type
   - Uses Django's `SECRET_KEY` for encryption

3. **Models** (`django_login_email/models.py`)
   - `EmailRecord`: Tracks sent emails and validation status
   - `IPBan`: Blocks IPs that send too many emails
   - Includes rate limiting and expiration logic

4. **Views** (`django_login_email/views/`)
   - `EmailLoginView`: Handles login form and email sending
   - `EmailVerifyView`: Handles email link verification
   - `EmailLogoutView`: Handles logout
   - `HomeView`: Protected home page example

5. **Security Features**
   - Rate limiting via `LoginTimeLimit` (default 10 minutes)
   - IP banning for abusers (`iputils.py`)
   - One-time use tokens
   - Token expiration validation

### Key Patterns

- **Abstract Base Classes**: Uses ABC pattern for `MailRecordAPI` to enforce database operations
- **Mixin Pattern**: Multiple mixins for different functionalities (email, verification, logging)
- **Class-based Views**: All views use Django's class-based view architecture
- **Settings Integration**: Relies on Django's email settings for SMTP configuration

### Customization Points

- **Email Templates**: Override `login_info_class` and `register_info_class` in views
- **Time Limits**: Configure via `LoginTimeLimit` instance
- **User Model**: Works with any Django user model via `get_user_model()`
- **URL Patterns**: Configurable verification URLs in email templates

## Testing Structure

- **Unit Tests**: Individual component tests in `tests/`
- **Integration Tests**: Full workflow tests in `tests/ft/`
- **View Tests**: Specific view testing in `tests/views/`
- **Test App**: `testapp/` provides example implementation

## Configuration

Key settings are in `settings/settings.py`:
- Email server configuration (uses MailHog by default for development)
- Database (SQLite by default, PostgreSQL config available)
- Logging configuration for debugging
- `SECRET_KEY` used for token encryption

## Package Structure

The package follows Django app conventions with:
- Standard Django app structure (models.py, views.py, admin.py, etc.)
- Management commands for utility operations
- Migrations for database schema
- Templates for email and web pages
- Forms for user input validation