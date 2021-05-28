#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json

import numpy as np
import pandas as pd

from data import TEST_FILES

from brainmatch.brainmatch import (
    project_id_field, project_labels_field,
    compute_top_n, get_projects_features, compute_feature_score,
    compute_total_score, match, filter_event_projects,
    check_necessary_contributor_data, normalize_contributors)


def test_compute_top_n():

    data = [
        ['participant1@bhg.org', 0.714286, 0.31250, 0.6],
        ['participant2@bhg.org', 0.476190, 0.25000, 0.4],
        ['participant3@bhg.org', 0.333333, 0.28125, 0.6],
        ['participant4@bhg.org', 0.285714, 0.18750, 0.6],
        ['participant5@bhg.org', 0.047619, 0.09375, 0.4],
        ['participant6@bhg.org', 0.547619, 0.15625, 0.2]]

    columns = ['email_address_field', '1', '3', '4']
    match_df = pd.DataFrame(data=data, columns=columns)

    n = 2

    data = [
        ['participant1@bhg.org', 1, 0.714286, 4, 0.600000],
        ['participant2@bhg.org', 1, 0.476190, 4, 0.400000],
        ['participant3@bhg.org', 4, 0.600000, 1, 0.333333],
        ['participant4@bhg.org', 4, 0.600000, 1, 0.285714],
        ['participant5@bhg.org', 4, 0.400000, 3, 0.093750],
        ['participant6@bhg.org', 1, 0.547619, 4, 0.200000]]

    columns = [
        'email_address_field', 'id_top1', 'score_top1', 'id_top2',
        'score_top2']

    expected_val = pd.DataFrame(data=data, columns=columns)

    obtained_val = compute_top_n(match_df, n)

    obtained_val[['id_top1', 'id_top2']] = \
        obtained_val[['id_top1', 'id_top2']].apply(pd.to_numeric)

    pd.testing.assert_frame_equal(obtained_val, expected_val)


def test_get_projects_features():

    project_data = \
        'programming:Python, tools:DIPY, tools:ANTs, modality:DWI, ' \
        'programming:Julia, programming:R, git_skills:2_branches_PRs, ' \
        'bhg:boston_usa_1'

    expected_val = dict({
        'git_skills:': ['2_branches_PRs'], 'modality:': ['DWI'],
        'programming:': ['Python', 'Julia', 'R'], 'project_type:': [],
        'project_tools_skills:': [], 'tools:': ['DIPY', 'ANTs'],
        'topic:': []})

    obtained_val = get_projects_features(project_data)

    assert obtained_val == expected_val


def test_compute_feature_score():

    proj_feature = ['DWI']
    contrib_feature = ['DWI', 'EEG', 'fMRI', 'MRI']

    expected_val = 1.0

    obtained_val = compute_feature_score(proj_feature, contrib_feature)

    assert obtained_val == expected_val


def test_compute_total_score():

    proj_features = dict({
        'git_skills:': ['2_branches_PRs'], 'modality:': ['DWI'],
        'programming:': ['Python', 'Julia', 'R'], 'project_type:': [],
        'project_tools_skills:': [], 'tools:': ['DIPY', 'ANTs'],
        'topic:': []})

    data = [
        '10/24/20 10:08', 'participant1@bhg.org', 'John Doe', '@mygithub1',
        'He/him/his', 'BHG', 'None', 'Researcher', 'Yes', 'All of them',
        'Python, Matlab, R, Unix Command Line, Shell Scripting, '
        'Containerization',
        'DWI, EEG, fMRI, MRI',
        'SPM, FSL, Freesurfer, AFNI, ANTs, Nipype, BIDS',
        'Bayesian Approaches, Connectome, Data Visualisation, Diffusion, '
        'Hypothesis Testing, ICA, MR Methodologies, PCA, Physiology, '
        'Tractography',
        '3 Continuous Integration', 'Julia, C++', 'DWI, fMRI, MRI',
        'ANTs, Nipype, MRtrix',
        'Bayesian Approaches, Granger Causality, Information Theory, '
        'Reproducible Scientific Methods, Tractography',
        'Yes', float("nan"),
        'I have read the Code of Conduct of the Brainhack Global '
        'Organization and accept it. Link: https://bit.ly/2HRbci0']

    index = [
        'Timestamp', 'email_address_field', 'Name and surname(s)',
        'GitHub Account', 'Preferred pronouns', 'Affiliation',
        'Do you consider yourself a member of any of the following '
        'traditionally underrepresented groups in science?', 'Career level',
        'Have you ever participated in a Brainhack/Hackathon?',
        'Which editions did you participate in?',
        'experience_programming_field', 'experience_modality_field',
        'experience_tools_field', 'experience_topic_field',
        'experience_git_skills_field', 'desired_programming_field',
        'desired_modality_field', 'desired_tools_field',
        'desired_topic_field',
        'Do you give the Brainhack Donostia Organizing Committee the consent '
        'to use your anonymized data for statistical purposes?',
        "All the talks and tutorials will be held on Zoom and they may be "
        "recorded. The videos may be shared on the Brainhack Global channels. "
        "Attendees' thumbnail windows and name tags might appear in the "
        "videos.", 'Unnamed: 21']

    contrib_data = pd.Series(data=data, index=index)

    expected_val = 0.7142857142857142

    obtained_val = compute_total_score(proj_features, contrib_data)

    assert np.allclose(obtained_val, expected_val)


def test_match():

    column_names = [project_id_field, project_labels_field]
    projects_df = pd.read_csv(
        TEST_FILES["projects"], sep='\t', header=None, names=column_names,
        skiprows=1)
    event = "bhg:boston_usa_1"
    event_projects_df = filter_event_projects(event, projects_df)

    contributors_df = pd.read_csv(TEST_FILES["participant_registration"])
    with open(TEST_FILES["fields"], 'r') as f:
        contributor_fields = json.load(f)

    normalize_contributors(contributors_df, contributor_fields)

    data = [
        ['participant1@bhg.org', 0.714286, 0.31250],
        ['participant2@bhg.org', 0.476190, 0.25000],
        ['participant3@bhg.org', 0.333333, 0.28125],
        ['participant4@bhg.org', 0.285714, 0.18750],
        ['participant5@bhg.org', 0.047619, 0.09375],
        ['participant6@bhg.org', 0.547619, 0.15625]]

    columns = ['email_address_field', '1', '3']

    expected_val = pd.DataFrame(data=data, columns=columns)

    obtained_val = match(event_projects_df, contributors_df)

    pd.testing.assert_frame_equal(obtained_val, expected_val)


def test_filter_event_projects():

    column_names = [project_id_field, project_labels_field]
    projects_df = pd.read_csv(
        TEST_FILES["projects"], sep='\t', header=None, names=column_names,
        skiprows=1)
    event = "bhg:boston_usa_1"

    event_projects = filter_event_projects(event, projects_df)

    expected_val = [1, 3]

    obtained_val = event_projects["ID"].tolist()

    assert obtained_val == expected_val


def test_check_necessary_contributor_data():

    contributors_df = pd.read_csv(TEST_FILES["participant_registration"])

    with open(TEST_FILES["fields"], 'r') as f:
        contributor_fields = json.load(f)

    normalize_contributors(contributors_df, contributor_fields)

    check_necessary_contributor_data(contributors_df)


def test_normalize_contributors():

    contributors_df = pd.read_csv(TEST_FILES["participant_registration"])

    with open(TEST_FILES["fields"], 'r') as f:
        contributor_fields = json.load(f)

    normalize_contributors(contributors_df, contributor_fields)
