import unittest
from unittest.mock import MagicMock, patch
from parameterized import parameterized
import base64
from email.mime.text import MIMEText
from email_fetcher import EmailFetcher
from database_manager import Email

class TestEmailFetcher(unittest.TestCase):

    def setUp(self):
        self.logger = MagicMock()
        self.service = MagicMock()
        self.db_manager = MagicMock()
        self.email_fetcher = EmailFetcher(self.logger, self.service)
        self.email_fetcher.db_manager = self.db_manager

    @parameterized.expand([
        ("message_1", "Subject 1", "Body 1", "2023-06-01 12:00:00 +0000"),
        ("message_2", "Subject 2", "Body 2", "2023-06-02 13:00:00 +0000"),
    ])
    @patch('email_fetcher.DatabaseManager.create_session')
    def test_fetch_emails(self, email_id, subject, body, date_received, mock_create_session):
        # Setup mock Gmail service response
        self.service.users().messages().list.return_value.execute.return_value = {
            'messages': [{'id': email_id}]
        }
        mime_msg = MIMEText(body)
        mime_msg['From'] = 'test@example.com'
        mime_msg['Subject'] = subject
        mime_msg['Date'] = date_received

        raw_msg = base64.urlsafe_b64encode(mime_msg.as_bytes()).decode('ASCII')
        self.service.users().messages().get.return_value.execute.return_value = {'raw': raw_msg}

        # Setup mock database session
        mock_session = MagicMock()
        mock_create_session.return_value.__enter__.return_value = mock_session

        # Setup mock query object
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.filter_by.return_value = mock_query
        mock_query.first.return_value = None  # Simulate no existing email

        # Execute the method under test
        self.email_fetcher.fetch_emails()

        # Verify interactions with the database
        mock_session.query.assert_called_once_with(Email)
        mock_query.filter_by.assert_called_once_with(email_id=email_id)
        mock_query.first.assert_called_once()
        mock_session.merge.assert_called_once()
        mock_session.commit.assert_called_once()

        # Verify interactions with the Gmail API
        self.service.users().messages().list.assert_called_once_with(userId='me', labelIds=['INBOX'])
        self.service.users().messages().get.assert_called_once_with(userId='me', id=email_id, format='raw')

    @patch('email_fetcher.DatabaseManager.create_session')
    def test_fetch_emails_existing_email(self, mock_create_session):
        # Setup mock Gmail service response
        email_id = 'message_1'
        self.service.users().messages().list.return_value.execute.return_value = {
            'messages': [{'id': email_id}]
        }
        mime_msg = MIMEText('Body 1')
        mime_msg['From'] = 'test@example.com'
        mime_msg['Subject'] = 'Subject 1'
        mime_msg['Date'] = '2023-06-01 12:00:00 +0000'

        raw_msg = base64.urlsafe_b64encode(mime_msg.as_bytes()).decode('ASCII')
        self.service.users().messages().get.return_value.execute.return_value = {'raw': raw_msg}

        # Setup mock database session
        mock_session = MagicMock()
        mock_create_session.return_value.__enter__.return_value = mock_session

        # Setup mock query object
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.filter_by.return_value = mock_query
        mock_query.first.return_value = Email(email_id=email_id)  # Simulate existing email

        # Execute the method under test
        self.email_fetcher.fetch_emails()

        # Verify interactions with the database
        mock_session.query.assert_called_once_with(Email)
        mock_query.filter_by.assert_called_once_with(email_id=email_id)
        mock_query.first.assert_called_once()
        mock_session.merge.assert_not_called()
        mock_session.commit.assert_not_called()

        # Verify interactions with the Gmail API
        self.service.users().messages().list.assert_called_once_with(userId='me', labelIds=['INBOX'])
        self.service.users().messages().get.assert_called_once_with(userId='me', id=email_id, format='raw')

