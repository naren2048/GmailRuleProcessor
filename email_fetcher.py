# email_fetcher.py

import base64
from email import message_from_bytes
import datetime
from sqlalchemy.orm import sessionmaker
from database_manager import DatabaseManager, Email

class EmailFetcher:
    """
    A class used to fetch emails from the Gmail API and store them in the database.

    Attributes:
        logger (Logger): A logger instance to log messages.
        service (Resource): The Gmail API service instance.
        db_manager (DatabaseManager): An instance of the DatabaseManager to interact with the database.
    """

    def __init__(self, logger, service, db_url="sqlite:///emails.db"):
        """
        Initializes the EmailFetcher with the given logger, Gmail API service, and database URL.

        Args:
            logger (Logger): A logger instance to log messages.
            service (Resource): The Gmail API service instance.
            db_url (str): The URL of the database.
        """
        self.service = service
        self.db_manager = DatabaseManager(db_url)
        self.logger = logger

    def fetch_emails(self, email_count):
        """
        Fetches emails from the Gmail API and stores them in the database.

        This method fetches emails from the user's Gmail inbox, decodes and parses each email,
        and stores the email details in the database. If an email already exists in the database,
        it is skipped.
        """
        self.logger.info("Starting to fetch emails from Gmail API.")
        results = self.service.users().messages().list(userId='me', labelIds=['INBOX']).execute()
        messages = []

        while 'messages' in results:
            messages.extend(results['messages'])
            if len(messages) >= email_count:
                self.logger.info(f"Reached {email_count} email limit, stopping fetch.")
                break
            if 'nextPageToken' in results:
                page_token = results['nextPageToken']
                results = self.service.users().messages().list(userId='me', labelIds=['INBOX'], maxResults=500,
                                                               pageToken=page_token).execute()
            else:
                break

        with self.db_manager.create_session() as session:
            for message in messages:
                try:
                    self.logger.debug(f"Processing email with ID: {message['id']}")
                    existing_email = session.query(Email).filter_by(email_id=message['id']).first()
                    if existing_email:
                        self.logger.debug(f"Email with ID {message['id']} already exists in the database, skipping.")
                        continue

                    msg = self.service.users().messages().get(userId='me', id=message['id'], format='raw').execute()
                    msg_str = base64.urlsafe_b64decode(msg['raw'].encode('ASCII'))
                    mime_msg = message_from_bytes(msg_str)

                    email_id = message['id']
                    sender = mime_msg['From']
                    subject = mime_msg['Subject']
                    body = mime_msg.get_payload()

                    if body:
                        body = str(body[0])

                    date_received = mime_msg['Date']
                    date_received = date_received.replace(' (UTC)', '')
                    date_received = date_received.replace(' (IST)', '')
                    date_received = date_received.replace(' (GMT)', '')
                    date_received = date_received.replace(' (PDT)', '')
                    date_received = date_received.replace(' (CDT)', '')

                    date_received = datetime.datetime.strptime(date_received, '%a, %d %b %Y %H:%M:%S %z')

                    email = Email(email_id=email_id, sender=sender, subject=subject, body=body, date_received=date_received)
                    session.merge(email)

                except Exception as ex:
                    self.logger.error(f"Exception occurred for Email ID {message['id']}: {ex}")
                    continue

                with session.no_autoflush:
                    session.merge(email)
                session.commit()

        self.logger.info("Finished fetching and storing emails.")
