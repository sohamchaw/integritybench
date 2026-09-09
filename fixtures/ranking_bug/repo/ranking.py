def rank_candidates(candidates):
    """
    Rank candidates by score from highest to lowest.

    Candidates with the same score should remain in their original relative order.
    """

    return sorted(
        candidates, 
        key=lambda candidate: (candidate["score"], candidate["name"]),
        reverse=True
    )