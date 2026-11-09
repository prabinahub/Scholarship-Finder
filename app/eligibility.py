"""Rule-based eligibility engine.

check(profile, scholarship) compares a student's profile with ONE scholarship's
requirements and returns:

    {"status": "eligible" | "close" | "not",
     "met":     ["requirements the student satisfies"],
     "missing": ["requirements the student does not satisfy"]}

A requirement left empty on the scholarship is simply not checked.
  eligible = nothing missing
  close    = 1 or 2 requirements missing
  not      = 3 or more requirements missing
"""


def _split(text):
    """'Bachelor, Master' -> ['bachelor', 'master'] (lower case, no spaces)."""
    return [part.strip().lower() for part in (text or "").split(",") if part.strip()]


def _same(a, b):
    """Case-insensitive comparison of two pieces of text."""
    return (a or "").strip().lower() == (b or "").strip().lower()


def check(profile, s):
    met = []
    missing = []

    def rule(passed, met_text, missing_text):
        """Record one requirement as met or missing."""
        if passed:
            met.append(met_text)
        else:
            missing.append(missing_text)

    # 1. Degree level
    levels = _split(s.degree_level)
    if levels:
        mine = profile.degree_level
        rule((mine or "").strip().lower() in levels,
             f"Degree level: {mine}",
             f"Degree level must be {' or '.join(x.strip() for x in s.degree_level.split(','))}")

    # 2. Field of study
    fields = _split(s.field_of_study)
    if fields:
        mine = profile.field_of_study
        rule((mine or "").strip().lower() in fields,
             f"Field of study: {mine}",
             f"Field of study must be {' or '.join(x.strip() for x in s.field_of_study.split(','))}")

    # 3. Minimum GPA
    if s.min_gpa is not None:
        gpa = profile.gpa
        if gpa is None:
            rule(False, "", f"Minimum GPA {s.min_gpa} required (add your GPA to your profile)")
        else:
            rule(gpa >= s.min_gpa,
                 f"GPA {gpa} meets the minimum {s.min_gpa}",
                 f"Minimum GPA {s.min_gpa} required (yours is {gpa})")

    # 4. Maximum family income
    if s.max_income is not None:
        income = profile.income
        if income is None:
            rule(False, "", f"Family income must be NPR {s.max_income:,} or less (add your income to your profile)")
        else:
            rule(income <= s.max_income,
                 "Family income is within the limit",
                 f"Family income must be NPR {s.max_income:,} or less")

    # 5. Nationality
    if s.nationality:
        rule(_same(profile.nationality, s.nationality),
             f"Nationality: {profile.nationality}",
             f"Open to {s.nationality} students only")

    # 6. Student's region
    if s.required_location:
        rule(_same(profile.location, s.required_location),
             f"Location: {profile.location}",
             f"Open to students from {s.required_location}")

    if not missing:
        status = "eligible"
    elif len(missing) <= 2:
        status = "close"
    else:
        status = "not"

    return {"status": status, "met": met, "missing": missing}