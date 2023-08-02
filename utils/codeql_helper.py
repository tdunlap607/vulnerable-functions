""""
CodeQL Helper Functions
"""
import subprocess
import os
import pandas as pd


def build_db(package_path: str, output_db_path: str):
    """Builds a CodeQL DB
    Info: https://docs.github.com/en/code-security/codeql-cli/using-the-codeql-cli/creating-codeql-databases

    Args:
        package_path (str): Location of source code
        output_db_path (str): Desired output DB name from CodeQL
    """

    if os.path.exists(output_db_path):
        print(f"CodeQL DB {output_db_path} already exists.")

    else:
        create_cmd = [
            f"codeql database create --language=go --source-root {package_path} {output_db_path} --overwrite"
        ]

        status = subprocess.run(create_cmd, shell=True, check=True)


def run_codeql(
    output_db_path: str,
    output_file_name: str,
    custom_query_path: str,
    return_results=True,
):
    """Runs a CodeQL query and decodes the bqrs output from the query. Saves results to a CSV.
    Info: https://docs.github.com/en/code-security/codeql-cli/codeql-cli-manual/query-run

    Args:
        output_db_path (str): Built DB path from CodeQL
        output_file_name (str): Desired output query result filename
        custom_query_path (str): Path to custom query
        return_results (bool, optional): Option to return CSV results in a pd.DataFrame. Defaults to True.

    Returns:
        pd.DataFrame: Results from custom query
    """

    # run the given query
    run_cmd = [
        f"codeql query run --database={output_db_path} {custom_query_path} --output={output_file_name}.bqrs"
    ]

    run_process = subprocess.run(run_cmd, shell=True, check=True)

    # decode the query output from bqrs type to csv
    decode_cmd = [
        f"codeql bqrs decode {output_file_name}.bqrs --format=csv --output={output_file_name}.csv"
    ]

    decode_process = subprocess.run(decode_cmd, shell=True, check=True)

    if return_results:
        # read results from CSV
        results = pd.read_csv(f"{output_file_name}.csv")

        return results


def custom_function_extractor_query(
    output_query_name: str, target_file: str, target_line: str
):
    """Generates a new function extractor query based on the target file/line parameters.

    Args:
        output_query_name (str): Name of new query file to generate
        target_file (str): Target file path to extract function
        target_line (str): Target line number to extract function
    """

    template = open(
        "/home/tad/Documents/GitHub/summer-research-23/code/go-vulnerable-symbol-analysis/codeql_queries/function_extractor.ql",
        "r",
        encoding="utf-8",
    ).read()

    update_template = template.replace("LINE_NUMBER", str(target_line))
    update_template = update_template.replace("FILE_NAME", target_file)

    # write new updated query
    update_query = open(
        f"/home/tad/Documents/GitHub/summer-research-23/code/go-vulnerable-symbol-analysis/codeql_queries/custom_queries/{output_query_name}.ql",
        "w",
        encoding="utf-8",
    )
    update_query.write(update_template)
    update_query.close()

    print(
        f"New query written to: ./code/go-vulnerable-symbol-analysis/codeql_queries/custom_queries/{output_query_name}.ql"
    )


def custom_extract_functions_in_file_query(output_query_name: str, target_file: str):
    """Generates a new function extractor query based on the target file/line parameters.

    Args:
        output_query_name (str): Name of new query file to generate
        target_file (str): Target file path to extract function
    """

    template = open(
        "/home/tad/Documents/GitHub/summer-research-23/code/go-vulnerable-symbol-analysis/codeql_queries/extract_functions_in_file.ql",
        "r",
        encoding="utf-8",
    ).read()

    update_template = template.replace("FILE_NAME", str(target_file))

    # write new updated query
    update_query = open(
        f"/home/tad/Documents/GitHub/summer-research-23/code/go-vulnerable-symbol-analysis/codeql_queries/custom_queries/{output_query_name}.ql",
        "w",
        encoding="utf-8",
    )
    update_query.write(update_template)
    update_query.close()

    print(
        f"New query written to: ./code/go-vulnerable-symbol-analysis/codeql_queries/custom_queries/{output_query_name}.ql"
    )
