# Changelog

### 0.7

- Downloads from OpenSuse's repo's are versioned as "continuous"
  
- AppImage.installedVersion is now a list of installed versions
  
- Added uninstall function
  
- added clean function (remove old versions of a program)
  

### 0.6.5

- Fixed bug that caused AppImages with "Install" links instead of "Download" links to fail on pulling data, such as [Joplin](https://appimage.github.io/Joplin/)

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