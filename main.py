#!/usr/bin/python
# -*- coding: UTF-8 -*-

import argparse
import logging

# Try to import constants from config.py.
try:
    from config import TABLE_FILE, LOGGING_LEVEL, USERS_FILTERS
# If file does not exist, generate a new one.
except ModuleNotFoundError:
    from utils import generate_config_file
    generate_config_file()
    from config import TABLE_FILE, LOGGING_LEVEL, USERS_FILTERS
from dao import LibraryManagementSystem


def run_cli(args, dao: LibraryManagementSystem) -> None:
    match args.command:
        case "add":
            dao.insert(args.title, args.author, args.year)
        case "delete":
            dao.delete(args.id)
        case "find":
            filters = dict()
            for _ in USERS_FILTERS:
                value = getattr(args, _)
                if value:
                    filters[_] = value
            dao.select(**filters)
        case "list":
            dao.select_all()
        case "modify":
            dao.modify(args.id, args.status)


def run_repl(dao: LibraryManagementSystem) -> None:
    """
    Interactive session mode.

    :param dao: LibraryManagementSystem class object provides CRUD operations.
    :return: None.
    """
    print("Interactive mode. Enter 'help' for commands list or 'exit' to exit.")
    while True:
        try:
            command = input("> ").strip()
            if command == "exit":
                print("Exit.")
                break
            elif command == "help":
                print("Available commands:")
                print("  add <title> <author> <year> - add a new book")
                print("  delete <id> - delete book by ID")
                for key in USERS_FILTERS:
                    print(f"  find {key} <{key}> - find book by {key}")
                print("  find key1 <val1> key2 <val2> ... keyN <valN> - find book by several filters")
                print("  list - show all books")
                print("  modify <id> <status> - change book status")
                print("  exit - quit the session")
            else:
                args = command.replace("'", "").replace('"', "").split(" ")
                if args[0] == "add" and len(args) == 4:
                    dao.insert(args[1], args[2], args[3])
                elif args[0] == "delete" and len(args) == 2:
                    dao.delete(args[1])
                elif args[0] == "find" and len(args) % 2 == 1:
                    if len(args) == 1:
                        dao.select_all()
                        continue
                    # Get filters from scrypt arguments.
                    filters = args[1:]
                    # Separate filters into keys and values.
                    filter_keys = [filters[i] for i in range(0, len(filters), 2)]
                    filter_values = [filters[i] for i in range(1, len(filters), 2)]
                    if len(filter_keys) != len(filter_values):
                        logging.warning("Mismatch between filter keys and values.")
                    else:
                        filters = dict(zip(filter_keys, filter_values))
                        dao.select(**filters)
                elif args[0] == "list" and len(args) == 1:
                    dao.select_all()
                elif args[0] == "modify":
                    if len(args) == 3:
                        dao.modify(args[1], args[2])
                    else:
                        dao.modify(args[1], " ".join(args[2:]))
                else:
                    print("Undefined command. Enter 'help' for commands list.")
        except Exception as e:
            logging.error(f"Error: {e}")

def main() -> None:
    """
    Main entry point for the Library Management System.

    Sets up logging, configures command-line argument parsing, and determines the mode of operation:
    either CLI mode (based on provided arguments) or REPL mode (interactive session).

    Features:
    - Adds books to the library.
    - Deletes books by ID.
    - Searches for books using optional filters.
    - Lists all books in the library.
    - Modifies the status of a book by its ID.

    :return: None
    """
    logging.basicConfig(level=getattr(logging, LOGGING_LEVEL.upper()),
                        format="[%(levelname)s][%(asctime)s] %(message)s",
                        datefmt="%d.%m.%Y %H:%M:%S")

    parser = argparse.ArgumentParser(
        description="Library Management System allows you to manage a "
                    "library of books. You can add, remove, search, and "
                    "modify books in the library using various commands.",
    )

    subparsers = parser.add_subparsers(dest="command")

    parser_add = subparsers.add_parser(
        "add", help="Add book"
    )
    parser_add.add_argument("title", help="Book title")
    parser_add.add_argument("author", help="Book author")
    parser_add.add_argument("year", help="Year of publication")

    parser_delete = subparsers.add_parser(
        "delete", help="Delete book"
    )
    parser_delete.add_argument("id", help="Book id to delete")

    parser_find = subparsers.add_parser(
        "find", help="Find book by filters"
    )
    for _ in USERS_FILTERS:
        parser_find.add_argument(
            f"-{_[0]}", f"--{_}", help=f"Book {_} to find"
        )

    parser_list = subparsers.add_parser(
        "list", help="Show all books list"
    )

    parser_modify = subparsers.add_parser(
        "modify", help="Modify book status"
    )
    parser_modify.add_argument("id", help="Book ID to modify")
    parser_modify.add_argument("status", help="New status")

    args = parser.parse_args()
    dao = LibraryManagementSystem(TABLE_FILE)

    if any(vars(args).values()):
        # If arguments given, run CLI.
        run_cli(args, dao)
    else:
        # If no arguments, run REPL.
        run_repl(dao)


if __name__ == "__main__":
    main()
