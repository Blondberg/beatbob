#!/bin/bash

VENV=venv # default name of virtual environment

setup() {
    echo "Creating virtual environment"
    python -m venv $VENV # create virtual environment
    activate
    echo "Installing necessary dependencies"
    pip install -r requirements.txt
    read -p "Please enter the project name (no spaces, leave empty to not create folder): " PROJECT_NAME
    if [ $PROJECT_NAME != "" ]
    then
        mkdir $PROJECT_NAME
        touch ./$PROJECT_NAME/__init__.py
    fi
}


clean() {
    deactivate
    echo "Doing some vacuuming... *whoosh whoosh*"
    rm -rf ./$VENV
    echo "Project cleaned"
}

setrequirements() {
    echo "Setting requirements"
    python -m pip freeze > requirements.txt
    echo "Requirements set"
}

activate() {
    echo "Activating virtual environment"
    source ./$VENV/Scripts/activate
    echo "To deactivate, run 'deactivate' in the terminal"
}

runpy() {
    echo "Looking for main file..."
    PATH_TO_GIT=$(git rev-parse --show-toplevel)
    PATH_TO_MAIN=$(find $PATH_TO_GIT -name "venv" -prune -name ".git" -prune -or -name "__main__.py")
    echo "Main file found!"
    echo "Running main file!"
    python -u $PATH_TO_MAIN
}

"$@"