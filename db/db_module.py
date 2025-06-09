from pony.orm import Database
from urllib.parse import urlparse
from config import DATABASE_URL
from db.models import *
import logging

db = Database()

db_params = {
    "provider": "postgres",
    "user": "worken",
    "password": "worken",
    "host": "localhost",
    "port": 5432,
    # main
    "database": "worken_constructor_bot",
    # "database": "bot_local",
}

if DATABASE_URL:
    db_url = urlparse(DATABASE_URL)
    db_params = {
        "provider": "postgres",
        "user": db_url.username,
        "password": db_url.password,
        "host": "/cloudsql/pom4h-bank:us-central1:pg16",
        "port": db_url.port or 5432,
        # main
        "database": "worken_constructor_bot",
        # "database": "bot_local",
    }


def connect_to_db() -> None:
    try:
        if db.provider is None:
            db.bind(**db_params)
            db.generate_mapping(create_tables=True)
            logging.info("Successfully connected to the database.")
        else:
            logging.debug("Database is already connected.")
    except Exception as e:
        logging.exception("Failed to connect to the database.")


# if __name__ == '__main__':
#     connect_to_db()
