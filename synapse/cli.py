# Dependencies
import sys
import json
import re
from os import getenv
from random import shuffle
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from dotenv import load_dotenv
from datetime import datetime
import gspread

# Load env variables from .env file
load_dotenv()


# History baseline for comparing pairs in number of days.  If a pair was
# not paired before this time, then it is assumed to be new.
HISTORY_SCORE_MAXIMUM = 300
VALID_EMAIL_REGEX = r"@(protectdemocracy\.org|voteshield\.us|example\.com)$"
HISTORY_SHEET_NAME = "Sent history (DO NOT EDIT)"


# Values to define as needed
global_gpread_client = None
global_google_auth_token = None


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

    # Parse arguments
    args = parser.parse_args()

    # Get list of emails from spreadsheet
    eprint("Loading emails...")
    emails = collect_emails(args.spreadsheet, args.sheet)

    # Reading history from spreadsheet
    history = read_history()

    # Make pairs
    score, pairs = pair_emails(emails, history=history)

    # Prompt user for sending emails
    eprint(
        f"Will send {len(emails)} emails in {len(pairs)} pairs with a repetition score of {score} (lower is better)."
    )
    email_confirmation = input("Send emails? (y/n): ")
    if re.match(r"(y|Y|yes|YES)", email_confirmation) is None:
        eprint("Exiting.")
        return

    # Send emails
    # TODO

    # Save history
    eprint("Saving history...")
    save_history(pairs)


def collect_emails(spreadsheet, sheet):
    """Collect emails from spreadsheet."""

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


def filter_emails(emails):
    """Filter emails to remove invalid emails and duplicates."""

    # Valid emails
    emails = [v for v in emails if re.search(VALID_EMAIL_REGEX, v)]

    # Remove any duplicates
    emails = unique(emails)

    return emails


def pair_emails(emails, history=None, sample_count=1000):
    """Randomly pair emails together"""

    # Don't do anything if only one or less emails
    if len(emails) < 2:
        return (0, [])

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


def unique(sequence):
    """Unique list preserving order"""
    seen = set()
    return [x for x in sequence if not (x in seen or seen.add(x))]


def eprint(*args, **kwargs):
    """Print to stderr"""
    print(*args, file=sys.stderr, **kwargs)


# Run if script is executed directly
if __name__ == "__main__":
    main()
