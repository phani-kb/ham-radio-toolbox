"""Utility functions for the HRT project."""

import csv
import os
import tempfile
import time
import zipfile
from typing import Any, Dict, List, Optional, Set, TypeVar, Union

import click
import requests

from hrt.common import constants
from hrt.common.config_reader import logger
from hrt.common.enums import SortBy
from hrt.common.hrt_types import QuestionNumber
from hrt.common.question_metric import QuestionMetric

T = TypeVar("T")


def read_delim_file(
    file_path: str,
    delimiter: str = ",",
    encoding: str = "iso-8859-1",
    skip_header: bool = False,
    header: Optional[str] = None,
    fields_count: Optional[int] = None,
) -> list[list[str]]:
    """Reads a delimited file and returns its contents as a list of dictionaries.
    :param encoding:
    :param file_path: Path to the file to be read.
    :param delimiter: Delimiter used in the file (default is comma).
    :param skip_header: Flag to skip the header (default is False).
    :param header: Header to be skipped (default is None).
    :param fields_count: Number of fields to be read from each row (default is None).
    :return: List of dictionaries representing the file contents.
    """
    data = []
    try:
        with open(file_path, encoding=encoding) as file:
            reader = csv.reader(file, delimiter=delimiter)
            for row in reader:
                if skip_header and header and row[0].startswith(header):
                    continue
                if fields_count:
                    row = row[:fields_count]
                data.append(row)
    except FileNotFoundError:
        logger.error("Error: The file at %s was not found.", file_path)
    except Exception as e:
        logger.error("An error occurred reading the file at %s: %s", file_path, e)
    return data


def save_output(filename: str, output: str, folder: Optional[str] = None) -> None:
    """Saves the output to a file with the given filename in the given folder.
    :param filename: Name of the file to save the output.
    :param output: Output to be saved in the file.
    :param folder: Folder where the file will be saved (default is None).
    """
    file_parent_folder = os.path.dirname(filename)
    file_folder = os.path.join(folder, file_parent_folder) if folder else file_parent_folder
    if file_folder and not os.path.exists(file_folder):
        create_folder(file_folder)
    filename = os.path.join(folder, filename) if folder else filename
    with open(filename, "w", encoding="utf-8", newline="") as file:
        file.write(output)


def get_header(header: str) -> str:
    """Returns the header with a separator line.
    :param header: Header to be returned.
    :return: Header with a separator line.
    """
    return f"{header}\n{'-' * len(header)}"


def create_folder(folder: str) -> None:
    """Creates a folder if it does not exist.
    :param folder: Path to the folder to be created.
    """
    is_folder_exists = os.path.exists(folder)
    if not is_folder_exists:
        os.makedirs(folder)


def read_filename(default_filename: str) -> str:
    """Reads a filename from the user input or returns the default filename.
    :param default_filename: Default filename to be returned if the user input is empty.
    :return: Filename provided by the user or the default filename.
    """
    filename = input(f"Enter a filename to save output (default: {default_filename}): ")
    return filename if filename else default_filename


def read_number_from_input(prompt: str, min_value: int, max_value: int) -> int:
    """Reads a number from the user input within a specified range.
    :param prompt: Prompt to be displayed to the user.
    :param min_value: Minimum value for the number.
    :param max_value: Maximum value for the number.
    :return: Number provided by the user within the specified range.
    """
    valid_input = False
    while not valid_input:
        num = click.prompt(prompt)
        try:
            num = int(num)
            if min_value <= num <= max_value:
                valid_input = True
                return num
            print(f"Invalid input. Please enter a number between {min_value} and {max_value}.")
        except ValueError:
            print("Invalid input. Please enter a valid number.")
    return -1


def write_output(
    output: List[str],
    filename: Optional[str] = None,
    folder: Optional[str] = None,
) -> None:
    """Writes the output to a file with the given filename in the given folder, line by line.
    :param output: List of lines to be written to the file.
    :param filename: Name of the file to write the output.
    :param folder: Folder where the file will be written (default is None).
    """
    if not filename:
        for line in output:
            print(line)
        return
    if folder:
        create_folder(folder)
    file_path = os.path.join(folder, filename) if folder else filename
    with open(file_path, "w", encoding="utf-8", newline="") as file:
        for line in output:
            file.write(f"{line}\n")


def permutations(word: str) -> List[str]:
    """Returns all possible permutations of a word.
    :param word: Word to generate permutations.
    :return: List word permutations.
    """
    if len(word) == 1:
        return [word]
    perms = []
    for i, letter in enumerate(word):
        for perm in permutations(word[:i] + word[i + 1 :]):
            perms.append(letter + perm)
    return perms


def get_word_combinations(word: str) -> List[str]:
    """Returns all possible combinations of a word.
    :param word: Word to generate combinations.
    :return: List of word combinations.
    """
    return ["".join(p) for p in permutations(word)]


def select_from_options(options: Dict[str, str], prompt: str) -> Optional[str]:
    """Selects an option from a dictionary of options.
    :param options: Dictionary of options to select from.
    :param prompt: Prompt to display to the user.
    :return: The key of the selected option.
    """
    if not options:
        logger.error("No options provided.")
        return None
    if len(options) == 1:
        return list(options.keys())[0]
    print(f"{prompt}:")
    for idx, option in enumerate(options, start=1):
        print(f"{idx}. {option} ({options[option]})")
    while True:
        try:
            choice = int(click.prompt(f"Please select {prompt.lower()} by number", type=int))
            if 1 <= choice <= len(options):
                return list(options.keys())[choice - 1]
            print(f"Invalid choice. Please select a number between 1 and {len(options)}.")
        except ValueError:
            print("Invalid input. Please enter a number.")


def select_option_from_list(options: List[str], prompt: str) -> Optional[str]:
    """Selects an option from a list of options.
    :param options: List of options to select from.
    :param prompt: Prompt to display to the user.
    :return: The selected option.
    """
    if not options:
        logger.error("No options provided.")
        return None
    if len(options) == 1:
        return options[0]
    print(f"{prompt}:")
    for idx, option in enumerate(options, start=1):
        print(f"{idx}. {option}")
    while True:
        try:
            choice = int(click.prompt(f"Please select {prompt.lower()} by number", type=int))
            if 1 <= choice <= len(options):
                return options[choice - 1]
            print(f"Invalid choice. Please select a number between 1 and {len(options)}.")
        except ValueError:
            print("Invalid input. Please enter a number.")


def get_user_input_index(choices: List[Any], prompt: str) -> int:
    """Selects a choice index from the given list of choices.
    :param choices: List of choices to select from.
    :param prompt: Prompt to display to the user.
    :return: Index of the selected choice.
    """
    while True:
        try:
            choice = int(input(prompt))
            if 1 <= choice <= len(choices):
                return choice - 1
            print(f"Invalid choice. Please select a number between 1 and {len(choices)}.")
        except ValueError:
            print("Invalid input. Please enter a number.")


def get_user_input_option(choices: List[str], prompt: str) -> str:
    """Selects a choice from the given list of choices.
    :param choices: List of choices to select from.
    :param prompt: Prompt to display to the user.
    :return: The selected choice.
    """
    choices_lower = [choice.lower() for choice in choices]
    while True:
        choice = input(prompt).lower()
        if choice in choices_lower:
            return choices[choices_lower.index(choice)]
        print("Invalid choice. Please select a valid option.")


def sort_callsigns(
    callsigns: List[str], sort_by: Optional[str], reverse: bool = False
) -> List[str]:
    """Sort callsigns by specific criteria.
    :param reverse:
    :param callsigns: List of callsigns to sort.
    :param sort_by: Criteria to sort by.
    :return: Sorted list of callsigns.
    """
    if not sort_by:
        return callsigns
    if sort_by == SortBy.CALLSIGN.id:
        callsigns = sorted(callsigns, reverse=reverse)
    return callsigns


def read_words_from_file(file_path: str) -> List[str]:
    """Read words from a file.
    :param file_path: Path to the file.
    :return: List of words read from the file.
    """
    with open(file_path, encoding="utf-8") as file:
        return [line.strip() for line in file.readlines()]


def load_callsigns_from_file(file_path: str) -> Set[str]:
    """Loads unique callsigns from a file.
    :param file_path: Path to the file.
    :return: List of unique callsigns.
    """
    try:
        with open(file_path, encoding="utf-8") as file:
            return {line.strip() for line in file}
    except FileNotFoundError:
        return set()


def download_file(url: str, output_file_path: str, zip_files: Optional[List[str]] = None) -> None:
    """Download a file from the given URL to the output file path.
    :param url: URL of the file to download.
    :param output_file_path: Path where to save the file.
    :param zip_files: List of files to extract from the ZIP file.
    """
    if url.endswith(".zip"):
        download_zip_file(
            url,
            output_file_path,
            zip_files,
        )
    else:
        with open(output_file_path, "wb") as output_file:
            output_file.write(requests.get(url, timeout=constants.REQUEST_TIMEOUT).content)
        logger.info("File saved to %s", output_file_path)


def download_zip_file(
    url: str,
    output_file_path: str,
    zip_files: Optional[List[str]] = None,
) -> None:
    """Download a ZIP file from the given URL to the output file path.
    :param url: URL of the ZIP file to download.
    :param output_file_path: Path where to save the extracted contents.
    :param zip_files: List of files to extract from the ZIP file.
    """
    if not url.endswith(".zip"):
        raise ValueError(f"Invalid URL {url}. Expected a ZIP file URL.")
    with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as temp_file:
        temp_file.write(requests.get(url, timeout=constants.REQUEST_TIMEOUT).content)
    temp_file_path = temp_file.name
    logger.info("Downloaded %s to %s", url, temp_file_path)

    output_folder = os.path.dirname(output_file_path)
    if output_folder and not os.path.exists(output_folder):
        create_folder(output_folder)

    with zipfile.ZipFile(temp_file_path, "r") as zip_ref:  # noqa: SIM117
        with open(output_file_path, "wb") as output_file:
            for file_info in zip_ref.infolist():
                if zip_files and file_info.filename not in zip_files:
                    continue
                output_file.write(zip_ref.open(file_info).read())
    logger.info("Extracted %s to %s", url, output_file_path)


def get_current_time() -> float:
    """Returns the current time in seconds since the epoch."""
    return time.time()


def load_question_metrics(metrics_file_path: Union[str, os.PathLike]) -> List[QuestionMetric]:
    """Loads metrics from a file.
    :param metrics_file_path: Path to the metrics file.
    :return: List of question metrics.
    """
    metrics: List[QuestionMetric] = []
    if not os.path.exists(metrics_file_path):
        return metrics
    with open(metrics_file_path, "r", encoding="utf-8") as file:
        for line in file:
            parts = line.strip().split(constants.DEFAULT_METRICS_DELIMITER)
            if len(parts) == 4:
                metric = QuestionMetric(
                    QuestionNumber(parts[0]), int(parts[1]), int(parts[2]), int(parts[3])
                )
                metrics.append(metric)
            else:
                logger.warning("Invalid metrics line: %s", line)
    return metrics


def read_metrics_from_file(metrics_file: str) -> List[QuestionMetric]:
    """Reads metrics from a file.
    :param metrics_file: Path to the metrics file.
    :return: List of question metrics.
    """
    metrics: List[QuestionMetric] = []
    if not os.path.exists(metrics_file):
        return metrics
    with open(metrics_file, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split(constants.DEFAULT_METRICS_DELIMITER)
            if len(parts) == 4:
                question_number = parts[0]
                correct_attempts = int(parts[1])
                wrong_attempts = int(parts[2])
                skip_count = int(parts[3])
                metric = QuestionMetric(
                    QuestionNumber(question_number), correct_attempts, wrong_attempts, skip_count
                )
                metrics.append(metric)
    return metrics


def get_user_agent(app_config: Optional[Dict[str, Any]]) -> str:
    """Returns a user agent string with app information.
    :param app_config: Application configuration dictionary.
    :return: User agent string.
    """
    if app_config is None:
        app_config = {}
    app_name = app_config.get("name", constants.APP_NAME)
    app_ver = app_config.get("version", constants.APP_VERSION)
    app_desc = app_config.get("description", constants.APP_DESCRIPTION)
    logger.debug("App Name: %s, App Version: %s, App Description: %s", app_name, app_ver, app_desc)
    user_agent = f"{app_name}/{app_ver} ({app_desc})"
    logger.info("User Agent: %s", user_agent)
    return user_agent


def get_pairs_from_callsign(callsign):
    """Get adjacent letter pairs from a callsign."""
    pairs = set()
    for i in range(len(callsign) - 1):
        pair = callsign[i : i + 2]
        if len(pair) == 2:
            pairs.add(pair)
    return pairs
