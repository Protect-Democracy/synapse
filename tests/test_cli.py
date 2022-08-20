# To test
from synapse.cli import pair_emails, calculate_history_score, has_pair_in_pairs


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
