# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).



## [Unreleased]
## 0.1.0 - 2017-07-26
### Added
- Tests: we can run tests for Maya
- Tests: added batch file which runs regular ktrack tests, kttk_widgets tests and maya tests (regular tests and maya tests)
- FileManagerWidget can now open and advance files
- Maya Engine: get qt_main_window
### Changed
- renamed ktrack_command to ktrack
### Fixed
- Context step was not validated correctly, now only accepts not None not empty strings or unicode
- FileManager OpenManager: now correclty calls engine to open file
- Maya Engine: now correctly sets project
- Maya Engine: has problems with os.path.expanduser("~"), now looks if on windows builds path by hand with os.environ['username]
## 0.0.1 - 2017-07-24
### Added
- This CHANGELOG file to hopefully serve as an evolving example
- __version__ to kttk