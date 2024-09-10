# Changelog

### Added

- Add `send_random` method to `Instance`. PR [#27](https://github.com/pekat-vision/pekat-vision-sdk-python/pull/27) by [@Adamasterr](https://github.com/Adamasterr).

## [2.0.0] - 2024-07-08

_If you are upgrading: please see [`UPGRADING.md`](UPGRADING.md)._

### Added

- Add [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/) documentation.
- Add `"image"` to allowed response types.
- Add docstrings to errors.
- Add named parameters to some errors.

### Changed

- **Breaking**: Change minimal python version to 3.8.
- **Breaking**: Move `Instance` to `instance.py`.
- **Breaking**: Move errors to `errors.py`.
- **Breaking**: Change return type of `Instance.analyze` to new type `Result(NamedTuple)`.
- Change docstring style to `google`.
- Simplify `README.md`.

### Removed

- **Breaking**: Remove the `password` and `api_key` parameters.
- Remove unused `CannotBeTerminated` exception.

### Fixed

- Fix `Instance.stop()` method trying to stop an `already_running` project.
- Fix `Instance(already_running=False)` not searching default install dir on Linux.
- Fix project path not accepting `~` as a home directory.

[2.0.0]: https://github.com/pekat-vision/pekat-vision-sdk-python/releases/tag/v2.0.0
