# Gmail Rule Processor

The Gmail Rule Processor is a Python project designed to fetch emails from a Gmail account and process them based on specific rules. The project utilizes the Gmail API to interact with the user's Gmail account and SQLAlchemy for database interactions.

## Features

- Fetches emails from a Gmail account using the Gmail API.
- Stores email metadata and content in a local database.
- Processes emails based on user-defined rules.


## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/naren2048/GmailRuleProcessor.git
    cd GmailRuleProcessor
    ```

2. Create a virtual environment and activate it:

    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install the required packages:

    ```bash
    pip install -r requirements.txt
    ```

4. Set up Gmail API credentials:

    - Go to the [Google Developers Console](https://console.developers.google.com/).
    - Create a new project.
    - Enable the Gmail API for the project.
    - Create OAuth 2.0 credentials and download the `credentials.json` file.
    - Save the `credentials.json` file in the root directory of the project.


## Usage

1. Run the main script:

    ```bash
    python main.py --max_emails_read=500 --log_level="DEBUG"
    ```

    This will authenticate with the Gmail API and start fetching emails based on the defined rules.

### Command Line Arguments

- `--max_emails_read` (default: 500): 
  - Type: Integer
  - Description: Specifies the maximum number of emails to be read and processed from the Gmail account.
  - Usage: To change the maximum number of emails read, pass this argument with a desired integer value.
  - Example: 
    ```bash
    python main.py --max_emails_read=1000
    ```

- `--log_level` (default: "INFO"): 
  - Type: String
  - Description: Sets the logging level for the script. Possible values are "DEBUG", "INFO", "WARNING", "ERROR", and "CRITICAL".
  - Usage: To change the logging level, pass this argument with a desired log level string.
  - Example:
    ```bash
    python main.py --log_level="DEBUG"
    ```

## Testing

To run the tests, use the following command:

```bash
pytest
