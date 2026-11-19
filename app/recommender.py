"""Ordering of the scholarships the student is already eligible for.

This file never decides eligibility (that is eligibility.py). It only decides
the ORDER, in two parts:
  1. interest_scores / order_by_interest : TF-IDF + cosine similarity
  2. rank_eligible                       : TOPSIS over interest match + days left
"""
from datetime import date

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .topsis import topsis

# How much each criterion matters in TOPSIS (they add up to 1)
WEIGHTS = [0.6, 0.4]      # [interest match, days left]
BENEFIT = [True, False]   # a bigger interest match is better; FEWER days left is better


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

    0 means nothing in common, 1 means very similar. Never shown to the student.
    """
    wanted = _profile_text(profile)

    # Nothing to compare (no interests or no scholarships): every score is 0
    if not wanted or not scholarships:
        return [0.0] * len(scholarships)

    texts = [_scholarship_text(s) for s in scholarships]
    try:
        # TF-IDF turns every text into a list of numbers. Words that are rare
        # across the scholarships (like "research") count for more than common
        # ones. The student's text goes LAST so it is the final row.
        # We do not use stop_words="english": that list contains "it", which
        # would delete the field of study "IT".
        matrix = TfidfVectorizer().fit_transform(texts + [wanted])
    except ValueError:
        # Happens when the texts contain no usable words at all
        return [0.0] * len(scholarships)

    # Cosine similarity compares the last row (the student) with every other
    # row (the scholarships) and gives one score for each scholarship.
    return list(cosine_similarity(matrix[-1], matrix[:-1])[0])


def order_by_interest(profile, items):
    """Interest match only. items = [(scholarship, result), ...], best match first."""
    scores = interest_scores(profile, [s for s, r in items])
    # Sort by score (highest first). The original position breaks ties, so
    # results do not jump around.
    ranked = sorted(zip(scores, range(len(items))), key=lambda pair: (-pair[0], pair[1]))
    return [items[i] for score, i in ranked]


def _days_left(s, today):
    """Days until the deadline, or None if there is no deadline or it has passed."""
    if s.deadline is None:
        return None
    days = (s.deadline - today).days
    return days if days >= 0 else None


def rank_eligible(profile, items, today=None):
    """Order eligible scholarships with TOPSIS, using interest match and days left.

    items = [(scholarship, result), ...]. Returns the same pairs in a new order.
    """
    if len(items) < 2:
        return list(items)          # nothing to rank
    today = today or date.today()

    # Criterion 1: interest match (from TF-IDF + cosine similarity)
    interest = interest_scores(profile, [s for s, r in items])

    # Criterion 2: days left. A scholarship with no deadline (or a passed one)
    # is treated as less urgent than every dated one: 30 days beyond the furthest.
    days = [_days_left(s, today) for s, r in items]
    known = [d for d in days if d is not None]
    far = max(known) + 30 if known else 0
    days = [far if d is None else d for d in days]

    # One row per scholarship: [interest match, days left]
    rows = [[i, d] for i, d in zip(interest, days)]
    scores = topsis(rows, WEIGHTS, BENEFIT)

    # Highest TOPSIS score first; original position breaks ties
    ranked = sorted(zip(scores, range(len(items))), key=lambda pair: (-pair[0], pair[1]))
    return [items[i] for score, i in ranked]
