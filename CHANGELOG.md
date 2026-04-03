# Changelog


## [1.1.1] - 2026.04.03

### Added


### Changed
- Changed aiosqlite for postgresql for local development
- moved `main.py` out of app for simplier CLI control

### Fixed


## [1.1.0] - 2026.03.24

### Added
- Added a progress bar to next rank in `Player Profiles`
- Added core folder to better control backend components
- Added a Pydantic Settings model to better control dev/prod workflow
- Setup alembic migrations so future me can be happy

### Changed
- Changed python version since PROD is not caught up with 3.13/3.14
- README has been updated

### Fixed


## [1.0.2] - 2026.03.02

### Added

### Changed

### Fixed
- Fixed an issue preventing the registration of matches due to SQL Enums.
- Fixed an issue where ranks were not the same in `Home` page compared to `Player Profile` page.


## [1.0.1] - 2026.02.25

### Added

### Changed

### Fixed
- Fixed an issue where rank icons were not showing on `Player Profile` page.


## [1.0.0] - 2026.02.24

### Added
- First release of new Volleyball Tracker

### Changed
- Backend/Frontend Framework for a faster response
- Minor Changes to Frontend UI
- Points System was added (2 for a Win, 1 for an OTL and 0 for a Loss)
- More STATS (Average Points per Match and Efficiency Rating, Points Scored / Points Conceded)
- Seasons were added, now matches will take part in yearly seasons
- NEW Player Profiles with previous season delta
- NEW Rank System based on Average Points per match * Efficiency Rating (Only after 10 seasonal games played)
- Added User Registration for better control of Admin Privileges 

### Fixed
