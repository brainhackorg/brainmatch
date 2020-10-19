#!/bin/bash

# Filename of output file (it can include the path).
OUTFILE=$1

# Clone Brainhack Global 2020 repository to get project info and move into directory.
if [[ -d "global2020" ]]
then
    echo "global2020 directory found."
    DIR_EXISTS=true
else
    echo "The global2020 directory could not be found..."
    DIR_EXISTS=false
    git clone https://github.com/brainhackorg/global2020
fi

cd global2020

# Get ID of projects on GitHub issues.
ISSUE_ID_LIST=$(gh issue list -L 1000 -l "status:web_ready"| awk '{print $1}')

# Create output file and add header.
echo "ID \t TITLE \t LABELS \n" > ${OUTFILE}

echo "Pulling data from project issues... "

# Loop throuh found issues.
for ISSUE_ID in $ISSUE_ID_LIST
do
    # Get project title.
    TITLE=$(gh issue view "${ISSUE_ID}" | grep 'title:' | cut -d':' -f2)

    # Get project labels.
    LABELS_LIST=$(gh issue view "${ISSUE_ID}" | grep 'labels:' | cut -d':' -f2)

    # Save ID, title and labels to output file.
    echo "${ISSUE_ID##*( )} \t ${TITLE##*( )} \t ${LABELS_LIST##*( )} \n" >> ${OUTFILE}
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