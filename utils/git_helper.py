"""
Helper git functions
"""
import os
import git
import patchparser
import subprocess
import pandas as pd
from packaging.version import Version, parse
import datetime


def clone_repo(repo_owner: str, repo_name: str, clone_path: str, local_name=False):
    """Clones a GitHub repository to a desired location

    Args:
        repo_owner (str): GitHub Repo Owner
        repo_name (str): GitHub Repo Project Name
        clone_path (str): Desired location to clone repository
        local_name (bool): Use a differnt local folder name
    """
    # set path
    if not local_name:
        clone_path = f"{clone_path}{repo_owner}/"
    else:
        clone_path = f"{clone_path}"

    if not os.path.exists(clone_path):
        os.makedirs(clone_path)

    if not local_name:
        # check if clone already exists
        if os.path.exists(f"{clone_path}{repo_name}"):
            print(f"Path already exists: {clone_path}{repo_name}")
        else:
            print(f"Cloning repo to: {clone_path}{repo_name}")
            try:
                git.Git(clone_path).clone(
                    f"https://github.com/{repo_owner}/"
                    f"{repo_name.replace('.git', '')}.git"
                )

                return True
            except Exception as e:
                print(e)
                return False

    else:  # specific local folder name
        # check if clone already exists
        if os.path.exists(f"{clone_path}{local_name}"):
            print(f"Path already exists: {clone_path}{local_name}")
        else:
            # clone repo
            print(f"Cloning repo to: {clone_path}{local_name}")
            git.Git(clone_path).clone(
                f"https://github.com/{repo_owner}/"
                f"{repo_name.replace('.git', '')}.git"
            )


def git_checkout_commit(clone_path: str, commit_sha: str):
    """Checkout a target commit

    Args:
        clone_path (str): Location of source code
        commit_sha (str): Target commit to checkout
    """

    # set the git repo
    repo = git.Repo(path=clone_path)

    # checkout the target commit_sha
    repo.git.checkout(commit_sha, force=True)


def git_diff(clone_path: str, commit_sha: str, df=False) -> dict:
    """Obtains the git diff information using patchparser
    Info: https://github.com/tdunlap607/patchparser

    Args:
        clone_path (str): Location of source code
        commit_sha (_type_): Target commit to parse
        df (bool): If you want a pandas DF back

    Returns:
        (dict): Dictionary of git diff info
    """

    repo_owner = clone_path.split("/")[-3]
    repo_name = clone_path.split("/")[-2]

    diff = patchparser.github_parser_local.commit_local(
        repo_owner=repo_owner,
        repo_name=repo_name,
        sha=commit_sha,
        base_repo_path=clone_path,
    )

    if df:
        diff_df = pd.DataFrame(diff)

        # calculate the line numbers modified in relational to the original file
        diff_df["original_modified_lines"] = diff_df.apply(
                lambda x: git_changed_original_lines(
                        raw_patch=x["raw_patch"],
                        original_line_start=x["original_line_start"],
                )
                if x["deletions"] > 0
                else None,
                axis=1,
        )

        # calculate the line numbers modified in relation to the fresh commit file
        diff_df["new_modified_lines"] = diff_df.apply(
                lambda x: git_changed_modified_lines(
                        raw_patch=x["raw_patch"],
                        modified_line_start=x["modified_line_start"],
                )
                if x["additions"] > 0
                else None,
                axis=1,
        )

        return diff_df
    else:
        return diff


def git_changed_original_lines(raw_patch: str, original_line_start: int) -> list:
    """Calculates the line numbers that were changed of the original file during the commit

    Args:
        raw_patch (str): Diff hunk from git_diff
        original_line_start (int): Line number start of diff hunk

    Returns:
        list: List of modified line numbers from the original file
    """
    # split the diff hunk based on newlines
    original = raw_patch.splitlines()

    try:
    # original lines can only be removed, we handled additions in git_changed_modified_lines
        original_lines = [x for x in original if x[0] != "+"][1:]

        # get the line numbers that were removed
        original_line_numbers = [
            idx + original_line_start for idx, i in enumerate(original_lines) if i[0] == "-"
        ]
    except:
        original_lines = [x for x in original[1:] if x[0] != "+"]

        # get the line numbers that were removed
        original_line_numbers = [
            idx + original_line_start for idx, i in enumerate(original_lines) if i[0] == "-"
        ]

    return original_line_numbers


def git_changed_modified_lines(raw_patch: str, modified_line_start: int) -> list:
    """Calculates the line numbers that were changed of the modified file during the commit

    Args:
        raw_patch (str): Diff hunk from git_diff
        modified_line_start (int): Line number start of diff hunk

    Returns:
        list: List of modified line numbers
    """
    # split the diff hunk based on newlines
    modified = raw_patch.splitlines()

    # modified lines can only be added, we handled removals in git_changed_original_lines
    try:
        modified_lines = [x for x in modified[1:] if x[0] != "-"]
    except:
        print("wait")

    # get the line numbers that were added
    modified_line_numbers = [
        idx + modified_line_start for idx, i in enumerate(modified_lines) if i[0] == "+"
    ]

    return modified_line_numbers


def semver_sort(temp_versions):
    """Sorts semver tags based on pythons packaging.version

    Args:
        temp_versions (list): List of tags

    Returns:
        pd.DataFrame: Sorted tags based on semver
    """
    if temp_versions is not None:
        if len(temp_versions) > 0:
            clean_parse = []
            for each in temp_versions:
                try:
                    temp_version = Version(each)
                    temp_version.raw_version = each
                    temp_version.error = False
                    clean_parse.append(temp_version)
                except Exception as err:
                    print(err)
                    # TODO: this needs to be handled better
                    clean_each = ".".join(each.split(".")[:3])
                    temp_version = Version(clean_each)
                    temp_version.raw_version = each
                    temp_version.error = True
                    clean_parse.append(temp_version)

            # sort the clean versions
            clean_parse.sort()

            clean_return = []

            for clean in clean_parse:
                clean_return.append(clean.raw_version)

            # create a df to sort the versions
            clean_return_df = pd.DataFrame(clean_return, columns=["tag"])
            clean_return_df["tag_order"] = clean_return_df.index

            return clean_return_df
    else:
        return []


def get_tags(repo_owner, repo_name, clone_path):
    """Obtains the local git repo tags for a given repository in a certain path

    Args:
        repo_owner (str): Repo owner
        repo_name (str): Name of repo
        clone_path (str): Local clone path of repo

    Returns:
        pd.DataFrame: A sorted pandas df of tags
    """

    # create repo path
    repo_path = f"{clone_path}"

    # execute the git tags command
    git_tags_command = (
        f"(cd {repo_path} && "
        f"git for-each-ref --sort=v:refname --format '%(refname) %(creatordate)' refs/tags)"
    )

    # this is all trusted input....not a vulnerability
    git_tags = subprocess.check_output(
        git_tags_command, shell=True, encoding="UTF-8"
    ).splitlines()

    # load in the tag outputs
    if len(git_tags) > 0:
        temp_df = pd.DataFrame(git_tags, columns=["raw_out"])
        temp_df["repo_owner"] = repo_owner
        temp_df["repo_name"] = repo_name
        temp_df["tag_count"] = len(temp_df)

        # extract the creatordate
        temp_df["creatordate"] = temp_df.apply(
            lambda x: datetime.datetime.strptime(
                " ".join(x["raw_out"].strip("\n").split(" ")[1:-1]),
                "%a %b %d %H:%M:%S %Y",
            ),
            axis=1,
        )
        # extract the tag from the list
        temp_df["tag"] = temp_df.apply(
            lambda x: x["raw_out"].strip("\n").split(" ")[0].replace("refs/tags/", ""),
            axis=1,
        )

        # get the correct semver tag order
        # temp_tags = temp_df["tag"].values.tolist()

        # sort the tags
        # sorted_tags = semver_sort(temp_tags)

        # add the sorted tags back to the original df
        # temp_df_sorted = pd.merge(temp_df, sorted_tags, on="tag", how="left")

    else:
        temp_df_sorted = pd.DataFrame(
            [["NO_TAGS", repo_owner, repo_name]],
            columns=["raw_out", "repo_owner", "repo_name"],
        )
        temp_df_sorted["tag_count"] = None
        temp_df_sorted["creatordate"] = None
        temp_df_sorted["tag"] = None
        temp_df_sorted["tag_order"] = None

    return temp_df


def match_functions(
    temp_functions: pd.DataFrame, temp_file_name: str, temp_lines: list
):
    """Matches changed line numbers to functions

    Args:
        temp_functions (_type_): _description_
        temp_file_name (_type_): _description_
        temp_lines (_type_): _description_
    """

    # match the file
    temp_file_match = temp_functions[
        temp_functions["funcFile"].str.contains(temp_file_name)
    ]

    temp_matches = pd.DataFrame()

    # make sure temp_lines is of type list
    # TODO: solve the issue where the modified file only includes deletions
    # Example: https://github.com/theupdateframework/go-tuf/commit/ed6788e710fc3093a7ecc2d078bf734c0f200d8d
    
    # cline/errors.go produces a int(0) for the new_modified_lines
    if isinstance(temp_lines, list):
        for line in temp_lines:
            # match the line number between the StartLine and EndLine of functions
            temp_line_match = temp_file_match[
                (temp_file_match["funcStartLine"] <= line)
                & (temp_file_match["funcEndLine"] >= line)
            ].copy()

            # add the file_name/line number match back to the df
            temp_line_match["file_name"] = temp_file_name
            temp_line_match["line"] = line

            # append to to complete df
            temp_matches = pd.concat([temp_matches, temp_line_match])

    return temp_matches