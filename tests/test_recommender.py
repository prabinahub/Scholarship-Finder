from datetime import date
from types import SimpleNamespace

from app.recommender import order_by_interest, rank_eligible


def make_student(**changes):
    student = dict(interests="research, science", course="", field_of_study="")
    student.update(changes)
    return SimpleNamespace(**student)


def make_scholarship(title, description="", field_of_study=""):
    return SimpleNamespace(title=title, description=description, field_of_study=field_of_study)


def titles(items):
    return [s.title for s, result in items]


def make_items():
    """(scholarship, result) pairs, like the dashboard builds them."""
    return [
        (make_scholarship("Need-Based Support", "Fee support for low-income families"), "r1"),
        (make_scholarship("Research Grant", "Funding for science research projects"), "r2"),
        (make_scholarship("Sports Award", "For national level athletes"), "r3"),
    ]


def test_scholarship_matching_the_interests_comes_first():
    assert titles(order_by_interest(make_student(), make_items()))[0] == "Research Grant"


def test_no_interests_keeps_the_original_order():
    items = make_items()
    assert order_by_interest(make_student(interests=""), items) == items


def test_ties_keep_the_original_order():
    items = [(make_scholarship("First"), 1), (make_scholarship("Second"), 2)]
    assert titles(order_by_interest(make_student(), items)) == ["First", "Second"]


def test_empty_list_is_fine():
    assert order_by_interest(make_student(), []) == []


def test_nothing_is_lost_or_changed():
    items = make_items()
    ordered = order_by_interest(make_student(), items)
    assert len(ordered) == 3
    assert sorted(titles(ordered)) == sorted(titles(items))
    assert {result for s, result in ordered} == {"r1", "r2", "r3"}


def test_the_word_it_is_not_thrown_away():
    student = make_student(interests="", field_of_study="IT")
    items = [
        (make_scholarship("Sports Award", "For athletes"), 1),
        (make_scholarship("IT Excellence Award", "For software students", "IT"), 2),
    ]
    assert titles(order_by_interest(student, items))[0] == "IT Excellence Award"



# ---- TOPSIS ranking (interest + deadline) ----

TODAY = date(2026, 11, 18)


def dated(title, deadline=None, description=""):
    return SimpleNamespace(title=title, description=description,
                           field_of_study="", deadline=deadline)


def test_sooner_deadline_first_when_interest_is_equal():
    items = [(dated("Later", date(2027, 3, 1)), 1), (dated("Sooner", date(2026, 12, 1)), 2)]
    ranked = rank_eligible(make_student(interests=""), items, today=TODAY)
    assert titles(ranked) == ["Sooner", "Later"]


def test_better_interest_match_first_when_deadlines_are_equal():
    same_day = date(2027, 1, 1)
    items = [(dated("Sports", same_day, "athletes and games"), 1),
             (dated("Research", same_day, "science research projects"), 2)]
    ranked = rank_eligible(make_student(), items, today=TODAY)
    assert titles(ranked)[0] == "Research"


def test_no_deadline_ranks_after_dated_scholarships_when_interest_is_equal():
    items = [(dated("No deadline"), 1), (dated("Dated", date(2027, 1, 1)), 2)]
    ranked = rank_eligible(make_student(interests=""), items, today=TODAY)
    assert titles(ranked) == ["Dated", "No deadline"]


def test_a_passed_deadline_is_not_treated_as_urgent():
    items = [(dated("Expired", date(2026, 10, 1)), 1), (dated("Open", date(2027, 1, 1)), 2)]
    ranked = rank_eligible(make_student(interests=""), items, today=TODAY)
    assert titles(ranked) == ["Open", "Expired"]


def test_zero_or_one_scholarship_is_returned_unchanged():
    assert rank_eligible(make_student(), [], today=TODAY) == []
    one = [(dated("Only"), 1)]
    assert rank_eligible(make_student(), one, today=TODAY) == one


def test_ranking_loses_nothing():
    items = [(dated(f"S{n}", date(2027, 1, n + 1)), n) for n in range(5)]
    ranked = rank_eligible(make_student(), items, today=TODAY)
    assert sorted(result for s, result in ranked) == [0, 1, 2, 3, 4]
    
    