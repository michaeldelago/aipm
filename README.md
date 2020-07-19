# AIPM
## A Package Manager for AppImages
-  scrapes appimages.github.io/apps, and creates a small download manager for these


### Usage
`aipm install appimage`
- install a package

`aipm search search_term`
- search for a package

`aipm import -f library.json`
- import a JSON in library format

`aipm export`
- export to `library.json` in the current working dir

`aipm scrape`
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
```