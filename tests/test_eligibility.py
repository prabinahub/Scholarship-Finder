from types import SimpleNamespace

from app.eligibility import check


def make_student(**changes):
    """A student profile. Pass keyword arguments to change any detail."""
    student = dict(degree_level="Bachelor", field_of_study="IT", gpa=3.6,
                   income=250000, nationality="Nepali", location="Bagmati")
    student.update(changes)
    return SimpleNamespace(**student)


def make_scholarship(**rules):
    """A scholarship. Any rule you do not pass is left empty (not checked)."""
    scholarship = dict(degree_level=None, field_of_study=None, min_gpa=None,
                       max_income=None, nationality=None, required_location=None)
    scholarship.update(rules)
    return SimpleNamespace(**scholarship)


def test_scholarship_with_no_rules_is_eligible():
    result = check(make_student(), make_scholarship())
    assert result["status"] == "eligible"
    assert result["met"] == [] and result["missing"] == []


def test_all_rules_met_is_eligible():
    s = make_scholarship(degree_level="Bachelor", field_of_study="Management, IT",
                         min_gpa=3.4, nationality="Nepali")
    result = check(make_student(), s)
    assert result["status"] == "eligible"
    assert len(result["met"]) == 4
    assert result["missing"] == []


def test_one_missing_requirement_is_close_match():
    result = check(make_student(), make_scholarship(degree_level="Bachelor", min_gpa=3.9))
    assert result["status"] == "close"
    assert result["missing"] == ["Minimum GPA 3.9 required (yours is 3.6)"]


def test_two_missing_requirements_is_still_close_match():
    s = make_scholarship(degree_level="Bachelor", min_gpa=3.9, field_of_study="Medicine")
    result = check(make_student(), s)
    assert result["status"] == "close"
    assert len(result["missing"]) == 2


def test_three_missing_requirements_is_not_eligible():
    s = make_scholarship(degree_level="Master, PhD", min_gpa=3.9, field_of_study="Medicine")
    result = check(make_student(), s)
    assert result["status"] == "not"
    assert len(result["missing"]) == 3


def test_gpa_equal_to_the_minimum_passes():
    assert check(make_student(gpa=3.6), make_scholarship(min_gpa=3.6))["status"] == "eligible"


def test_income_equal_to_the_limit_passes():
    assert check(make_student(income=250000), make_scholarship(max_income=250000))["status"] == "eligible"


def test_income_above_the_limit_fails():
    result = check(make_student(income=300000), make_scholarship(max_income=250000))
    assert result["status"] == "close"
    assert "NPR 250,000" in result["missing"][0]


def test_region_rule():
    result = check(make_student(location="Bagmati"), make_scholarship(required_location="Karnali"))
    assert result["missing"] == ["Open to students from Karnali"]


def test_any_one_listed_degree_level_is_enough():
    s = make_scholarship(degree_level="+2, Bachelor")
    assert check(make_student(degree_level="Bachelor"), s)["status"] == "eligible"
    assert check(make_student(degree_level="PhD"), s)["status"] == "close"


def test_capital_letters_and_extra_spaces_are_ignored():
    s = make_scholarship(degree_level="  bachelor ,MASTER ", field_of_study=" it ",
                         nationality="nepali", required_location="BAGMATI")
    assert check(make_student(), s)["status"] == "eligible"


def test_empty_profile_details_are_reported_not_crashed():
    student = make_student(gpa=None, income=None, nationality=None, location=None)
    s = make_scholarship(min_gpa=3.0, max_income=100000, nationality="Nepali",
                         required_location="Karnali")
    result = check(student, s)
    assert result["status"] == "not"
    assert len(result["missing"]) == 4
    assert "add your GPA" in result["missing"][0]
    