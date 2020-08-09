# Changelog

### 0.6

- Logging revisited (though a work in progress)

- Ratelimit checks for GitHub API calls

- Small bug in Download progress showing 4 instead of the growing downloaded amount

- Refactored appimagelibrary.update to be more "functional" (use that loosely)
  
  - Uses map/filter instead of loops

- 

### 0.5

- Uses proper feed.json (Issue #1)
  
  - adds `update` action, deprecates `scrape`

- better handling for issues with invalid github links

- Added support for the download link being with OpenSuse mirrors

- slightly cleaned up appimage downloading method, though it's not perfect

### 0.4

- update config file formatting

- Bugfix if the AppImage isn't the first download

- empty `search` results has better message

- rudimentary install script added

### 0.3

- Fixed Typos in README.md

- Set the Downloads directory to be in bin, with a hidden file ".apps"
  
  - Makes it easier to have the AppImages as user-specific executables

### 0.2

- If no options are selected, show the help (though I believe argparse already does this)
  
  - uses long args because it looks "gooder"

### 0.1

- Initial Commit
