#!bin/bash

ISSUE_ID_LIST=$(gh issue list -L 1000 | awk '{print $1}')

echo "ID \t TITLE \t LABELS \n" > projects.tsv

for ISSUE_ID in $ISSUE_ID_LIST
do
    TITLE=$(gh issue view "${ISSUE_ID}" | grep 'title:' | cut -d':' -f2)
    LABELS_LIST=$(gh issue view "${ISSUE_ID}" | grep 'labels:' | cut -d':' -f2)
    # echo ${TITLE##*( )}
    # echo ${LABELS_LIST##*( )}
    echo "${ISSUE_ID##*( )} \t ${TITLE##*( )} \t ${LABELS_LIST##*( )} \n" >> projects.tsv
done
