#!/usr/bin/env python
# -*- coding: utf-8 -*-

import functools
import operator

import pandas as pd


top_match_label = "top"
underscore = "_"
label_separator = ","

project_top_id_label = "id"
score_id_label = "score"

project_id_field = "ID"
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
    """Generate top match column names to host information (project identifier
    and contributor score) about the best project fit of a contributor.

    Parameters
    ----------
    n : int
        Project identifier and score pair count to be generated.

    Returns
    -------
    columns : list
        Column names.

    Examples
    --------
    >>> n = 2
    >>> columns = _generate_top_match_column_names(n)
    >>> print(columns)
    ['id_top1', 'score_top1', 'id_top2', 'score_top2']
    """

    columns = []

    for i in range(n):
        project_top_id_col_name = \
            project_top_id_label + underscore + top_match_label + str(i+1)
        score_col_name = \
            score_id_label + underscore + top_match_label + str(i+1)
        columns.extend([project_top_id_col_name, score_col_name])

    return columns


def compute_top_n(match_df, n):
    """Compute the top-n project rank for each contributor in the matching
    data.

    Parameters
    ----------
    match_df : DataFrame
        Matching data.
    n : int
        Rank of the data to be kept.

    Returns
    -------
    top_match_df : DataFrame
        Top-n rank contributor matching data.
    """

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
        # Keep the top n results
        top_data = top_data[:len(columns)]
        top_match.append(top_data)

    top_match_df = pd.DataFrame(top_match, columns=columns)

    return top_match_df


def get_projects_features(project_data):
    """Get the project features under the form of a dictionary from the
    provided data string.

    Parameters
    ----------
    project_data : str
        Project data.

    Returns
    -------
    project_features : dict
        Project features.
    """

    project_features = dict.fromkeys(feature_keys)

    labels = project_data.split(label_separator)

    # Get the values from the labels corresponding to each feature
    for key in project_features.keys():
        project_features[key] = \
            [label.replace(key, "").strip()
             for label in labels if key in label]

    return project_features


def compute_feature_score(proj_feature, contrib_feature):
    """Compute the score of the contributor features with respect to the
    required project features. The score is computed as ratio of the number of
    features the contributor presents with respect to the number of features
    required by the project. The score is bounded in the range [0, 1]: a value
    of 0 means that the contributor does not present any of the features
    required by the project; a value of 1 means that the contributor presents
    all required features.

    Parameters
    ----------
    proj_feature : list
        Required project features.
    contrib_feature : list
        Contributor features.

    Returns
    -------
    score : float
        The contributor's score for the given project feature.
    """

    feature_match = list(set(proj_feature) & set(contrib_feature))

    # Avoid division by 0 if no feature was provided
    score = len(feature_match)/len(proj_feature) if len(proj_feature) else 0

    return score


def compute_total_score(proj_features, contrib_data):
    """Compute the total score of a given contributor with respect to the
    required project features. The total score is bounded in the [0, 1] range:
    a value of 0 means that the contributor does not present any of the
    features required by the project; a value of 1 means that the contributor
    presents all required features.

    Parameters
    ----------
    proj_features : dict
        Required project features.
    contrib_data : Series
        Contributor features.

    Returns
    -------
    float
        The contributor's score with respect to the required project features.
    """

    score = 0

    nzero_feature_count = sum(len(val) for val in proj_features.values())

    # Assume that the integer indicating the skill is separated from the its
    # meaning by a whitespace
    contrib_git_skills = [int(s) for s in contrib_data[
        experience_git_skills_field].split(" ") if s.isdigit()][0]

    # Sort the git skills labels in ascending order and take the highest skill
    # level if more than one git skill label are given to a project.
    proj_features[git_skills_label] = \
        sorted(proj_features[git_skills_label])[-1]

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
    score += compute_feature_score(proj_features[modality_label],
                                   contrib_experience_modality)

    score += compute_feature_score(proj_features[programming_label],
                                   contrib_experience_programming)

    score += compute_feature_score(proj_features[tools_label],
                                   contrib_experience_tools)

    score += compute_feature_score(proj_features[topic_label],
                                   contrib_experience_topic)

    # Compute the scores corresponding to the contributor's desired items
    score += compute_feature_score(proj_features[modality_label],
                                   contrib_desired_modality)

    score += compute_feature_score(proj_features[programming_label],
                                   contrib_desired_programming)

    score += compute_feature_score(proj_features[tools_label],
                                   contrib_desired_tools)

    score += compute_feature_score(proj_features[topic_label],
                                   contrib_desired_topic)

    return score/nzero_feature_count


def match(projects_df, contributors_df):
    """Compute the contributor to project matching. Provides a score
    determining the fit or match of a given contributor with respect to the
    event projects.

    Parameters
    ----------
    projects_df : DataFrame
        Project data.
    contributors_df : DataFrame
        Contributor data.

    Returns
    -------
    match_df : DataFrame
        Contributor to project matching data.
    """

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
            score = compute_total_score(proj_features, contrib_data)
            contrib_match.append(score)

        match_df = match_df.append(
            pd.Series(contrib_match, index=columns), ignore_index=True)

    return match_df


def filter_event_projects(event, projects_df):
    """Retrieve project data corresponding to the given event.

    Parameters
    ----------
    event : str
        Event.
    projects_df : DataFrame
        Project data.

    Returns
    -------
    projects_df : DataFrame
        Project data corresponding to the given event.
    """

    project_labels = list(projects_df[project_labels_field])

    if event == 'bhg:global':
        event = 'bhg:'

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
    """Check whether the contributor data contain all required fields.

    Parameters
    ----------
    contributors_df : DataFrame
        Contributor data.
    """

    indices = contributors_df.columns.tolist()

    missing = set(necessary_indices).difference(indices)

    if len(missing) != 0:
        raise ValueError("The script cannot continue.\n"
                         "Your contributor file is missing data:\n"
                         "Found: {}\nNecessary: {}\nMissing: {}".
                         format(indices, necessary_indices, list(missing)))


def normalize_contributors(contributors_df, contributor_fields):
    """Normalize contributor data: strip leading and trailing whitespaces in
    column headers, and rename them according to the provided contributor
    fields.

    Parameters
    ----------
    contributors_df : DataFrame
        Contributor data.
    contributor_fields : dict
        Contributor fields.

    Returns
    -------
    DataFrame
        Normalized contributor data.
    """

    # Make sure headers do not have leading or trailing spaces.
    contributors_df.rename(columns=lambda x: x.strip(), inplace=True)

    contributors_df.rename(
        columns={y: x for x, y in contributor_fields.items()}, inplace=True)
