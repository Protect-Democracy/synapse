# Dependencies
import sys
import json
import re
import random
from time import sleep
from urllib.parse import urlencode
from os import getenv, path
from random import shuffle
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from dotenv import load_dotenv
from datetime import datetime
import gspread
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Load env variables from .env file
load_dotenv()


# History baseline for comparing pairs in number of days.  If a pair was
# not paired before this time, then it is assumed to be new.
HISTORY_SCORE_MAXIMUM = 300
HISTORY_SHEET_NAME = "Sent history (DO NOT EDIT)"
TIME_TO_WAIT_BETWEEN_EMAILS = 15
EMAIL_MATCH_PERMUTATIONS = 10000


# Potential subjects to use
POTENTIAL_SUBJECTS = [
    "You've been paired for a 1:1! ☕️ Time to schedule. 📆",
    "1:1 time for [[[NAMES]]]! ☕️",
    "[[[NAMES]]] you've been selected to catch up! 🍩",
    "Schedule your 1:1, [[[NAMES]]]! 📆",
    "What luck! [[[NAMES]]] have been paired for a 1:1! 🧋",
]


# Values to define as needed
global_gpread_client = None
global_google_auth_token = None
global_mail_handler = None
global_quiet_output = False


def main():
    """Main function to handle CLI."""

    # CLI setup and arguments
    parser = ArgumentParser(
        description="Reads emails from spreadsheet, matches them, and then sends emails.",
        formatter_class=ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "--no-send",
        action="store_true",
        help="Just read and match, but do not send emails.",
    )
    parser.add_argument(
        "--send",
        action="store_true",
        help="Do not require a user confirmation to send emails.",
    )
    parser.add_argument(
        "--spreadsheet",
        type=str,
        help="Google Spreadsheet ID to parse; will also use SYNAPSE_SPREADSHEET if not provided.",
    )
    parser.add_argument(
        "--sheet",
        type=str,
        help="Google Spreadsheet Sheet ID; will also use SYNAPSE_SHEET if not provided.  Will use 0 if not provided in either place.",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Minimize output.",
    )

    # Parse arguments
    args = parser.parse_args()

    # Define output
    global global_quiet_output
    global_quiet_output = args.quiet

    # Use env variables if not provided
    spreadsheet = args.spreadsheet or getenv("SYNAPSE_SPREADSHEET")
    sheet = args.sheet or getenv("SYNAPSE_SHEET", "0")

    # Get list of emails from spreadsheet
    eprint("  💾 Loading emails...")
    emails = collect_emails(spreadsheet, sheet)

    # Reading history from spreadsheet
    history = read_history()

    # Make pairs
    score, pairs = pair_emails(emails, history=history)

    # No send
    if args.no_send:
        eprint(
            f"\n⛔️ Not sending {len(emails)} emails in {len(pairs)} pairs with a repetition score of {score} (lower is better, 0 is not repetition)."
        )
        return

    # Prompt user for sending emails
    if not args.send:
        eprint(
            f"  📧 Will send {len(emails)} emails in {len(pairs)} pairs with a repetition score of {score} (lower is better, 0 is not repetition)."
        )
        for pair in pairs:
            eprint(f"     - {', '.join(pair)}")

        email_confirmation = input("     Send emails? (y/n): ")
        if re.match(r"(y|Y|yes|YES)", email_confirmation) is None:
            eprint("\nExiting.")
            return

    # Send emails
    eprint(f"  📧 Sending {len(pairs)} emails...")
    send_emails(pairs, spreadsheet, sheet)

    # Close mail handler
    mail_handler = get_mail_handler()
    if mail_handler is not None:
        mail_handler.quit()

    # Save history
    eprint("  💾 Saving history...")
    save_history(pairs)


def send_emails(pairs, spreadsheet, sheet):
    """
    Send all emails

    :param pairs: List of pairs to send emails for.
    :param spreadsheet: ID of the spreadsheet, defaults to env var SYNAPSE_SPREADSHEET.
    :param sheet: ID of the sheet, defaults to env var SYNAPSE_SHEET and 0 if neither
    """

    # Templates
    dirname = path.dirname(__file__)
    email_template_html_filename = path.join(
        dirname, "templates", "email_template.html"
    )
    with open(email_template_html_filename, "r") as email_template_html:
        email_template_txt_filename = path.join(
            dirname, "templates", "email_template.txt"
        )
        with open(email_template_txt_filename, "r") as email_template_txt:

            # Read files
            email_template_txt_contents = email_template_txt.read()
            email_template_html_contents = email_template_html.read()

            # Go through each pair and send emails
            for pair in pairs:
                emails = ",".join(pair)
                names = [email.split(".")[0].capitalize() for email in pair]
                html_names = [f"<strong>{name}</strong>" for name in names]
                names_joined = join_names(names)
                html_names_joined = join_names(html_names)

                # Subject
                subject = random.choice(POTENTIAL_SUBJECTS).replace(
                    "[[[NAMES]]]", names_joined
                )

                # Spreadsheet URL
                spreadsheet_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet}/edit#gid={sheet}"

                # Schedule URL
                schedule_query = urlencode(
                    {
                        "action": "TEMPLATE",
                        "text": f"1:1 - {', '.join(names)}",
                        "add": emails,
                        "details": f"This 1:1 was randomly paired by an automated system.  If you don't want to receive these pairings anymore, manage your email at this spreadsheet: {spreadsheet_url}",
                    }
                )
                schedule_url = (
                    f"https://calendar.google.com/calendar/render?{schedule_query}"
                )

                # Text template
                body_text = (
                    email_template_txt_contents.replace("[[[NAMES]]]", names_joined)
                    .replace("[[[SCHEDULE_URL]]]", schedule_url)
                    .replace("[[[SPREADSHEET_URL]]]", spreadsheet_url)
                )

                # Email template
                body_html = (
                    email_template_html_contents.replace(
                        "[[[NAMES]]]", html_names_joined
                    )
                    .replace("[[[SCHEDULE_URL]]]", schedule_url)
                    .replace("[[[SPREADSHEET_URL]]]", spreadsheet_url)
                )

                # Send email
                send_email(emails, None, subject, body_html, body_text)


def send_email(to, from_, subject, body_html, body_text):
    """
    Send a multipart email
    Inspiration: https://stackoverflow.com/questions/882712/send-html-emails-with-python

    :param to: Email address to send to in the form of a string of emails separated by
        commas.  Ex: a@example.com, b@example.com
    :param from_: Email address to send from.  If not provided, will use the default
        email address that is sending the emails.
    :param subject: Subject of the email.
    :param body_html: HTML body of the email.
    :param body_text: Text body of the email.
    """
    from_ = from_ if from_ is not None else getenv("SYNAPSE_GMAIL_USERNAME")

    # Create message container - the correct MIME type is multipart/alternative.
    msg = MIMEMultipart("alternative")
    msg.set_charset("UTF-8")
    msg["Subject"] = subject
    msg["From"] = from_
    msg["To"] = to
    msg["reply-to"] = to

    # Create the body of the message (a plain-text and an HTML version).
    text = body_text
    html = body_html

    # Record the MIME types of both parts - text/plain and text/html.
    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")

    # Attach parts into message container.
    # According to RFC 2046, the last part of a multipart message, in this case
    # the HTML message, is best and preferred.
    msg.attach(part1)
    msg.attach(part2)

    # Send the message via local SMTP server.
    mail_handler = get_mail_handler()
    mail_handler.sendmail(from_, msg["To"].split(","), msg.as_string())

    # Make sure we don't do too many too quickly
    sleep(TIME_TO_WAIT_BETWEEN_EMAILS)


def collect_emails(spreadsheet, sheet):
    """
    Collect emails from spreadsheet.

    :param spreadsheet: ID of the spreadsheet, defaults to env var SYNAPSE_SPREADSHEET.
    :param sheet: ID of the sheet, defaults to env var SYNAPSE_SHEET and 0 if neither
        is provided.
    """

    # Use environment variable if not provided
    if not spreadsheet:
        spreadsheet = getenv("SYNAPSE_SPREADSHEET")
    if not sheet:
        sheet = getenv("SYNAPSE_SHEET", "0")

    # Check values
    if not spreadsheet:
        raise Exception(
            "Spreadsheet not provided via CLI argument or SYNAPSE_SPREADSHEET environment variable."
        )

    # Connect to spreadsheet
    gspread_client = get_gpread_client()
    spreadsheet = gspread_client.open_by_key(spreadsheet)
    sheet = spreadsheet.get_worksheet(int(sheet))

    # Get all values from first column
    column_values = sheet.col_values(1)

    return filter_emails(column_values)


def filter_emails(emails, filter_regex=None):
    """
    Filter emails to remove invalid emails and duplicates.

    :param emails: List of emails to filter.
    :param filter_regex: Regex to filter emails by.  Defaults to env
        var SYNAPSE_VALID_EMAIL_REGEX.
    """

    # Valid emails
    valid_email_regex_string = (
        filter_regex if filter_regex else getenv("SYNAPSE_VALID_EMAIL_REGEX")
    )
    if not valid_email_regex_string:
        raise Exception(
            "Please provide a SYNAPSE_VALID_EMAIL_REGEX value such as '@example\\.com$'"
        )
    valid_email_regex = re.compile(valid_email_regex_string, re.IGNORECASE)
    emails = [v for v in emails if re.search(valid_email_regex, v)]

    # Remove any duplicates
    emails = unique(emails)

    return emails


def pair_emails(emails, history=None, sample_count=None):
    """
    Randomly pair emails together

    :param emails: List of emails to pair.
    :param history: List of previous pairings to avoid.
    :param sample_count: Number of pair permutations to make to try to
        find the most optimal; if not provided uses EMAIL_MATCH_PERMUTATIONS
        constant.
    """

    # Don't do anything if only one or less emails
    if len(emails) < 2:
        return (0, [])

    # Sample count
    sample_count = (
        sample_count if sample_count is not None else EMAIL_MATCH_PERMUTATIONS
    )

    # Make samples of pairs to try to avoid matching people up with
    # the sample people recently
    samples = []
    for s in range(sample_count):
        # Shuffle emails to be able to pair
        shuffled = emails.copy()
        shuffle(shuffled)

        # Place to store pairs
        pairs = []

        # Create pairs
        while len(shuffled) > 0:
            # Add two
            pair = [shuffled.pop(), shuffled.pop()]

            # If there is only one left, add it to the last pair
            if len(shuffled) == 1:
                pair.append(shuffled.pop())

            pairs.append(pair)

        # Determine history score and add to sample
        history_score = calculate_history_score(pairs, history)
        samples.append((history_score, pairs))

    # Find lowest score
    samples.sort(key=lambda x: x[0])

    return (samples[0][0], samples[0][1])


def read_history():
    """Read history from spreadsheet"""

    # Get history spreadsheet
    gspread_client = get_gpread_client()
    history_spreadsheet = gspread_client.open_by_key(getenv("SYNAPSE_SPREADSHEET"))

    # Get history if sheet exists
    history_sheet = None
    try:
        history_sheet = history_spreadsheet.worksheet(HISTORY_SHEET_NAME)
    except gspread.exceptions.WorksheetNotFound:
        return None

    # Get all values
    values = history_sheet.get_all_records()

    # Transform
    transformed = []
    for v in values:
        try:
            transformed.append(
                {
                    "score": convert_date_to_score(v["Date"]),
                    "pairs": json.loads(v["Email pairs"]),
                }
            )
        except json.decoder.JSONDecodeError:
            pass

    return transformed


def convert_date_to_score(input):
    """Convert iso string to score"""

    # Convert to datetime
    input_datetime = datetime.fromisoformat(input)

    # Calculate score
    score = HISTORY_SCORE_MAXIMUM - (datetime.now() - input_datetime).days

    # If after maximum, set to 1 to help push pairing with
    # someone that is a 0, but ok to re-pair
    if score < 0:
        score = 1

    return score


def save_history(pairs):
    """Save pairing to history spreadsheet."""

    # Get history spreadsheet
    gspread_client = get_gpread_client()
    history_spreadsheet = gspread_client.open_by_key(getenv("SYNAPSE_SPREADSHEET"))

    # Get history sheet, make one if not found
    try:
        history_sheet = history_spreadsheet.worksheet(HISTORY_SHEET_NAME)
    except gspread.exceptions.WorksheetNotFound:
        history_sheet = history_spreadsheet.add_worksheet(
            title=HISTORY_SHEET_NAME,
            rows=1000,
            cols=3,
        )

        # Add headers
        history_sheet.append_row(["Date", "Email pairs"])

        # Some niceties: Format first row
        history_sheet.format(
            "A1:C1",
            {
                "backgroundColor": {"red": 50, "green": 50, "blue": 50},
                "textFormat": {"bold": True},
            },
        )
        history_sheet.freeze(rows=1)

    # Add new history
    history_sheet.append_row([datetime.now().isoformat(), json.dumps(pairs)])


def calculate_history_score(pairs, history):
    """Calculate history score for pairs.  Score is based on number of days since last pair."""

    if not history or len(history) == 0:
        return 0

    # Go through each pair and determine if found in each history
    # and assign score base on how long ago it was.
    total_score = 0
    for pair in pairs:
        for sent in history:
            if has_pair_in_pairs(pair, sent["pairs"]):
                total_score += sent["score"]

    return total_score


def has_pair_in_pairs(pair, pairs):
    """Find pair in pairs, where a pair could be a list of two or more emails."""

    for p in pairs:
        common_found = 0
        for email in pair:
            if email in p:
                common_found += 1

        if common_found >= 2:
            return True

    return False


def get_gpread_client():
    """Get Google Spreadsheet client."""
    global global_gpread_client

    if global_gpread_client is None:
        google_auth_token = get_google_auth_token()
        global_gpread_client = gspread.service_account_from_dict(google_auth_token)

    return global_gpread_client


def get_google_auth_token():
    global global_google_auth_token

    # Check Google credentials if spreadsheet option is provided
    if global_google_auth_token is None:
        json_token = getenv("SYNAPSE_GOOGLE_SERVICE_ACCOUNT", None)
        if json_token is None:
            raise Exception(
                "Google Service Account not found. Please set SYNAPSE_GOOGLE_SERVICE_ACCOUNT environment variable."
            )
        else:
            try:
                global_google_auth_token = json.loads(json_token)
            except json.decoder.JSONDecodeError:
                raise Exception(
                    "Google Service Account not parsable. Please set SYNAPSE_GOOGLE_SERVICE_ACCOUNT environment variable as escaped JSON."
                )

    return global_google_auth_token


def get_mail_handler():
    """Create mail handler if needed"""
    global global_mail_handler

    if global_mail_handler is None:
        global_mail_handler = smtplib.SMTP("smtp.gmail.com", 587)
        global_mail_handler.ehlo()
        global_mail_handler.starttls()
        global_mail_handler.login(
            getenv("SYNAPSE_GMAIL_USERNAME"), getenv("SYNAPSE_GMAIL_APP_PASSWORD")
        )

    return global_mail_handler


def join_names(names):
    """Join names with commas and 'and'"""

    if len(names) == 1:
        return names[0]
    elif len(names) == 2:
        return f"{names[0]} and {names[1]}"
    else:
        return f"{', '.join(names[:-1])}, and {names[-1]}"


def unique(sequence):
    """Unique list preserving order"""
    seen = set()
    return [x for x in sequence if not (x in seen or seen.add(x))]


def eprint(*args, **kwargs):
    """Print to stderr"""
    global global_quiet_output

    if not global_quiet_output:
        print(*args, file=sys.stderr, **kwargs)


# Run if script is executed directly
if __name__ == "__main__":
    main()
