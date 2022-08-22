# Deps for testing
import pytest
from freezegun import freeze_time

# Deps to test
from synapse.cli import (
    pair_emails,
    calculate_history_score,
    has_pair_in_pairs,
    filter_emails,
    convert_date_to_score,
)


def test_pair_emails():
    test_emails = [
        "ex1@a.bc",
        "ex2@a.bc",
        "ex3@a.bc",
        "ex4@a.bc",
        "ex5@a.bc",
        "ex6@a.bc",
        "ex7@a.bc",
        "ex8@a.bc",
        "ex9@a.bc",
    ]

    # Test basic example
    test_score, test_pairs = pair_emails(test_emails)
    assert test_score == 0
    assert len(test_pairs) == 4
    assert len(test_pairs[0]) == 2
    assert len(test_pairs[1]) == 2
    assert len(test_pairs[2]) == 2
    assert len(test_pairs[3]) == 3

    # Test not enough
    assert pair_emails([]) == (0, [])
    assert pair_emails(["a@b.com"]) == (0, [])

    # Test with history
    test_history = [
        {
            "score": 100,
            "pairs": [
                ["ex1@a.bc", "ex2@a.bc"],
                ["ex3@a.bc", "ex4@a.bc"],
            ],
        },
    ]
    test_score, test_pairs_with_history = pair_emails(test_emails, history=test_history)
    assert len(test_pairs_with_history) == 4


def test_calculate_history_score():
    test_history = [
        {
            "score": 100,
            "pairs": [
                ["ex1@a.bc", "ex2@a.bc"],
                ["ex3@a.bc", "ex4@a.bc"],
                ["ex5@a.bc", "ex6@a.bc"],
                ["ex7@a.bc", "ex8@a.bc"],
                [
                    "ex9@a.bc",
                    "ex10@a.bc",
                    "ex11@a.bc",
                ],
            ],
        },
        {
            "score": 50,
            "pairs": [
                ["ex5@a.bc", "ex1@a.bc"],
                ["ex6@a.bc", "ex2@a.bc"],
                ["ex7@a.bc", "ex3@a.bc"],
                ["ex8@a.bc", "ex4@a.bc"],
                ["ex9@a.bc", "ex5@a.bc"],
            ],
        },
    ]
    test_pairs = [
        ["ex1@a.bc", "ex3@a.bc"],
        ["ex2@a.bc", "ex4@a.bc"],
        ["ex11@a.bc", "ex9@a.bc"],
    ]
    test_pairs_2 = [
        ["ex1@a.bc", "ex3@a.bc"],
        ["ex7@a.bc", "ex3@a.bc"],
        ["ex9@a.bc", "ex11@a.bc"],
    ]
    test_pairs_3 = [
        ["ex1@a.bc", "ex3@a.bc"],
        ["ex2@a.bc", "ex4@a.bc"],
        ["ex3@a.bc", "ex5@a.bc"],
    ]
    test_pairs_4 = [
        ["ex1@a.bc", "ex3@a.bc"],
        ["ex2@a.bc", "ex4@a.bc"],
        ["ex3@a.bc", "ex5@a.bc"],
        # This one matches twice
        [
            "ex9@a.bc",
            "ex5@a.bc",
            "ex6@a.bc",
        ],
    ]

    assert calculate_history_score(test_pairs, test_history) == 100
    assert calculate_history_score(test_pairs_2, test_history) == 150
    assert calculate_history_score(test_pairs_3, test_history) == 0
    assert calculate_history_score(test_pairs_4, test_history) == 150


def test_has_pair_in_pairs():
    # Test basic ex
    test_pairs = [
        ["ex1@a.bc", "ex2@a.bc"],
        ["ex3@a.bc", "ex4@a.bc"],
        ["ex5@a.bc", "ex6@a.bc"],
        ["ex7@a.bc", "ex8@a.bc"],
        ["ex9@a.bc", "ex10@a.bc", "ex11@a.bc"],
    ]
    test_pair = ["ex5@a.bc", "ex6@a.bc"]
    test_no_match_pair = ["ex5@a.bc", "ex2@a.bc"]
    test_triple_pair = [
        "ex5@a.bc",
        "ex6@a.bc",
        "ex7@a.bc",
    ]
    test_pair_match_triple = ["ex9@a.bc", "ex11@a.bc"]

    assert has_pair_in_pairs(test_pair, test_pairs) == True
    assert has_pair_in_pairs(test_no_match_pair, test_pairs) == False
    assert has_pair_in_pairs(test_triple_pair, test_pairs) == True
    assert has_pair_in_pairs(test_pair_match_triple, test_pairs) == True


def test_filter_emails():
    test_emails = [
        "not-email",
        "",
        "a@example.com",
        "a@example.com",
        "a+34@example.com",
        "in@valid.net",
    ]

    assert filter_emails(test_emails) == ["a@example.com", "a+34@example.com"]


@freeze_time("2022-01-01T12:00:00")
def test_convert_date_to_score():

    # Basics
    assert convert_date_to_score("2021-12-01T01:01:01") == 300 - 31
    assert convert_date_to_score("2022-01-01T01:01:01") == 300 - 0
    assert convert_date_to_score("2019-12-01T01:01:01") == 1
