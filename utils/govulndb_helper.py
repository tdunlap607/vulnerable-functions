"""
Helper functions for GoVulnDB
"""
import yaml
import os
import pandas as pd


def load_report(local_db: str, report_id: str) -> dict:
    """Parses a GoVulnDB Report

    Args:
        local_db (str): Local clone of https://github.com/golang/vulndb
        report_id (str): GoVulnDB Report ID

    Returns:
        dict: Dict of yaml
    """
    # check if .yaml is appended, if not, add it
    if ".yaml" in report_id:
        pass
    else:
        report_id = f"{report_id}.yaml"

    with open(f"{local_db}{report_id}", "r") as f:
        temp_yaml = yaml.safe_load(f)

    return temp_yaml


def load_all_reports(govulndb_path: str, verbose=True) -> pd.DataFrame:
    """Parses and loads all reports in the GoVulnDB

    Args:
        govulndb_path (str): Path to the locally cloned GoVulnDB
        verbose (bool): Prints status of loading reports

    Returns:
        pd.DataFrame: Complete parsed GoVulnDB reports
    """
    # get reports
    report_ids = os.listdir(govulndb_path)

    # parse the reports
    parsed_reports = pd.DataFrame()

    # get the repos for each report
    for index, temp_id in enumerate(report_ids):
        if verbose:
            print(f"Loaded {index+1}/{len(report_ids)}")
        # parse the reports
        temp_report = parse_report(local_db=govulndb_path, report_id=temp_id)
        temp_df = pd.DataFrame.from_dict([temp_report])

        # combine the reports to a single DF
        parsed_reports = pd.concat([parsed_reports, temp_df])

    parsed_reports["known_vfc"] = parsed_reports.apply(
        lambda x: True if x["vfc_sha"] != [] else False, axis=1
    )

    return parsed_reports


def parse_report(local_db: str, report_id: str) -> dict:
    """Parses useful keys from the GoVulnDB report

    Args:
        local_db (str): Location of locally cloned GoVulnDB
        report_id (str): GoVulnDB Report ID

    Returns:
        dict: Parsed keys
    """
    # load the report
    report = load_report(local_db, report_id)

    # parse important aspect of the report
    report_id = report["id"]
    report_git_repo = report["modules"][0]["module"]

    # git repo owner/name
    try:
        git_repo_owner = report_git_repo.split("github.com/")[-1].split("/")[0]
        git_repo_name = report_git_repo.split("github.com/")[-1].split("/")[1]
    except Exception:
        git_repo_owner = None
        git_repo_name = None

    # extract the references
    report_fixes_total = report["references"]
    report_fixes = [x["fix"] for x in report_fixes_total if "fix" in x.keys()]

    # VFCs. These are GitHub commits
    report_vfc = [x for x in report_fixes if "commit/" in x]
    report_vfc_sha = [x.split("commit/")[-1].strip("/") for x in report_vfc]

    # handle the standard library instances for VFCs
    report_vfc_std_lib = [
        x for x in report_fixes if "https://go.googlesource.com/go/+/" in x
    ]
    report_vfc_std_lib_sha = [
        x.split("go/+/")[-1].strip("/") for x in report_vfc_std_lib
    ]

    # extract vulnerable symbols
    try:
        report_symbols = report["modules"][0]["packages"][0]["symbols"]
    except Exception:
        report_symbols = None
    try:
        report_derived_symbols = report["modules"][0]["packages"][0]["derived_symbols"]
    except Exception:
        report_derived_symbols = None

    # extract fixed/vulnerable at version
    try:
        fixed = report["modules"][0]["versions"][0]["fixed"]
    except Exception:
        fixed = None

    try:
        vulnerable_version = report["modules"][0]["vulnerable_at"]
    except Exception:
        vulnerable_version = None

    # create a simple dictionary to return
    report_parsed = {
        "id": report_id,
        "git_repo": report_git_repo,
        "repo_owner": git_repo_owner,
        "repo_name": git_repo_name,
        "fix_links": report_fixes,
        "vfc": report_vfc + report_vfc_std_lib,
        "vfc_sha": report_vfc_sha + report_vfc_std_lib_sha,
        "symbols": report_symbols,
        "derived_symbols": report_derived_symbols,
        "fixed_version": fixed,
        "vulnerable_version": vulnerable_version,
    }

    return report_parsed
