from ranking import rank_candidates


def test_higher_scores_rank_first():
    candidates = [
        {"name": "Alice", "score": 82},
        {"name": "Bob", "score": 95},
        {"name": "Charlie", "score": 88},
    ]

    result = rank_candidates(candidates)

    assert [candidate["name"] for candidate in result] == [
        "Bob",
        "Charlie",
        "Alice",
    ]


def test_equal_scores_preserve_original_order():
    candidates = [
        {"name": "Alice", "score": 90},
        {"name": "Bob", "score": 90},
        {"name": "Charlie", "score": 90},
    ]

    result = rank_candidates(candidates)

    assert [candidate["name"] for candidate in result] == [
        "Alice",
        "Bob",
        "Charlie",
    ]


def test_mixed_scores_preserve_order_within_ties():
    candidates = [
        {"name": "Alice", "score": 95},
        {"name": "Bob", "score": 88},
        {"name": "Charlie", "score": 88},
        {"name": "Diana", "score": 80},
    ]

    result = rank_candidates(candidates)

    assert [candidate["name"] for candidate in result] == [
        "Alice",
        "Bob",
        "Charlie",
        "Diana",
    ]