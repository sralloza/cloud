# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
* Run tests on push.
* Add endpoints to ignore folders: `/ignore/<path>`, `/show-ignored`, `/unignore/<path>` and `/unignore-all`.
* If there is an error uploading files, the message will appear as a notification.
* Add links to `/cloud` below the files form.

### Changed
* The box below the files form is a link to `/clod`.

### Fixed
* Fixed issues with `PermissionErrors`.
* Fixed typo: *emtpy* -> *empty*.

### Removed
* Removed hyper link in cloud's title.

## [1.0.0] - 2019-07-18
### Added
* Add sudoers file to store admins.

### Changed
* Rename route `/m` to `/md`.
* Improve error messages.
* Improve config.
* Move `get_folders` and `get_sudoers` to `utils` module.

### Fixed
* Add tests.

[Unreleased]: https://github.com/sralloza/flask-web/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/sralloza/flask-web/releases/tag/v1.0.0
