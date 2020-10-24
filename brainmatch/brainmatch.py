#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import functools
import json
import operator
import os

import pandas as pd

extension_sep = "."
top_match_label = "top"
underscore = "_"
label_separator = ","

project_top_id_label = "id"
score_id_label = "score"

project_id_field = "ID"
project_title_field = "TITLE"
project_labels_field = "LABELS"

email_address_field = "email_address_field"

experience_modality_field = "experience_modality_field"
experience_programming_field = "experience_programming_field"
experience_tools_field = "experience_tools_field"
experience_topic_field = "experience_topic_field"

experience_git_skills_field = "experience_git_skills_field"

desired_modality_field = "desired_modality_field"
desired_programming_field = "desired_programming_field"
desired_tools_field = "desired_tools_field"
desired_topic_field = "desired_topic_field"

necessary_indices = [email_address_field,
                     experience_modality_field,
                     experience_programming_field,
                     experience_tools_field,
                     experience_topic_field,
                     experience_git_skills_field,
                     desired_modality_field,
                     desired_programming_field,
                     desired_tools_field,
                     desired_topic_field]

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


def _generate_top_match_column_names(n):

    columns = []

    for i in range(n):
        project_top_id_col_name = \
            project_top_id_label + underscore + top_match_label + str(i+1)
        score_col_name = \
            score_id_label + underscore + top_match_label + str(i+1)
        columns.extend([project_top_id_col_name, score_col_name])

    return columns


def compute_top_n(match_df, n):

    ids = match_df.columns.tolist()
    project_count = len(ids[1:])
    top_match_col_names = _generate_top_match_column_names(
        n if n < project_count else project_count)
    columns = list([[email_address_field], top_match_col_names])
    columns = functools.reduce(operator.iconcat, columns, [])

    top_match = []

    # Loop over contributors and order project ids by their scores
    for _, data in match_df.iterrows():
        top_scores = data[1:].sort_values(ascending=False)
        top_data = \
            [x for y in zip(top_scores.index.tolist(), top_scores) for x in y]
        top_data = list([[data[0]], top_data])
        top_data = functools.reduce(operator.iconcat, top_data, [])
        top_match.append(top_data)

    top_match_df = pd.DataFrame(top_match, columns=columns)

    return top_match_df


def get_projects_features(project_data):

    project_features = dict.fromkeys(feature_keys)

    labels = project_data.split(label_separator)

    # Get the values from the labels corresponding to each feature
    for key in project_features.keys():
        project_features[key] = \
            [label.replace(key, "") for label in labels if key in label]

    return project_features


def compute_score(proj_features, contrib_data):

    score = 0

    # Assume that the integer indicating the skill is separated from the its
    # meaning by a whitespace
    contrib_git_skills = [int(s) for s in contrib_data[
        experience_git_skills_field].split(" ") if s.isdigit()][0]

    proj_git_skills = int(
        proj_features[git_skills_label].split(underscore)[0]
        if proj_features[git_skills_label] else -1)

    # Split the dataframe strings into lists
    contrib_experience_modality = \
        [s.strip() for s in contrib_data[experience_modality_field].split(",")]
    contrib_experience_programming = \
        [s.strip()
         for s in contrib_data[experience_programming_field].split(",")]
    contrib_experience_tools = \
        [s.strip() for s in contrib_data[experience_tools_field].split(",")]
    contrib_experience_topic = \
        [s.strip() for s in contrib_data[experience_topic_field].split(",")]

    contrib_desired_modality = \
        [s.strip() for s in contrib_data[desired_modality_field].split(",")]
    contrib_desired_programming = \
        [s.strip() for s in contrib_data[desired_programming_field].split(",")]
    contrib_desired_tools = \
        [s.strip() for s in contrib_data[desired_tools_field].split(",")]
    contrib_desired_topic = \
        [s.strip() for s in contrib_data[desired_topic_field].split(",")]

    # Compute the score corresponding to the contributor's git skills
    if contrib_git_skills >= proj_git_skills > 0:
        score += 1

    # Compute the scores corresponding to the contributor's experience
    experience_modality_match = list(
        set(proj_features[modality_label]) & set(contrib_experience_modality))
    score += len(experience_modality_match)

    experience_programming_match = list(
        set(proj_features[programming_label]) &
        set(contrib_experience_programming))
    score += len(experience_programming_match)

    experience_tools_match = list(
        set(proj_features[tools_label]) & set(contrib_experience_tools))
    score += len(experience_tools_match)

    experience_topic_match = list(
        set(proj_features[topic_label]) & set(contrib_experience_topic))
    score += len(experience_topic_match)

    # Compute the scores corresponding to the contributor's desired items
    desired_modality_match = list(
        set(proj_features[modality_label]) & set(contrib_desired_modality))
    score += len(desired_modality_match)

    desired_programming_match = list(
        set(proj_features[programming_label]) &
        set(contrib_desired_programming))
    score += len(desired_programming_match)

    desired_tools_match = list(
        set(proj_features[tools_label]) & set(contrib_desired_tools))
    score += len(desired_tools_match)

    edesired_topic_match = list(
        set(proj_features[topic_label]) & set(contrib_desired_topic))
    score += len(edesired_topic_match)

    return score


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
            proj_features = get_projects_features(
                project_data[project_labels_field])

            # Match and score the expected fields
            score = compute_score(proj_features, contrib_data)
            contrib_match.append(score)

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
    parser.add_argument("--n", type=int, default=5,
                        help="Top n.")

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

    # Compute the top n
    top_match_df = compute_top_n(match_df, args.n)

    path = os.path.dirname(args.out_match_fname)
    match_basename = os.path.basename(args.out_match_fname)
    rootname, ext = match_basename.split(extension_sep)
    top_basename = \
        rootname + underscore + top_match_label + extension_sep + ext
    top_fname = os.path.join(path, top_basename)

    # Save data to a csv file
    top_match_df.to_csv(top_fname, index=False)


if __name__ == "__main__":
    main()
