import unittest
from unittest.mock import MagicMock, patch
from rule_processor import RuleProcessor
from database_manager import Email
import json

class TestRuleProcessor(unittest.TestCase):

    @patch('rule_processor.DatabaseManager')
    @patch('rule_processor.Action')
    @patch('rule_processor.Rule')
    def setUp(self, MockRule, MockAction, MockDatabaseManager):
        self.logger = MagicMock()
        self.rules_file = 'rules.json'
        self.db_url = 'sqlite:///:memory:'
        self.service = MagicMock()

        # Mock database manager
        self.mock_db_manager = MockDatabaseManager.return_value
        self.mock_session = MagicMock()
        self.mock_db_manager.create_session.return_value.__enter__.return_value = self.mock_session

        # Mock Rule and Action
        self.mock_rule = MockRule.return_value
        self.mock_action = MockAction.return_value

        # Create a RuleProcessor instance
        self.rule_processor = RuleProcessor(self.logger, self.rules_file, self.db_url, self.service)

        # Mock rules loading
        self.rules_json = [
            {
                "conditions": [
                    {"field_name": "subject", "predicate": "contains", "value": "test"}
                ],
                "overall_predicate": "All",
                "actions": ["move_message"]
            }
        ]
        self.mock_rule.evaluate.return_value = True
        self.mock_action.execute.return_value = None

        with patch('builtins.open', unittest.mock.mock_open(read_data=json.dumps(self.rules_json))):
            self.rule_processor.rules = self.rule_processor.load_rules(self.rules_file)

    def test_process_emails(self):
        # Setup mock emails
        email1 = Email(email_id='email_1', subject='test email')
        email2 = Email(email_id='email_2', subject='another test email')
        self.mock_session.query().all.return_value = [email1, email2]

        # Process emails
        self.rule_processor.process_emails()

    def test_apply_actions(self):
        email = Email(email_id='email_1', subject='test email')
        action = MagicMock()
        action.action_type = 'move_message'

        # Apply actions
        self.rule_processor.apply_actions(email, [action])

        # Verify that action was executed
        action.execute.assert_called_with(email, self.service)


