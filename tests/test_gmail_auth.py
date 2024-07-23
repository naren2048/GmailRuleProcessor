import unittest
from unittest.mock import patch, MagicMock
import os
import pickle
from gmail_authenticator import GmailAuthenticator, SCOPES  # Adjust the import according to your project structure

class TestGmailAuthenticator(unittest.TestCase):

    def setUp(self):
        self.logger = MagicMock()
        self.credentials_file = 'test_credentials.json'
        self.token_file = 'test_token.pickle'
        self.authenticator = GmailAuthenticator(self.logger, self.credentials_file, self.token_file)

    @patch('gmail_authenticator.os.path.exists')
    @patch('gmail_authenticator.pickle.load')
    @patch('gmail_authenticator.pickle.dump')
    @patch('gmail_authenticator.InstalledAppFlow')
    @patch('gmail_authenticator.build')
    @patch('gmail_authenticator.Request')
    def test_authenticate_with_existing_valid_token(self, MockRequest, MockBuild, MockInstalledAppFlow, MockPickleDump, MockPickleLoad, MockOsPathExists):
        # Mock a valid token
        mock_creds = MagicMock()
        mock_creds.valid = True

        MockOsPathExists.return_value = True
        MockPickleLoad.return_value = mock_creds

        # Call the authenticate method
        service = self.authenticator.authenticate()

        # Assertions
        self.logger.info.assert_any_call('Starting authentication process.')
        self.logger.info.assert_any_call('Token file found, loading credentials.')
        self.logger.info.assert_any_call('Authentication process completed successfully.')
        MockBuild.assert_called_once_with('gmail', 'v1', credentials=mock_creds)
        self.assertEqual(service, MockBuild.return_value)

    @patch('gmail_authenticator.os.path.exists')
    @patch('gmail_authenticator.pickle.load')
    @patch('gmail_authenticator.pickle.dump')
    @patch('gmail_authenticator.InstalledAppFlow')
    @patch('gmail_authenticator.build')
    @patch('gmail_authenticator.Request')
    def test_authenticate_with_expired_token_and_refresh(self, MockRequest, MockBuild, MockInstalledAppFlow, MockPickleDump, MockPickleLoad, MockOsPathExists):
        # Mock an expired token with a refresh token
        mock_creds = MagicMock()
        mock_creds.valid = False
        mock_creds.expired = True
        mock_creds.refresh_token = True

        MockOsPathExists.return_value = True
        MockPickleLoad.return_value = mock_creds

        # Call the authenticate method
        service = self.authenticator.authenticate()

        # Assertions
        self.logger.info.assert_any_call('Refreshing expired credentials.')
        mock_creds.refresh.assert_called_once_with(MockRequest())
        self.logger.info.assert_any_call('Authentication process completed successfully.')
        MockBuild.assert_called_once_with('gmail', 'v1', credentials=mock_creds)
        self.assertEqual(service, MockBuild.return_value)

    @patch('gmail_authenticator.os.path.exists')
    @patch('gmail_authenticator.pickle.load')
    @patch('gmail_authenticator.pickle.dump')
    @patch('gmail_authenticator.InstalledAppFlow')
    @patch('gmail_authenticator.build')
    @patch('gmail_authenticator.Request')
    def test_authenticate_with_no_existing_token(self, MockRequest, MockBuild, MockInstalledAppFlow, MockPickleDump, MockPickleLoad, MockOsPathExists):
        # Mock no existing token
        mock_creds = MagicMock()
        mock_creds.valid = True

        MockOsPathExists.return_value = False
        mock_flow = MockInstalledAppFlow.from_client_secrets_file.return_value
        mock_flow.run_local_server.return_value = mock_creds

        # Call the authenticate method
        service = self.authenticator.authenticate()

        # Assertions
        self.logger.info.assert_any_call('Token file not found.')
        self.logger.info.assert_any_call('Credentials not available or invalid, starting OAuth flow.')
        MockInstalledAppFlow.from_client_secrets_file.assert_called_once_with(self.credentials_file, SCOPES)
        mock_flow.run_local_server.assert_called_once_with(port=0)
        MockPickleDump.assert_called_once_with(mock_creds, unittest.mock.ANY)
        self.logger.info.assert_any_call('Credentials saved to token file.')
        self.logger.info.assert_any_call('Authentication process completed successfully.')
        MockBuild.assert_called_once_with('gmail', 'v1', credentials=mock_creds)
        self.assertEqual(service, MockBuild.return_value)

