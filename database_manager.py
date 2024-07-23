from sqlalchemy import create_engine, Column, String, DateTime, Text, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class Email(Base):
    """
    A class used to represent an Email.

    Attributes:
        id (int): The primary key of the email record.
        email_id (str): The unique identifier for the email.
        sender (str): The email address of the sender.
        subject (str, optional): The subject of the email.
        body (str, optional): The body content of the email.
        date_received (datetime, optional): The date and time the email was received.
    """
    __tablename__ = 'emails'

    id = Column(Integer, primary_key=True)
    email_id = Column(String, nullable=False)
    sender = Column(String, nullable=False)
    subject = Column(String, nullable=True)
    body = Column(Text, nullable=True)
    date_received = Column(DateTime, nullable=True)


class DatabaseManager:
    """
    A class to manage the database operations for the Email records.

    Attributes:
        db_url (str): The database URL.
        engine (sqlalchemy.engine.base.Engine): The SQLAlchemy engine connected to the database.
        Session (sqlalchemy.orm.session.sessionmaker): The session factory for creating new sessions.
    """

    def __init__(self, db_url):
        """
        Initializes the DatabaseManager with the given database URL.

        Args:
            db_url (str): The database URL.
        """
        self.engine = create_engine(db_url)
        self.Session = sessionmaker(bind=self.engine)
        Base.metadata.create_all(self.engine)

    def create_session(self):
        """
        Creates and returns a new database session.

        Returns:
            sqlalchemy.orm.session.Session: A new database session.
        """
        return self.Session()
