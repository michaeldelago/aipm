#!/bin/bash

main () {
    BASECONFLOCATION="/home/$USER/.config/aipm.yaml"

    [[ -f aipm-sample.yaml ]] && cp "./aipm-sample.yaml" "$BASECONFLOCATION"
    sed -i "s/USERNAME/$USER/g" "$BASECONFLOCATION" && \
        printf "User set as: %s \n" "$USER"

    read -rp "What is your GitHub username? (leave blank for none)" gh_login
    [[ "$gh_login" =~ .+ ]] && sed -i "s/ghlogin/$gh_login/g" "$BASECONFLOCATION" && \
        printf "GitHub username set to: %s" "$gh_login"

    read -rp "What is your GitHub api token? (leave blank for none)" gh_token
    [[ "$gh_token" =~ .+ ]] && sed -i "s/ghtoken/$gh_token/g" "$BASECONFLOCATION" && \
        printf "GitHub API token set to: %s" "$gh_token"

    [[ -d "/home/$USER/bin" ]] && ln -s "/home/$USER/bin/aipm" "$(pwd)/aipm.py" && \
        printf "aipm installed to: %s" "/home/$USER/bin"
    [[ ! -d "/home/$USER/bin" ]] && \
        printf "Location doesn't exist: %s" "/home/$USER/bin"

    printf "Ok, you should be good to go - The last step is to import the JSON, with the command: \n\n\t%s\n\nAfter this, you should be able to use the application as normal" "aipm import -f library.json"
}

main