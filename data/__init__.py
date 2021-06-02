"""Read test or example data."""

from os.path import join as pjoin, dirname


DATA_DIR = pjoin(dirname(__file__))

TEST_FILES = {
    "expected_match": pjoin(DATA_DIR, "expected_match.csv"),
    "expected_match_global": pjoin(DATA_DIR, "expected_match_global.csv"),
    "expected_match_global_top": pjoin(
        DATA_DIR, "expected_match_global_top.csv"),
    "expected_match_top": pjoin(DATA_DIR, "expected_match_top.csv"),
    "fields": pjoin(DATA_DIR, "fields.json"),
    "participant_registration": pjoin(
        DATA_DIR, "participant_registration.csv"),
    "projects": pjoin(DATA_DIR, "projects.tsv"),
}
