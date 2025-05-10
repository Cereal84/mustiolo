# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]
### Added
- Support for multiple border styles (`SINGLE_ROUNDED`, `SINGLE_RECTANGLE`, etc.).
- Capture exceptions during command execution and print an error
- Override command name, short help via decorator argument

### Changed
- Improved `_handle_line` logic to reduce code repetition.
- Optimized string concatenation in `draw_message_box` by using `join`.

### Fixed
- Fixed a bug where empty content caused rendering issues in the message box.

## [0.0.1] - 2025-05-07
### Added
- Initial release of the project with support for creating message boxes.
- Function `draw_message_box` to create customizable message boxes with borders.
- Automatic text wrapping based on the specified width.
