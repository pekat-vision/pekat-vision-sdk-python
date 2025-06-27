# Changelog

## [2.3.2] - 2025-06-27

### Fixed

- Create attributes before an exception can be raised. PR [#42](https://github.com/pekat-vision/pekat-vision-sdk-python/pull/42) by [@Adamasterr](https://github.com/Adamasterr).

## [2.3.1] - 2025-06-24

### Fixed

- Replace atexit registers with method calls in `__del__`. PR [#40](https://github.com/pekat-vision/pekat-vision-sdk-python/pull/40) by [@ondrej-from-pekat](https://github.com/ondrej-from-pekat).
- Add try catch around version parse. PR [#38](https://github.com/pekat-vision/pekat-vision-sdk-python/pull/38) by [@ondrej-from-pekat](https://github.com/ondrej-from-pekat).

## [2.3.0] - 2025-02-24

### Changed

- Use requests.Session for improved performance in Instance class. PR [#34](https://github.com/pekat-vision/pekat-vision-sdk-python/pull/34) by [@pololanik](https://github.com/pololanik).

## [2.2.0] - 2025-01-14

### Changed

- Use shared memory for analyzing locally. PR [#33](https://github.com/pekat-vision/pekat-vision-sdk-python/pull/33) by [@Adamasterr](https://github.com/Adamasterr).

## [2.1.0] - 2024-10-08

### Added

- Add `send_random` method to `Instance`. PR [#27](https://github.com/pekat-vision/pekat-vision-sdk-python/pull/27) by [@Adamasterr](https://github.com/Adamasterr).

### Changed

- Create a random number generator in `__init__`. PR [#30](https://github.com/pekat-vision/pekat-vision-sdk-python/pull/30) by [@Adamasterr](https://github.com/Adamasterr).

### Fixed

- Fix `AttributeError` when stopping a remote `Instance / Analyzer`. PR [#26](https://github.com/pekat-vision/pekat-vision-sdk-python/pull/26) by [@Adamasterr](https://github.com/Adamasterr)

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

[2.3.2]: https://github.com/pekat-vision/pekat-vision-sdk-python/releases/tag/v2.3.2
[2.3.1]: https://github.com/pekat-vision/pekat-vision-sdk-python/releases/tag/v2.3.1
[2.3.0]: https://github.com/pekat-vision/pekat-vision-sdk-python/releases/tag/v2.3.0
[2.2.0]: https://github.com/pekat-vision/pekat-vision-sdk-python/releases/tag/v2.2.0
[2.1.0]: https://github.com/pekat-vision/pekat-vision-sdk-python/releases/tag/v2.1.0
[2.0.0]: https://github.com/pekat-vision/pekat-vision-sdk-python/releases/tag/v2.0.0
