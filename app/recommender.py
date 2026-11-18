"""Interest ordering with TF-IDF and cosine similarity.

This file only decides the ORDER of scholarships the student is already
eligible for. It never decides eligibility (that is eligibility.py).
"""
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def _profile_text(profile):
    """Join what the student told us about their interests into one piece of text."""
    parts = [profile.interests, profile.course, profile.field_of_study]
    # "if p" skips empty fields (None or "") so we never join the word "None"
    return " ".join(p for p in parts if p)


def _scholarship_text(s):
    """Join the words that describe a scholarship into one piece of text."""
    parts = [s.title, s.description, s.field_of_study]
    return " ".join(p for p in parts if p)


def interest_scores(profile, scholarships):
    """Give every scholarship a number: how similar it is to the student's interests.

    0 means nothing in common, 1 means very similar. The number is only used
    for sorting. The student never sees it.
    """
    wanted = _profile_text(profile)

    # Nothing to compare (no interests or no scholarships): every score is 0
    if not wanted or not scholarships:
        return [0.0] * len(scholarships)

    texts = [_scholarship_text(s) for s in scholarships]
    try:
        # TF-IDF turns every text into a list of numbers. Words that are rare
        # across the scholarships (like "research") count for more than common
        # words. The student's text goes LAST so it is the final row.
        # We do not use stop_words="english": that list contains "it", which
        # would delete the field of study "IT".
        matrix = TfidfVectorizer().fit_transform(texts + [wanted])
    except ValueError:
        # Happens when the texts contain no usable words at all
        return [0.0] * len(scholarships)

    # Cosine similarity compares the last row (the student) with every other row
    # (the scholarships) and gives one score for each scholarship.
    return list(cosine_similarity(matrix[-1], matrix[:-1])[0])


def order_by_interest(profile, items):
    """Put the best interest match first.

    items is a list of (scholarship, result) pairs, as built by the dashboard.
    We return the same pairs in a new order. Nothing is removed or changed.
    """
    scores = interest_scores(profile, [s for s, r in items])

    # Pair each score with the item's original position, then sort by score
    # (highest first). When two scores are equal, the original position keeps
    # the old order, so results do not jump around.
    ranked = sorted(zip(scores, range(len(items))), key=lambda pair: (-pair[0], pair[1]))
    return [items[i] for score, i in ranked]