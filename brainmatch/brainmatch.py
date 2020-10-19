#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import functools
import json
import operator

import pandas as pd


project_id_field = "ID"
project_title_field = "TITLE"
project_labels_field = "LABELS"

email_address_field = "email_address_field"

experience_programming_languages_field = "experience_programming_languages_field"
experience_neuroscientific_techniques_field =  "experience_neuroscientific_techniques_field"
experience_neurosoftware_field = "experience_neurosoftware_field"
experience_methods_field = "experience_methods_field"

experience_git_field = "experience_git_field"

desired_programming_languages_field = "desired_programming_languages_field"
desired_neuroscientific_techniques_field = "desired_neuroscientific_techniques_field"
desired_neurosoftware_field = "desired_neurosoftware_field"
desired_methods_field = "desired_methods_field"

necessary_indices = [email_address_field,
                     experience_programming_languages_field,
                     experience_neuroscientific_techniques_field,
                     experience_neurosoftware_field,
                     experience_methods_field,
                     experience_git_field,
                     desired_programming_languages_field,
                     desired_neuroscientific_techniques_field,
                     desired_neurosoftware_field,
                     desired_methods_field]

bhg_label = "bhg:"

git_skills_label = "git_skills:"
modality_label = "modality:"
programming_label = "programming:"
project_type_label = "project_type:"
project_tools_skills_label = "project_tools_skills:"
tools_label = "tools:"
topic_label = "topic:"

feature_keys = [git_skills_label, modality_label, programming_label,
                project_type_label, project_tools_skills_label,
                tools_label, topic_label]


def get_projects_features(project_data):

    project_features = dict.fromkeys(feature_keys)

    # ToDo
    # Get the data corresponding to each key from project_data

    return project_features


def match(projects_df, contributors_df):

    project_ids = list(map(str, projects_df[project_id_field].tolist()))
    columns = list([[email_address_field], project_ids])
    columns = functools.reduce(operator.iconcat, columns, [])

    match_df = pd.DataFrame(columns=columns)

    # Loop over contributors
    for contrib_index, contrib_data in contributors_df.iterrows():

        contrib_match = list([contrib_data[email_address_field]])

        # Loop over projects belonging to an event
        for proj_index, project_data in projects_df.iterrows():

            # Get the features for the project
            features = get_projects_features(
                project_data[project_labels_field])

            # ToDo
            # Match and score the expected fields
            contrib_match.append(proj_index)  # add some value for now

        match_df = match_df.append(
            pd.Series(contrib_match, index=columns), ignore_index=True)

    return match_df


def filter_event_projects(event, projects_df):

    project_labels = list(projects_df[project_labels_field])

    for proj_index, project_data in projects_df.iterrows():
        if event not in project_data[project_labels_field]:
            projects_df = projects_df.drop(proj_index)

    if projects_df.empty:
        raise ValueError("The script cannot continue.\n"
                         "No project has been assigned to your event:\n"
                         "Event: {}\nProjects' labels: {}\n"
                         "No project contains the label: {}\n".
                         format(event, project_labels, event))

    return projects_df


def check_necessary_contributor_data(contributors_df):

    indices = contributors_df.columns.tolist()

    missing = set(necessary_indices).difference(indices)

    if len(missing) != 0:
        raise ValueError("The script cannot continue.\n"
                         "Your contributor file is missing data:\n"
                         "Found: {}\nNecessary: {}\nMissing: {}".
                         format(indices, necessary_indices, list(missing)))


def normalize_contributors(contributors_df, contributor_fields):

    # Make sure headers do not have leading or trailing spaces.
    contributors_df.rename(columns=lambda x: x.strip(), inplace=True)

    contributors_df.rename(
        columns={y: x for x, y in contributor_fields.items()}, inplace=True)


def _build_arg_parser():

    parser = argparse.ArgumentParser(
        description="Project-contributor matching",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("bhg_event", type=str,
                        help="BHG event (e.g. bhg:donostia_esp_1).")
    parser.add_argument("in_projects_fname", type=str,
                        help="Input projects filename (.tsv).")
    parser.add_argument("in_contributors_fname", type=str,
                        help="Input contributor filename (.csv).")
    parser.add_argument("in_contributors_fields_fname", type=str,
                        help="Input contributors fields filename (.json).")
    parser.add_argument("out_match_fname", type=str,
                        help="Output match filename (.csv)")

    return parser


def main():

    # Parse arguments
    parser = _build_arg_parser()
    args = parser.parse_args()

    # projects_df = pd.read_csv(args.in_projects_fname, sep='\t')
    projects_df = pd.read_csv(args.in_projects_fname)
    contributors_df = pd.read_csv(args.in_contributors_fname)

    with open(args.in_contributors_fields_fname, 'r') as f:
        contributor_fields = json.load(f)

    # Normalize contributor data
    normalize_contributors(contributors_df, contributor_fields)

    # Check the contributor file contains all necessary fields
    check_necessary_contributor_data(contributors_df)

    # Filter projects not belonging to the event
    projects_df = filter_event_projects(args.bhg_event, projects_df)

    # Compute the project-contributor match
    match_df = match(projects_df, contributors_df)

    # Save data to a csv file
    match_df.to_csv(args.out_match_fname, index=False)


if __name__ == "__main__":
    main()
