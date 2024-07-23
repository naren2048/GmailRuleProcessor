import os
import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.labels'
]

class GmailAuthenticator:
    """
    A class to authenticate with Gmail API using OAuth 2.0.

    Attributes:
        logger (logging.Logger): The logger instance to log messages.
        credentials_file (str): Path to the credentials JSON file.
        token_file (str): Path to the token pickle file.
    """

    def __init__(self, logger, credentials_file='credentials.json', token_file='token.pickle'):
        """
        Initializes the GmailAuthenticator class.

        Args:
            logger (logging.Logger): The logger instance to log messages.
            credentials_file (str): Path to the credentials JSON file.
            token_file (str): Path to the token pickle file.
        """
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.logger = logger

    def authenticate(self):
        """
        Authenticates the user with Gmail and returns a service instance.

        Returns:
            googleapiclient.discovery.Resource: The authenticated Gmail service instance.

        Raises:
            Exception: If authentication fails.
        """
        self.logger.info('Starting authentication process.')

        creds = None
        if os.path.exists(self.token_file):
            self.logger.info('Token file found, loading credentials.')
            with open(self.token_file, 'rb') as token:
                creds = pickle.load(token)
        else:
            self.logger.info('Token file not found.')

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                self.logger.info('Refreshing expired credentials.')
                creds.refresh(Request())
            else:
                self.logger.info('Credentials not available or invalid, starting OAuth flow.')
                flow = InstalledAppFlow.from_client_secrets_file(self.credentials_file, SCOPES)
                creds = flow.run_local_server(port=0)
                self.logger.info('OAuth flow completed, credentials obtained.')

            with open(self.token_file, 'wb') as token:
                pickle.dump(creds, token)
                self.logger.info('Credentials saved to token file.')

        self.logger.info('Authentication process completed successfully.')
        return build('gmail', 'v1', credentials=creds)
