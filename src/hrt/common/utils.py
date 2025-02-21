"""Utility functions for the HRT project."""

import csv
import os
import tempfile
import time
import zipfile

import click
import requests

from hrt.common import constants
from hrt.common.config_reader import logger


def read_delim_file(
    file_path,
    delimiter=",",
    encoding: str = "iso-8859-1",
    skip_header=False,
    header=None,
    fields_count=None,
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
                if skip_header and row[0].startswith(header):
                    continue
                if fields_count:
                    row = row[:fields_count]
                data.append(row)
    except FileNotFoundError:
        logger.error("Error: The file at %s was not found.", file_path)
    except Exception as e:
        logger.error("An error occurred reading the file at %s: %s", file_path, e)
    return data


def save_output(filename, output, folder=None):
    """Saves the output to a file with the given filename in the given folder.

    :param filename: Name of the file to save the output.
    :param output: Output to be saved in the file.
    :param folder: Folder where the file will be saved (default is None).
    """
    filename = os.path.join(folder, filename) if folder else filename
    with open(filename, "w", encoding="utf-8", newline="") as file:
        file.write(output)


def get_header(header):
    """Returns the header with a separator line.

    :param header: Header to be returned.
    :return: Header with a separator line.
    """
    return f'{header}\n{"-" * len(header)}'


def create_folder(folder):
    """Creates a folder if it does not exist.

    :param folder: Path to the folder to be created.
    """
    is_folder_exists = os.path.exists(folder)
    if not is_folder_exists:
        os.makedirs(folder)


def write_output(output, filename=None, folder=None):
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


def permutations(word):
    """Returns all possible permutations of a word.

    :param word: Word to generate permutations.
    :return: List of permutations of the word.
    """
    if len(word) == 1:
        return [word]
    perms = []
    for i, letter in enumerate(word):
        for perm in permutations(word[:i] + word[i + 1 :]):
            perms.append(letter + perm)
    return perms


def get_word_combinations(word):
    """Returns all possible combinations of a word.

    :param word: Word to generate combinations.
    :return: List of combinations of the word.
    """
    return ["".join(p) for p in permutations(word)]


def select_from_options(options, prompt):
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


def select_option_from_list(options, prompt) -> str | None:
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


def get_user_input_index(choices, prompt: str):
    """Selects a choice index from the given list of choices.

    :param prompt:
    :param choices: List of choices to select from.
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


def read_words_from_file(file_path):
    """Read words from a file."""
    with open(file_path, encoding="utf-8") as file:
        return [line.strip() for line in file.readlines()]


def load_callsigns_from_file(file_path):
    """Loads unique callsigns from a file."""
    try:
        with open(file_path, encoding="utf-8") as file:
            callsigns = {line.strip() for line in file}
        return list(callsigns)
    except FileNotFoundError:
        return []


def download_file(url, output_file_path, zip_files: list[str] = None):
    """Download a file from the given URL to the output file path."""
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


def download_zip_file(url, output_file_path, zip_files: list[str] = None):
    """Download a ZIP file from the given URL to the output file path."""
    if not url.endswith(".zip"):
        raise ValueError(f"Invalid URL {url}. Expected a ZIP file URL.")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as temp_file:
        temp_file.write(requests.get(url, timeout=constants.REQUEST_TIMEOUT).content)
    temp_file_path = temp_file.name
    logger.info("Downloaded %s to %s", url, temp_file_path)

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


def get_user_agent(app_config: dict) -> str:
    """Returns a random user agent from the list of user agents."""
    if app_config is None:
        app_config = {}
    app_name = app_config.get("name", constants.APP_NAME)
    app_ver = app_config.get("version", constants.APP_VERSION)
    app_desc = app_config.get("description", "")
    return f"{app_name}/{app_ver} ({constants.GITHUB_URL}; {app_desc})"
