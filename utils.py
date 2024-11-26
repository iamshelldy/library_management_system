import csv
import logging


def count_rows(file_name: str, block_size: int = 1024 * 1024) -> int:
    """
    Counts the number of rows (lines) in a file efficiently
    using block reading. It is assumed that there is no '\n'
    character in the book fields, such as the title or author.

    :param file_name: Path to the file.
    :param block_size: Size of the block to read (in bytes). Default is 1 MB.
    :return: Number of rows in the file.
    """
    try:
        with open(file_name, "rb") as f:
            row_cnt = 0
            while True:
                b = f.read(block_size)
                if not b:
                    break
                row_cnt += b.count(b"\n")
            return row_cnt
    except FileNotFoundError:
        logging.error(f"Error: {file_name} not found.")
        raise FileNotFoundError(f"Error: {file_name} not found.")
    except Exception as e:
        logging.error(f"An error occurred while reading the file: {e}.")
        raise Exception(f"An error occurred while reading the file: {e}")


def generate_db(file_name: str, header) -> None:
    """
    Generates an empty database file with the specified header.

    Creates a new file with the provided name and writes the given
    header as the first row. Overwrites the file if it already exists.

    :param file_name: The name of the database file to create.
    :param header: An iterable of strings representing the column names.
    :return: None
    """
    with open(file_name, encoding="utf-8", mode="a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)

    logging.info(f"File {file_name} generated.")


def generate_config_file() -> None:
    """
    Generates a configuration file (config.py) with default settings.

    This function creates a new 'config.py' file and writes the default
    configuration values for the database file, table structure, book statuses,
    and logging level. It ensures that the necessary configuration is available
    for the application to run.

    The generated config file includes:
    - The path to the CSV file for storing book data.
    - The table structure, defining the fields for books (id, title, author, year, status).
    - Valid book statuses for validation when changing a book's status.
    - Logging level for controlling the verbosity of log messages.

    :return: None
    """
    logging.info(f"Generating config file 'config.py'...")
    try:
        with open("config.py", encoding="utf-8", mode="w") as f:
            f.writelines([
                "# Path of the DB file using for books storage. Must be '.csv' format.\n",
                'TABLE_FILE = "books_data.csv"\n\n',
                "# Fields of books table (CSV header, defines structure of the table).\n",
                "# For correct books filtering, columns must start with different letters.\n",
                "TABLE_FIELDS = (\n",
                '    "id",\n',
                '    "title",\n',
                '    "author",\n',
                '    "year",\n',
                '    "status",\n',
                ")\n\n",
                "# Filters available to users to search for books. Must be columns of the table.\n",
                "USERS_FILTERS = (\n",
                '    "title",\n',
                '    "author",\n',
                '    "year",\n',
                ")\n\n"
                "# Valid books statuses (uses for validation of user input when change book status).\n",
                "BOOKS_STATUSES = (\n",
                '    "в наличии",\n',
                '    "выдана",\n',
                ")\n\n",
                "# Setting the level of detail of logs. Must be DEBUG, INFO, WARNING, ERROR or CRITICAL.\n",
                'LOGGING_LEVEL = "INFO"\n',
            ])
        logging.info(f"Config file 'config.py' generated.")
    except Exception as e:
        logging.error(f"An error occurred while generating the config file: {e}")
        exit(1)
