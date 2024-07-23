

from gmail_authenticator import GmailAuthenticator
from email_fetcher import EmailFetcher
from rule_processor import RuleProcessor
from logger import SimpleLogger
import argparse



def main():
    #import pdb; pdb.set_trace()
    # Create the parser
    parser = argparse.ArgumentParser(description='Process some args.')

    # Add arguments
    parser.add_argument('--max_emails_read', type=int, default=500, help='An integer for max number of email read allowed.')
    parser.add_argument('--log_level', type=str, default="INFO", help='A string to print log level ')
    args = parser.parse_args()

    logger = SimpleLogger(name="GmailRuleLogger", log_file="application_log.log", level=args.log_level).get_logger()
    # Step 1: Authenticate with Gmail API
    authenticator = GmailAuthenticator(logger)
    service = authenticator.authenticate()

    # Step 2: Fetch Emails
    fetcher = EmailFetcher(logger, service)
    fetcher.fetch_emails(args.max_emails_read)

    # Step 3: Process Emails
    processor = RuleProcessor(logger, 'rules.json', service=service)
    processor.process_emails()

if __name__ == '__main__':
    main()
