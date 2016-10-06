# Change Log

## [0.2.0] - 2016-10-06

### Changed

- Changes internals to be compatible with the latest Orator version.
- Automatically returns a 404 error when `ModelNotFound` is raised.
- Adds support for directly returning Orator objects.


## [0.1.1] - 2015-11-28

### Fixed

- `Orator` class no longer inherits from  `DatabaseManager` to avoid errors when setting up teardown context.

### Changed

- Automatically disconnects after a request.


## [0.1] - 2015-07-07

Initial release



[0.2.0]: https://github.com/sdispater/flask-orator/releases/tag/0.2.0
[0.1.1]: https://github.com/sdispater/flask-orator/releases/tag/0.1.1
[0.1]: https://github.com/sdispater/flask-orator/releases/tag/0.1
