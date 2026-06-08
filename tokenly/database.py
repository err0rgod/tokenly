"""
Database utility module for managing the SQLModel engine and sessions.
Provides boilerplate for connecting to a database and initializing tables.
"""

from sqlmodel import SQLModel, create_engine, Session
from typing import Generator

class DatabaseManager:
    """
    Manages database connection and session lifecycle.

    Attributes:
        engine: The SQLAlchemy engine for database communication.
    """

    def __init__(self, db_url: str = "sqlite:///./database.db", echo: bool = False):
        """
        Initializes the database engine.

        Args:
            db_url (str): The database connection string. Defaults to a local SQLite file.
            echo (bool): If True, SQL statements will be logged to stdout.
        """
        self.engine = create_engine(db_url, echo=echo)

    def init_db(self):
        """
        Creates all tables defined in the models.
        Should be called once during application startup.
        """
        SQLModel.metadata.create_all(self.engine)

    def get_session(self) -> Generator[Session, None, None]:
        """
        Provides a database session for use in a context manager or dependency injection.

        Yields:
            Session: A SQLModel session object.
        """
        with Session(self.engine) as session:
            yield session
