# rule_processor.py

import json
from database_manager import DatabaseManager, Email
from rule import Rule
from action import Action

class RuleProcessor:
    """
    A class used to process rules on emails and perform actions based on those rules.

    Attributes:
        db_manager (DatabaseManager): The database manager for email storage.
        rules (list): A list of rules to be applied.
        service: The service object for interacting with Gmail API.
        logger: The logger object for logging messages.
    """

    def __init__(self, logger, rules_file, db_url="sqlite:///emails.db", service=None):
        """
        Initializes the RuleProcessor with the given parameters.

        Args:
            logger: The logger object for logging messages.
            rules_file (str): The file path to the JSON file containing rules.
            db_url (str): The database URL for storing emails.
            service: The service object for interacting with Gmail API.
        """
        self.db_manager = DatabaseManager(db_url)
        self.logger = logger
        self.rules = self.load_rules(rules_file)
        self.service = service

        self.logger.debug(f"Initialized RuleProcessor with rules from {rules_file} and database {db_url}")

    def load_rules(self, rules_file):
        """
        Loads rules from the specified JSON file.

        Args:
            rules_file (str): The file path to the JSON file containing rules.

        Returns:
            list: A list of rule dictionaries.
        """
        with open(rules_file, 'r') as file:
            rules_json = json.load(file)
        rules = []
        for rule in rules_json:
            conditions = [Rule(cond['field_name'], cond['predicate'], cond['value'], self.logger) for cond in rule['conditions']]
            actions = []
            folder = rule.get('folder', '')
            for action in rule['actions']:
                if action == "move_message":
                    actions.append(Action(action, self.logger, new_folder=folder))
                else:
                    actions.append(Action(action, self.logger))
            rules.append({'conditions': conditions, 'overall_predicate': rule['overall_predicate'], 'actions': actions})

        self.logger.debug(f"Loaded {len(rules)} rules from {rules_file}")
        return rules

    def process_emails(self):
        """
        Processes all emails in the database by applying rules and executing actions if conditions are met.
        """
        self.logger.debug("Starting to process emails.")
        session = self.db_manager.create_session()
        emails = session.query(Email).all()
        self.logger.debug(f"Fetched {len(emails)} emails from database.")

        for email in emails:
            self.logger.debug(f"Processing email with ID: {email.email_id}")
            for rule in self.rules:
                conditions = rule['conditions']
                overall_predicate = rule['overall_predicate']
                actions = rule['actions']

                if overall_predicate == "All":
                    if all(cond.evaluate(email) for cond in conditions):
                        self.logger.debug(f"Email ID: {email.email_id} matched all conditions of a rule.")
                        self.apply_actions(email, actions)
                elif overall_predicate == "Any":
                    if any(cond.evaluate(email) for cond in conditions):
                        self.logger.debug(f"Email ID: {email.email_id} matched any condition of a rule.")
                        self.apply_actions(email, actions)

        session.close()
        self.logger.debug("Finished processing emails.")

    def apply_actions(self, email, actions):
        """
        Applies the specified actions to the email.

        Args:
            email (Email): The email object to apply actions to.
            actions (list): A list of actions to be executed.
        """
        self.logger.debug(f"Applying {len(actions)} actions to email with ID: {email.email_id}")
        for action in actions:
            action.execute(email, self.service)
            self.logger.debug(f"Executed action: {action.action_type} on email ID: {email.email_id}")
