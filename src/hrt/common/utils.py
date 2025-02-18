import csv
import os
import tempfile
import time
import zipfile

import click
import requests

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
        logger.error(f"Error: The file at {file_path} was not found.")
    except Exception as e:
        logger.error(f"An error occurred reading the file at {file_path}: {e}")
    return data


def save_output(filename, output, folder=None):
    """Saves the output to a file with the given filename in the given folder.

    :param filename: Name of the file to save the output.
    :param output: Output to be saved in the file.
    :param folder: Folder where the file will be saved (default is None).
    """
    filename = os.path.join(folder, filename) if folder else filename
    with open(filename, "w") as file:
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
    with open(file_path, "w") as file:
        for line in output:
            file.write(f"{line}\n")


def select_from_options(options, prompt):
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


def read_words_from_file(file_path):
    """Read words from a file."""
    with open(file_path) as file:
        return [line.strip() for line in file.readlines()]


def load_callsigns_from_file(file_path):
    """Loads unique callsigns from a file."""
    try:
        with open(file_path) as file:
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
            output_file.write(requests.get(url).content)
        logger.info(f"File saved to {output_file_path}")


def download_zip_file(url, output_file_path, zip_files: list[str] = None):
    """Download a ZIP file from the given URL to the output file path."""
    if not url.endswith(".zip"):
        raise ValueError(f"Invalid URL {url}. Expected a ZIP file URL.")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as temp_file:
        temp_file.write(requests.get(url).content)
    temp_file_path = temp_file.name
    logger.info(f"Downloaded {url} to {temp_file_path}")

    with zipfile.ZipFile(temp_file_path, "r") as zip_ref:  # noqa: SIM117
        with open(output_file_path, "wb") as output_file:
            for file_info in zip_ref.infolist():
                if zip_files and file_info.filename not in zip_files:
                    continue
                output_file.write(zip_ref.open(file_info).read())
    logger.info(f"Extracted {url} to {output_file_path}")


def get_current_time() -> float:
    """Returns the current time in seconds since the epoch."""
    return time.time()
