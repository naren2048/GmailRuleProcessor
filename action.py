class Action:
    """
    A class to represent an action to be performed on an email.

    Attributes:
        action_type (str): The type of action to be performed (e.g., 'mark_as_read', 'mark_as_unread', 'move_message').
        logger (logging.Logger): The logger instance to log messages.
    """

    def __init__(self, action_type, logger, new_folder=None):
        """
        Initializes the Action class.

        Args:
            action_type (str): The type of action to be performed.
            logger (logging.Logger): The logger instance to log messages.
        """
        self.action_type = action_type
        self.logger = logger
        self.new_folder = new_folder

    def execute(self, email, service):
        """
        Executes the specified action on the given email.

        Args:
            email (Email): The email object containing email details.
            service (googleapiclient.discovery.Resource): The authenticated Gmail service instance.
            folder_name (str, optional): The folder name to move the email to (required for 'move_message' action).

        Raises:
            ValueError: If an invalid action type is provided.
        """
        self.logger.info(f"Executing action: {self.action_type} for email: {email.email_id}")
        if self.action_type == "mark_as_read":
            self.logger.debug("Starting mark as read action")
            self.mark_as_read(email, service)
        elif self.action_type == "mark_as_unread":
            self.logger.debug("Starting mark as unread action")
            self.mark_as_unread(email, service)
        elif self.action_type == "move_message":
            self.logger.debug(f"Starting move message action, New Folder: {self.new_folder}")
            self.move_message(email.email_id, service)
        else:
            self.logger.error(f"Invalid action type: {self.action_type}")
            raise ValueError(f"Invalid action type: {self.action_type}")

    def mark_as_read(self, email, service):
        """
        Marks the specified email as read.

        Args:
            email (Email): The email object containing email details.
            service (googleapiclient.discovery.Resource): The authenticated Gmail service instance.
        """
        self.logger.info(f"Marking email as read: {email.email_id}")
        service.users().messages().modify(
            userId='me',
            id=email.email_id,
            body={'removeLabelIds': ['UNREAD']}
        ).execute()
        self.logger.info(f"Email {email.email_id} marked as read")


    def mark_as_unread(self, email, service):
        """
        Marks the specified email as unread.

        Args:
            email (Email): The email object containing email details.
            service (googleapiclient.discovery.Resource): The authenticated Gmail service instance.
        """
        self.logger.info(f"Marking email as unread: {email.email_id}")
        service.users().messages().modify(
            userId='me',
            id=email.email_id,
            body={'addLabelIds': ['UNREAD']}
        ).execute()
        self.logger.info(f"Email {email.email_id} marked as unread")


    def move_message(self, email_id, service):
        """
        Moves the specified email to the given folder.

        Args:
            email_id (str): The ID of the email to be moved.
            service (googleapiclient.discovery.Resource): The authenticated Gmail service instance.

        """
        self.logger.info(f"Moving email: {email_id} to folder: {self}")

        # Find the label ID for the folder name
        labels = service.users().labels().list(userId='me').execute().get('labels', [])
        folder_label = next((label for label in labels if label['name'] == self.new_folder), None)

        if folder_label:
            folder_label_id = folder_label['id']
            self.logger.debug(f"Folder {self.new_folder} exists with ID: {folder_label_id}")
        else:
            # Create the folder if it doesn't exist
            self.logger.debug(f"Folder {self.new_folder} does not exist, creating new folder.")
            new_label = service.users().labels().create(userId='me', body={'name': self.new_folder}).execute()
            folder_label_id = new_label['id']
            self.logger.info(f"Created new folder {self.new_folder} with ID: {folder_label_id}")

        # Move the email by adding the folder label and removing the INBOX label
        service.users().messages().modify(
            userId='me',
            id=email_id,
            body={'addLabelIds': [folder_label_id], 'removeLabelIds': ['INBOX']}
        ).execute()
        self.logger.info(f"Email {email_id} moved to folder {self.new_folder}")
