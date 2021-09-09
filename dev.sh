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

activate() {
    echo "Activating virtual environment"
    source ./$VENV/Scripts/activate
    echo "To deactivate, run 'deactivate' in the terminal"
}

clean() {
    deactivate
    echo "Doing some vacuuming... *whoosh whoosh*"
    rm -rf ./$VENV
    echo "Project cleaned"
}

"$@"