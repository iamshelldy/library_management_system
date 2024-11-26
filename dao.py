import csv
import logging
from tempfile import NamedTemporaryFile
from shutil import move, copy
from os.path import exists

from config import TABLE_FIELDS, BOOKS_STATUSES, USERS_FILTERS
from utils import count_rows, generate_db


class LibraryManagementSystem:
    """
    DAO class providing CRUD functionality to manage a library of books.

    This class allows you to add, delete, search, display books,
    and update their status. It works with text files to store
    book data.
    """
    def __init__(self, filename: str) -> None:
        """
        Initializes the LibraryManagementSystem instance.

        This constructor sets up the database file and its backup file.
        It checks if the specified library file exists:
        - If the file does not exist, it generates a new database file.
        - If the file exists, it checks for any necessary migrations to
          update the database structure.

        :param filename: The name of the file to store the library data.
        :return: None.
        """
        self.db_file = filename
        self.backup_file = self.db_file.split(".")[0] + ".bak"

        if not exists(filename):  # Checking for library file existing.
            logging.debug(f"File {self.db_file} does not exist. Create a new one.")
            generate_db(self.db_file, TABLE_FIELDS)
        else:  # If file exists, check for changing DB structure.
            self.check_for_migration()

    def check_for_migration(self) -> None:
        """
        Checks if the database structure has changed and performs
        migration if necessary.

        This method compares the current header of the library database
        file with the expected structure. If the database structure has
        changed, it triggers a migration process to update the file.

        If the structure is already up-to-date, no action is taken.

        :return: None
        :raises Exception: If any error occurs during the file operation.
        """
        logging.debug("Checking for migrations.")

        try:
            with open(self.db_file, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                header = next(reader)

                if header == list(TABLE_FIELDS):
                    logging.debug("No migration required.")
                    return

            self.migrate(header)
        except Exception as e:
            logging.error(f"Failed to check for migration: {e}.")

    def create_backup(self) -> None:
        """
        Creates a backup of the library database.

        :return: None
        """
        try:
            copy(self.db_file, self.backup_file)
            logging.debug(f"Backup created: {self.backup_file}.")
        except Exception as e:
            logging.error(f"Failed to create backup: {e}.")

    def restore_backup(self):
        """
        Checks if the backup file exists and restores library from it.

        :return: None
        :raises Exception: If any error occurs during the file operation.
        """
        try:
            if exists(self.backup_file):
                copy(self.backup_file, self.db_file)
                logging.info(f"Backup restored from {self.backup_file}.")
            else:
                logging.warning("Backup file does not exist.")
        except Exception as e:
            logging.error(f"Failed to restore backup: {e}.")

    def migrate(self, old_header: list) -> None:
        """
        Performs migration of a library structure.

        Backups a library db file. Creates a temporary file. Overwrites the
        existing table into it, changing the order of columns and inserting
        new columns according to the config. after all, overwrites the db
        file with a temporary file.

        :param old_header: (list) Previous header of the library database.
        :return: None
        :raises Exception: If any error occurs during the file operation
        """
        logging.info("Starting migration.")
        self.create_backup()

        try:
            with NamedTemporaryFile(mode="w", encoding="utf-8",
                                    newline="", delete=False) as temp_file:
                with open(self.db_file, encoding="utf-8", mode="r", newline="") as f:
                    reader = csv.reader(f)
                    next(reader)  # Skip header.
                    writer = csv.writer(temp_file)
                    writer.writerow(TABLE_FIELDS)  # New header.
                    for row in reader:
                        new_row = [
                            row[old_header.index(field)] if field in old_header else ""
                            for field in TABLE_FIELDS
                        ]
                        writer.writerow(new_row)

            move(temp_file.name, self.db_file)
            logging.info("Migration done.")
        except Exception as e:
            logging.error(f"Migration failed: {e}.")
            self.restore_backup()


    def select_all(self) -> None:
        """
        Retrieves all books from the library database.

        Reads the library database file and returns a list of all books,
        excluding the header row. Each book is represented as a list of its fields.

        :return: A list of all books in the library.
        :raises FileNotFoundError: If the database file is not found.
        :raises Exception: If any other error occurs during the file operation.
        """
        logging.debug("Starting selection all books.")
        try:
            with open(self.db_file, encoding="utf-8", mode="r") as f:
                reader = csv.reader(f)
                books = list(reader)[1:]
                logging.info("Books found:")
                for row in books:
                    logging.info(row)
                # RETURN BOOKS HERE.
        except FileNotFoundError:
            logging.error(f"Error: {self.db_file} not found.")
        except Exception as e:
            logging.error(f"An error occurred: {e}.")


    def select(self, **filters) -> None:
        """
        Finds books in the database that match the given filters.

        This method allows to search for books based on various attributes, such as
        title, author, year, etc. Filters are passed as key-value pairs where keys
        are column names (e.g., 'title', 'author', etc.), and values are the values
        to search for.

        Example usage:
            dao.find(title='Война и мир', author='Толстой')
            dao.find(**{'title': 'Война и мир', 'author': 'Толстой'})
            This will return a list of books where the title is "Война и мир" and
            the author is "Толстой".

        :param filters: Key-value pairs representing the filters (column name: key).
                        if none, finds all books in the database.
        :return: None.
        :raises FileNotFoundError: If the database file is not found.
        :raises Exception: If any other error occurs during the file operation.
        """
        logging.debug(f"Starting selection books with filters {filters}.")

        actual_filters = dict()
        for key in filters.keys():
            if key not in USERS_FILTERS:
                logging.warning(f"Filter {key} is not available and will be ignored.")
            else:
                actual_filters[key] = filters[key]
        logging.debug(f"Cleaned filters are: {actual_filters}.")

        filtered_books = []

        for key in actual_filters.keys():
            key_col_index = TABLE_FIELDS.index(key)

            if len(filtered_books) == 0:
                try:
                    with open(self.db_file, encoding="utf-8", mode="r") as f:
                        reader = csv.reader(f)
                        next(reader)  # Skip header.
                        for row in reader:
                            if row[key_col_index].lower() == filters[key].lower():
                                filtered_books.append(row)
                    logging.debug("First filter was used successfully. No file errors.")
                except FileNotFoundError:
                    logging.error(f"Error: {self.db_file} not found")
                except Exception as e:
                    logging.error(f"An error occurred: {e}")
            else:
                for book in filtered_books:
                    if book[key_col_index].lower() != filters[key].lower():
                        filtered_books.remove(book)

        logging.info("Books found:")
        for book in filtered_books:
            logging.info(book)

    def insert(self, title: str, author: str, year: str) -> None:
        """
        Inserts a new book into the database.

        Adds a book with the provided title, author, and year to the library.
        Automatically generates a unique ID and sets the book status to "в наличии".

        :param title: The title of the book to be added.
        :param author: The author of the book to be added.
        :param year: The year of publication of the book.
        :return: None.
        """
        logging.debug(f"Starting insertion book {title} {author} {year}.")
        try:
            book_id = count_rows(self.db_file)
            logging.debug(f"The new book ID: {book_id}.")
        except Exception as e:
            logging.error(f"Getting the new book id was failed. {e}")
            return
        try:
            with open(self.db_file, encoding="utf-8", mode="a", newline="") as f:
                writer = csv.writer(f)
                new_row = []
                for col in TABLE_FIELDS:
                    if col == "id":
                        new_row.append(book_id)
                    elif col == "title":
                        new_row.append(title)
                    elif col == "author":
                        new_row.append(author)
                    elif col == "year":
                        new_row.append(year)
                    elif col == "status":
                        new_row.append("в наличии")
                    else:
                        new_row.append("")
                writer.writerow(new_row)
                logging.info(f"Book {title} {author} {year} was inserted successfully.")
        except FileNotFoundError:
            logging.error(f"Error: {self.db_file} not found.")
        except Exception as e:
            logging.error(f"An error occurred: {e}.")

    def delete(self, book_id: str) -> None:
        """
        Deletes a book with the specified ID from the library database.

        Reads the database file, excludes the row corresponding to the given
        book ID, and writes the remaining data to a temporary file, which
        then replaces the original database file.

        :param book_id: The ID of the book to be deleted.
        :return: None
        :raises FileNotFoundError: If the database file is not found.
        :raises Exception: If any other error occurs during the file operation.
        """
        logging.debug(f"Starting deletion book with id {book_id}.")
        id_field_index = TABLE_FIELDS.index("id")

        try:
            # Flag to track the availability of the book you are looking for.
            # Change it to True, when book will be found and deleted.
            deleted = False
            with NamedTemporaryFile(mode="w", encoding="utf-8",
                                    newline="", delete=False) as temp_file:
                with open(self.db_file, encoding="utf-8", mode="r", newline="") as f:
                    reader = csv.reader(f)
                    writer = csv.writer(temp_file)

                    for row in reader:
                        if row[id_field_index] == book_id:
                            deleted = True
                            continue
                        writer.writerow(row)

            move(temp_file.name, self.db_file)

            if deleted:
                logging.info(f"Book with id {book_id} was successfully deleted.")
            else:
                logging.info(f"Book with id {book_id} was not found.")
        except FileNotFoundError:
            logging.error(f"Error: {self.db_file} not found.")
        except Exception as e:
            logging.error(f"An error occurred: {e}.")

    def modify(self, book_id: str, status: str) -> None:
        """
        Modifies the status of a book with the specified ID in the library database.

        The method validates the new status, checks its validity, and then updates
        the status of the book in the database. A temporary file is used to write the
        updated data, which replaces the original database file.

        :param book_id: The ID of the book to be modified.
        :param status: The new status to assign to the book (e.g., "в наличии", "выдана").
        :return: None
        :raises ValueError: If the provided status is invalid.
        :raises FileNotFoundError: If the database file is not found.
        :raises Exception: If any other error occurs during the file operation.
        """
        logging.debug(f"Starting modification book with id {book_id} status by {status}.")
        status = status.strip().lower()  # Clear user input.
        # Check if status book is valid.
        if status not in BOOKS_STATUSES:
            logging.warning(f"Status '{status}' is not available. "
                            f"Existing statuses are {BOOKS_STATUSES}.")
            return
        # Find table indices, because they can change when DB migrated.
        id_field_index = TABLE_FIELDS.index("id")
        status_field_index = TABLE_FIELDS.index("status")
        try:
            # Flag to track the availability of the book you are looking for.
            # Change it to True, when book will be found and modified.
            modified = False
            with NamedTemporaryFile(mode="w", encoding="utf-8",
                                    newline="", delete=False) as temp_file:
                with open(self.db_file, encoding="utf-8",
                          mode="r", newline="") as f, temp_file:
                    reader = csv.reader(f)
                    writer = csv.writer(temp_file)

                    for row in reader:
                        if row[id_field_index] == book_id:
                            modified = True
                            row[status_field_index] = status
                        writer.writerow(row)

            move(temp_file.name, self.db_file)
            if modified:
                logging.info(f"Book with id {book_id} was successfully modified.")
            else:
                logging.info(f"Book with id {book_id} was not found.")
        except FileNotFoundError:
            logging.error(f"Error: {self.db_file} not found.")
        except Exception as e:
            logging.error(f"An error occurred: {e}.")
