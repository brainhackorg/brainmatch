#!bin/bash

# Get ID of projects on GitHub issues.
ISSUE_ID_LIST=$(gh issue list -L 1000 -l "status:web_ready"| awk '{print $1}')

# Create output file and add header.
echo "ID \t TITLE \t LABELS \n" > projects.tsv

# Loop throuh found issues.
for ISSUE_ID in $ISSUE_ID_LIST
do
    # Get project title.
    TITLE=$(gh issue view "${ISSUE_ID}" | grep 'title:' | cut -d':' -f2)

    # Get project labels.
    LABELS_LIST=$(gh issue view "${ISSUE_ID}" | grep 'labels:' | cut -d':' -f2)

    # Save ID, title and labels to output file.
    echo "${ISSUE_ID##*( )} \t ${TITLE##*( )} \t ${LABELS_LIST##*( )} \n" >> projects.tsv
done
