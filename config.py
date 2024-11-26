# Path of the DB file using for books storage. Must be '.csv' format.
TABLE_FILE = "books_data.csv"

# Fields of books table (CSV header, defines structure of the table).
# For correct books filtering, columns must start with different letters.
TABLE_FIELDS = (
    "id",
    "title",
    "author",
    "year",
    "status",
)

# Filters available to users to search for books. Must be columns of the table.
USERS_FILTERS = (
    "title",
    "author",
    "year",
)

# Valid books statuses (uses for validation of user input when change book status).
BOOKS_STATUSES = (
    "в наличии",
    "выдана",
)

# Setting the level of detail of logs. Must be DEBUG, INFO, WARNING, ERROR or CRITICAL.
LOGGING_LEVEL = "INFO"
