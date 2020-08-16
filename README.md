# AIPM - A Package Manager for AppImages

###### Scrapes [appimage.github.io/apps](appimage.github.io/apps), and creates a small download manager for these

### Usage

`aipm install appimage`

- install a package
  `aipm uninstall appimage`
- uninstalls all versions of package
  `aipm clean [appimage|all]`
- remove older versions of AppImages

`aipm search search_term`

- search for a package
  `aipm import -f library.json`
  
- import a JSON in library format
  `aipm export`
  
- export to `library.json` in the current working dir
  `aipm update`
  
- Pulls the library from
  `aipm scrape`[Deprecated]
  
- generate the library manually
  
- requires `gh_login` and `gh_token` to be set in configuration
  

`aipm -h`

- shows you the same thing as above
  
  ### Installation
  
  ```
  

1. clone repo
  
2. install python dependencies
  pip install -r requirements.txt
  
3. symlink aipm
  ln -s /path/to/repo/aipm.py /home/USER/bin/aipm
  
4. configure application (edit aipm-sample.yaml, and move it to /home/USER/.config/aipm.yaml)
  
5. import library
  aipm import -f /path/to/repo/library.json
  OR
  aipm update
  ```
  
  ### Notes
  

- Created when I started using Fedora Silverblue
  
  - Immutable OS, favors applications that are installed via AppImage or Flatpak
    
  - It's super cool and suprisingly usable, I'd recommend looking into it.
    
- I found shortcomings with a similar project, [spm](https://github.com/simoniz0r/spm)
  
  - funnily enough, you can actually download spm (as an AppImage) with this tool.
    
- I just wanted a simple tool to install AppImages as needed
  
  - I also wanted to write it
    
- I thought it would be cool to pull a list of AppImages from an "official" resource
  
- Before this project, I had no clue how webscraping worked. Turns out it's really easy :E
  
- I chose shelve as a db because it's lightweight, and has a great context manager
  
  - I don't feel that a full sqlite3 db is necessary for a database so small/simple
    

### Shortcomings

- There is no rollback (though older versions aren't deleted when new ones are installed)
  
- If installation through `aipm` isn't working, it's always worth a google search for the project instead
  
- AppImages and Flatpaks are better and worse than eachother in their own ways.
  

### Known Bugs/ToDo

- There is sometimes an issue with KeyErrors on the shelve db, due to the way a json can be imported (i think?)
  
  - This would potentially be solved by switching to sqlite3
    
  - Workaround for this is to run an update command
    
- Implement "upgrade" command
  
  - It should only install a package if there's a newer version
    
  - ideally, if the release cycle is "continuous", it should always download the new version