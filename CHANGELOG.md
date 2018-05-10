# Changelog

## [0.1] - 2018-04-30
### Added
 - Standard command line interface
 - Standard file system
 - Standard command system, but with scripts and programs
 - List of preloaded programs, being the basic commands
 - User can create own scripts/programs

## [0.2] - 2018-05-10
### Added
 - Syncing functionality between the VFS and the file system on the disk
 - Current state is saved to the disk when shutdown and loaded on startup
 - Presets are stored externally and loaded on the first startup
 - More CLI functionality, including multiline support and comments
 - More commands, including logic and math operators and `clear`
### Changed
 - Programs and scripts are loaded from the file system, instead of internally
 - Improved output of `help` and `list` commands
 - Piping is more realistic; using a virtual stdin, rather than appending piped output to `argv`
### Removed
 - `script` and `prog` commands; use `/run` directory instead
### Fixed
 - Small CLI bugs
 - Constants work
