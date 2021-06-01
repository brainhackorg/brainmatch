#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import json
import os

import pandas as pd

from brainmatch.brainmatch import (
    top_match_label, underscore, project_id_field, project_labels_field,
    check_necessary_contributor_data, compute_top_n, filter_event_projects,
    match, normalize_contributors)


extension_sep = "."


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

    column_names = [project_id_field, project_labels_field]
    projects_df = pd.read_csv(
        args.in_projects_fname, sep='\t', header=None, names=column_names,
        skiprows=1)
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
    dec_places = 2
    match_df.round(dec_places).to_csv(args.out_match_fname, index=False)

    # Compute the top n
    top_match_df = compute_top_n(match_df, args.n)

    path = os.path.dirname(args.out_match_fname)
    match_basename = os.path.basename(args.out_match_fname)
    rootname, ext = match_basename.split(extension_sep)
    top_basename = \
        rootname + underscore + top_match_label + extension_sep + ext
    top_fname = os.path.join(path, top_basename)

    # Save data to a csv file
    top_match_df.round(dec_places).to_csv(top_fname, index=False)


if __name__ == "__main__":
    main()
