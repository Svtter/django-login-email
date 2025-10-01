# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.6.2] - 2024-10-01

### Added
- Version bump to 0.6.2

### Changed
- Renamed `set_token` to `build_message` for better clarity

### Fixed
- Fixed type error in the codebase

### Documentation
- Added Sphinx and related dependencies for documentation build
- Fixed docs build path in GitHub Pages deploy step
- Migrated Sphinx source to `docs/source` and updated RTD config
- Migrated Sphinx docs from `docs/source` to `docs` root

## [0.6.1] - 2024-09-30

### Fixed
- Fixed problem with from-email functionality

### Changed
- Updated README.md with improvements

## [0.6.0] - 2024-09-29

### Fixed
- Fixed missing request handling (#8)

### Added
- Documentation updates with new future features
- Added new related project information

## [0.5.0] - 2024-09-28

### Added
- IP ban functionality for preventing frequent email sending without login
- Version bump to 0.5.0 (#7)

### Changed
- Multiple README.md updates for better documentation

## [0.4.0] - 2024-09-27

### Fixed
- Fixed validate record functionality (#6)

### Added
- Made login and register views editable (#5)

## [0.3.0] - 2024-09-26

### Added
- Initial stable release
- Core email login and register functionality
- Time-limited login links
- Email sending rate limiting with TimeLimit
- One-time use login links
- Support for multiple users
- Configurable User model support

### Features
- [x] The developer could define their own `User` model
- [x] Time-limited of login link
- [x] Limited of sending email using TimeLimit to set minutes
- [x] The link could be used for Login once
- [x] Register new user
- [x] Support multiple user
- [x] Ban the IP to send mail frequently without login

### Planned Features
- [ ] Support [django-templated-email](https://github.com/vintasoftware/django-templated-email)
- [ ] Support Django Anymail
- [ ] Allow users to change their email address
- [ ] Enable 2FA
- [ ] More easier and customizable login link

---

## Related Project

- [django-email-verification](https://github.com/LeoneBacciu/django-email-verification)
- [django-login-with-email](https://github.com/wsvincent/django-login-with-email)
- [django-unique-user-email](https://github.com/carltongibson/django-unique-user-email)