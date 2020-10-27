#!/bin/bash

display_usage() {
    echo "This script will save the ID, and labels of the Brainhack Global projects for the given event.\n"
    echo "Usage:"
    echo "\tsh pull_issues.sh OUTPUT EVENT (REPO)\n"
    echo "Arguments:\n"
    echo "\tOUTPUT [required]: Path to store the output file. It can also be a filename. It must have the '.tsv' extension.\n"
    echo "\tEVENT [required]: Label of the Brainhack Global event to pull project data from. It must start by 'bhg:'.\n"
    echo "\tREPO [optional]: Path to global 2020 repository. Usefule if you do not want to clone the repository again."
    echo "\tIf this argument is not given, the script will clone the repository and delete it once the script finishes.\n"
    echo "Help:\n"
    echo "\tYou can display this help message using the '-h' and '--help' flags as in:\n"
    echo "\t'pull_issues.sh -h' or 'pull_issues.sh --help'"
} 

# If no arguments are supplied, display usage.
if [  $# -le 1 ]
then
    display_usage
    exit 1
fi

# Check whether user supplied -h or --help . If yes, display usage.
if [[ ( $* == "--help") ||  $* == "-h" ]]
then
    display_usage
    exit 0
fi

# Filename of output file (it can include the path).
OUTFILE=$1
# Event label.
EVENT=$2
# Path to the repository. It can be empty
REPOPATH=$3

# If REPOPATH is given then move into that directory and if it is not given then
# clone Brainhack Global 2020 repository to get project info and move into directory.
if [ $# -eq 3 ]
then
    echo "Moving into ${REPOPATH}"
    DIR_EXISTS=true
    cd ${REPOPATH}
else
    echo "The global2020 directory could not be found..."
    DIR_EXISTS=false
    git clone https://github.com/brainhackorg/global2020
    cd global2020
fi

# Get ID of projects on GitHub issues.
ISSUE_ID_LIST=$(gh issue list -L 1000 -l "${EVENT}"| awk '{print $1}')

# Create output file and add header.
echo "ID    LABELS \n" > ${OUTFILE}

echo "Pulling data from project issues... "

# Loop throuh found issues.
for ISSUE_ID in $ISSUE_ID_LIST
do
    # Get project labels.
    LABELS_LIST=$(gh issue view "${ISSUE_ID}" | grep 'labels:' | cut -d':' -f2)

    # Only save the issue if the issue has the project and (web_ready or published) labels.
    if [[ ${LABELS_LIST} == *project* ]] && [[ ${LABELS_LIST} == *status:web_ready* || ${LABELS_LIST} == *status:published* ]]
    then
        # Save ID, title and labels to output file.
        echo "${ISSUE_ID##*( )}    ${LABELS_LIST##*( )}\n" >> ${OUTFILE}
    fi
done

# Leave directory.
cd ..

# Check if filename has a slash (path). Move the file one directory up if it's just a filename.
if [[ "${OUTFILE}" != *\/*  ]] || [[ "${OUTFILE}" != *\\* ]]
then
    echo "An absolute path for the output file was not provided."
    echo "Moving output file one directory up..."
    mv global2020/${OUTFILE} .
    CURRENT_DIR=$(pwd)
    OUTFILE=$(echo "${CURRENT_DIR}/${OUTFILE}")
fi

# Do not remove directory if it already existed.
if ! ${DIR_EXISTS}
then
    echo "Removing cloned repository..."
    rm -rf global2020
fi

echo "Projects data saved in ${OUTFILE}"