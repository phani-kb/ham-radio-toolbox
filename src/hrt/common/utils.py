import csv
import os
import time

from hrt.config_reader import logger


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


def read_words_from_file(file_path):
    """Read words from a file."""
    with open(file_path) as file:
        words = [line.strip() for line in file.readlines()]
    return words


def get_current_time() -> float:
    """Returns the current time in seconds since the epoch."""
    return time.time()
