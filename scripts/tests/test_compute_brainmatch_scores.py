#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import tempfile

import pandas as pd

from data import TEST_FILES

tmp_dir = tempfile.TemporaryDirectory()


def test_display_help(script_runner):

    ret = script_runner.run("compute_brainmatch_scores.py",
                            "--help")
    assert ret.success


def test_execution(script_runner):

    os.chdir(os.path.expanduser(tmp_dir.name))

    in_projects_fname = TEST_FILES["projects"]
    in_contributors_fname = TEST_FILES["participant_registration"]
    in_contributors_fields_fname = TEST_FILES["fields"]

    out_match_file_rootname = "brainmatch_scores"
    out_match_file_basename = out_match_file_rootname + ".csv"
    out_match_fname = os.path.join(".", out_match_file_basename)

    out_top_match_file_rootname = "brainmatch_scores_top"
    out_top_match_file_basename = out_top_match_file_rootname + ".csv"
    out_top_match_fname = os.path.join(".", out_top_match_file_basename)

    # Test with site-specific BHG event projects
    ret = script_runner.run(
        "compute_brainmatch_scores.py",
        "bhg:boston_usa_1",
        in_projects_fname,
        in_contributors_fname,
        in_contributors_fields_fname,
        out_match_fname)

    assert ret.success

    expected_val = pd.read_csv(TEST_FILES["expected_match"])
    obtained_val = pd.read_csv(out_match_fname)

    pd.testing.assert_frame_equal(obtained_val, expected_val)

    # Test with the top rank results
    ret = script_runner.run(
        "compute_brainmatch_scores.py",
        "bhg:boston_usa_1",
        in_projects_fname,
        in_contributors_fname,
        in_contributors_fields_fname,
        out_match_fname,
        "--n", "2")

    assert ret.success

    expected_val = pd.read_csv(TEST_FILES["expected_match_top"])
    obtained_val = pd.read_csv(out_top_match_fname)

    pd.testing.assert_frame_equal(obtained_val, expected_val)

    out_match_file_rootname = "brainmatch_scores"
    out_match_file_basename = out_match_file_rootname + ".csv"
    out_match_fname = os.path.join(".", out_match_file_basename)

    # Test with global BHG event projects
    ret = script_runner.run(
        "compute_brainmatch_scores.py",
        "bhg:global",
        in_projects_fname,
        in_contributors_fname,
        in_contributors_fields_fname,
        out_match_fname)

    assert ret.success

    expected_val = pd.read_csv(TEST_FILES["expected_match_global"])
    obtained_val = pd.read_csv(out_match_fname)

    pd.testing.assert_frame_equal(obtained_val, expected_val)

    # Test with the top rank results
    ret = script_runner.run(
        "compute_brainmatch_scores.py",
        "bhg:global",
        in_projects_fname,
        in_contributors_fname,
        in_contributors_fields_fname,
        out_match_fname,
        "--n", "2")

    assert ret.success

    expected_val = pd.read_csv(TEST_FILES["expected_match_global_top"])
    obtained_val = pd.read_csv(out_top_match_fname)

    pd.testing.assert_frame_equal(obtained_val, expected_val)
