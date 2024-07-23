import unittest
from unittest.mock import Mock, patch
from parameterized import parameterized
from action import Action


class TestAction(unittest.TestCase):

    def setUp(self):
        self.logger = Mock()

    @parameterized.expand([
        ("mark_as_read", "mark_as_read"),
        ("mark_as_unread", "mark_as_unread"),
        ("move_message", "move_message"),
    ])
    @patch('googleapiclient.discovery.Resource')
    def test_execute_valid_actions(self, name, action_type, mock_service):
        email = Mock()
        email.email_id = "123"
        action = Action(action_type, self.logger, new_folder="TestFolder" if action_type == "move_message" else None)

        if action_type == "move_message":
            # Mock the service responses for move_message
            mock_service.users().labels().list().execute.return_value = {'labels': []}
            mock_service.users().labels().create().execute.return_value = {'id': 'LabelId'}

        action.execute(email, mock_service)

        if action_type == "mark_as_read":
            self.logger.info.assert_called_with("Email 123 marked as read")
            self.logger.debug.assert_called_with("Starting mark as read action")
            mock_service.users().messages().modify.assert_called_with(
                userId='me',
                id=email.email_id,
                body={'removeLabelIds': ['UNREAD']}
            )
        elif action_type == "mark_as_unread":
            self.logger.info.assert_called_with("Email 123 marked as unread")
            self.logger.debug.assert_called_with("Starting mark as unread action")
            mock_service.users().messages().modify.assert_called_with(
                userId='me',
                id=email.email_id,
                body={'addLabelIds': ['UNREAD']}
            )
        elif action_type == "move_message":
            mock_service.users().labels().list().execute.assert_called()
            mock_service.users().labels().create.assert_called_with(
                userId='me', body={'name': 'TestFolder'}
            )
            mock_service.users().messages().modify.assert_called_with(
                userId='me',
                id=email.email_id,
                body={'addLabelIds': ['LabelId'], 'removeLabelIds': ['INBOX']}
            )
            self.logger.info.assert_called_with("Email 123 moved to folder TestFolder")

    @patch('googleapiclient.discovery.Resource')
    def test_execute_invalid_action(self, mock_service):
        email = Mock()
        email.email_id = "123"
        action = Action("invalid_action", self.logger)

        with self.assertRaises(ValueError) as context:
            action.execute(email, mock_service)

        self.assertEqual(str(context.exception), "Invalid action type: invalid_action")
        self.logger.error.assert_called_with("Invalid action type: invalid_action")


