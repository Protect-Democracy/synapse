# Dependencies
from os import getenv
from random import shuffle
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from dotenv import load_dotenv

# Load env variables from .env file
load_dotenv()


# History baseline for comparing pairs in number of days.  If a pair was
# not paired before this time, then it is assumed to be new.
HISTORY_BASELINE = 180


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
    emails = collect_emails(args.spreadsheet, args.sheet)

    # Make pairs
    pairs = pair_emails(emails)


def collect_emails(spreadsheet, sheet):
    """Collect emails from spreadsheet."""

    # Use environment variable if not provided
    if not spreadsheet:
        spreadsheet = getenv("SYNAPSE_SPREADSHEET")
    if not sheet:
        spreadsheet = getenv("SYNAPSE_SHEET", "0")

    return ["one@example.com", "two@example.com"]


def pair_emails(emails, history=None, sample_count=1000):
    """Randomly pair emails together"""

    # Don't do anything if only one or less emails
    if len(emails) < 2:
        return []

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

        # Add to samples
        samples.append((history_score, pairs))

    # Find lowest score
    samples.sort(key=lambda x: x[0])

    return samples[0][1]


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


# Run if script is executed directly
if __name__ == "__main__":
    main()
