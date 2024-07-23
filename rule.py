# rule.py

import logging

class Rule:
    """
    A class used to define and evaluate rules for filtering emails.

    Attributes:
        field_name (str): The field name of the email to be evaluated.
        predicate (str): The condition to be checked on the field.
        value (str): The value to be compared against the field value.
    """

    def __init__(self, field_name, predicate, value, logger):
        """
        Initializes the Rule with the given field name, predicate, and value.

        Args:
            field_name (str): The field name of the email to be evaluated.
            predicate (str): The condition to be checked on the field.
            value (str): The value to be compared against the field value.
        """
        self.field_name = field_name
        self.predicate = predicate
        self.value = value
        self.logger = logger

        self.logger.debug(f"Initialized Rule: field_name={field_name}, predicate={predicate}, value={value}")

    def evaluate(self, email):
        """
        Evaluates the rule against the given email.

        Args:
            email (Email): The email object to be evaluated.

        Returns:
            bool: True if the rule condition is met, False otherwise.
        """
        field_value = getattr(email, self.field_name, None)
        self.logger.debug(f"Evaluating Rule: field_name={self.field_name}, predicate={self.predicate}, value={self.value}, email_field_value={field_value}")

        if field_value is None:
            self.logger.debug("Field value is None, returning False.")
            return False

        if self.predicate == "contains":
            result = self.value in field_value
        elif self.predicate == "not_contains":
            result = self.value not in field_value
        elif self.predicate == "equals":
            result = self.value == field_value
        elif self.predicate == "not_equals":
            result = self.value != field_value
        elif self.predicate == "less_than":
            result = field_value < self.value
        elif self.predicate == "greater_than":
            result = field_value > self.value
        else:
            self.logger.error(f"Unknown predicate: {self.predicate}")
            return False

        self.logger.debug(f"Evaluation result: {result}")
        return result
