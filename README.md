# brainmatch

[![Build Status](https://github.com/brainhackorg/brainmatch/workflows/test,%20package/badge.svg)](https://github.com/brainhackorg/brainmatch/actions?query=workflow%3A%22test%2C+package%22+branch%3Amain)

Event project requirement-contributor request matching toolkit.

## Introduction

The purpose of these scripts is to find matches between projects submitted to
a Brainhack Global event and the participants in that event. For each
participant and project, the algorithm generates a score based on the matches
between a project's requirements (e.g. topic, required skills or tools) and the
participant's skills, background and interests.

Once the result is generated, the Brainhack Global event organizers will be
able to send participants an email with information about the projects that
potentially fit them better within the context of the event.

To gather these data we recommend using the [Brainhack Global Participant Registration Form](https://github.com/brainhackorg/bhg-event-materials)
provided by the Brainhack Global Organization as a convenience participant
registration form.

## Context

The tools assume that the projects submitted as issues to the [https://github.com/brainhackorg/global2020](https://github.com/brainhackorg/global2020)
repository have been labelled correctly, meaning that they have been assigned
to a given Brainhack Global event, that they have been already published to the
website, and that they contain the appropriate labels concerning their topic
and required skills and tools.

Similarly, it assumes that your Brainhack Global event participant data is
available as a `CSV` file, and that for each participant it contains the data
that will allow matching them to a project. That is, it will contain
information about the participants' skills or background and interests.

Note that in order for the scripts to work, the relevant participant data
needs to perfectly match the available labels in the project issues in the
[https://github.com/brainhackorg/global2020](https://github.com/brainhackorg/global2020) repository.

The scoring method does not currently take into account the required level of
expertise for a project, nor is the participant's desired project type taken
into account. Similarly, the method assumes that, even if multiple `git_skills`
labels may be present for a project, the involved skills are incremental, and
hence, only the most demanding skill (according to the fixed scale/label values)
is taken into account to compute the contribution of such category to the score
for a given participant.

The scores are normalized to 1.

## Requirements

Besides Python and the Python packages specified in [`setup.cfg`](setup.cfg),
the tools assume that you have [GitHub's command line tool](https://cli.github.com/) installed.

## Instructions

In order to obtain the project-participant matches, you will need to:

1. Pull the project data locally, by calling the `tools/pull_issues.sh` script.
The script will output a `TSV` file containing all relevant data from all
existing projects in the [https://github.com/brainhackorg/global2020](https://github.com/brainhackorg/global2020)
issues.

1. Your registration form is likely to use some custom text to gather the
required participant information. These data are expected to be readable as
separate data pieces whose headings or titles can be matched to a set of
standardized fields. These standardized fields used in the scripts to ensure
that the appropriate data can be retrieved for finding the matches.

Since these headings may be variable across events, we expect you to provide a
mapping between them and the standard fields used in the scripts as a `JSON`
file. These standard fields are the following:

```
"email_address_field":,
"experience_programming_field":,
"experience_modality_field":,
"experience_tools_field":,
"experience_topic_field":,
"experience_git_skills_field":,
"desired_programming_field":,
"desired_modality_field":,
"desired_tools_field":,
"desired_topic_field":
```

Assuming that your Brainhack Global local event label is `bhg:donostia_esp_1`
(i.e. you are organizing the BHG Donostia event); the project data file pulled
was called `data/projects.tsv`; your participant registration data is contained
in `data/event_registration.csv`; the mapping of your custom fields to the
standard fields is contained in `data/fields.json`; you are naming your output
file `data/match.csv`; and that you would like to additionally restrict the
score sorting to a top-5, you will be calling the script as:

```
python compute_brainmatch_scores.py
    bhg:boston_usa_1
    data/projects.tsv
    data/participant_registration.csv
    data/fields.json
    data/match.csv
    --n 5
```

The script will write the result of the project-contributor match to the
`data/match.csv` file, and the top `n` scores in descending order will be
written to `data/match_top.csv`.

Example input files and expected output files are provided in the `data`
folder.

Note that you can also explore the projects and the matches of all available
projects by using the `bhg:global` flag when pulling the projects, and when
computing the scores for the pulled projects.

## Troobleshooting

You should make sure that:
1. You have installed and configured the necessary components described in the
[Requirements](#Requirements) section.
1. Your `fields.json` mapping file is accurate.

If the shell script that pulls the issues from the [https://github.com/brainhackorg/global2020](https://github.com/brainhackorg/global2020)
repository is unable to pull the issues, or the generated `projects.tsv` file is
empty, it may well due to the fact that [GitHub's command line tool](https://cli.github.com/)
has not been installed or has not been configured. Note that the tool **will
prompt** you to authenticate with your `GitHub` account at the command line to
grant the necessary permissions to be able to use `GitHub` CLI tool. If you are
not prompted to authenticate, the shell script that pulls the issues will not be
able to pull them, even if you are able to call and run it with no **apparent**
issues. You can check that the GitHub's command line tool installation was
successful by calling any GitHub CLI command in the terminal (e.g.
`gh issue list`) on a given **repository** that is hosted in GitHub and that you
have cloned locally, and checking that the result is the expected one. Please,
follow the instructions for your operating system, and read the output messages
when running the tools to be able to diagnose any issue.

Use the available test data and the expected matches to ensure that the tool's
necessary components have been installed and are working as expected.
