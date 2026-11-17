from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def _profile_text(profile):
    parts = [profile.interests, profile.course, profile.field_of_study]
    return " ".join(p for p in parts if p)


def _scholarship_text(s):
    parts = [s.title, s.description, s.field_of_study]
    return " ".join(p for p in parts if p)


def interest_scores(profile, scholarships):
    """One number per scholarship: how close its text is to the student's interests."""
    wanted = _profile_text(profile)
    if not wanted or not scholarships:
        return [0.0] * len(scholarships)
    texts = [_scholarship_text(s) for s in scholarships]
    try:
        matrix = TfidfVectorizer().fit_transform(texts + [wanted])
    except ValueError:
        return [0.0] * len(scholarships)
    return list(cosine_similarity(matrix[-1], matrix[:-1])[0])


def order_by_interest(profile, items):
    """items = [(scholarship, result), ...]. Same items, best interest match first."""
    scores = interest_scores(profile, [s for s, r in items])
    ranked = sorted(zip(scores, range(len(items))), key=lambda pair: (-pair[0], pair[1]))
    return [items[i] for score, i in ranked]
