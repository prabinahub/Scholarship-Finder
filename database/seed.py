"""Adds SAMPLE scholarships to the database so the dashboard has data.

Run from the project folder:   python database/seed.py
These are made-up examples for testing. Real data will come from the admin
panel and the scrapers.
"""
import os
import sys
from datetime import date

# let this script find the "app" package in the project folder above it
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import Scholarship

SAMPLES = [
    dict(title="Merit Scholarship (sample)",
         provider="Sample College of Management", location="Lalitpur",
         description="Awarded to students with outstanding results in their previous level.",
         amount="50% tuition waiver", deadline=date(2027, 1, 31),
         degree_level="Bachelor", field_of_study="Management, IT",
         min_gpa=3.4, nationality="Nepali"),

    dict(title="Need-Based Support (sample)",
         provider="Sample Education Trust", location="Kathmandu",
         description="Fee support for capable students from low-income families.",
         amount="NPR 40,000 per year", deadline=date(2026, 12, 20),
         degree_level="+2, Bachelor", field_of_study="",
         max_income=300000, nationality="Nepali"),

    dict(title="Research Fellowship (sample)",
         provider="Sample University", location="Bhaktapur",
         description="Fellowship for research in artificial intelligence and data science.",
         amount="NPR 20,000 monthly",
         degree_level="Master, PhD", field_of_study="IT, Science",
         min_gpa=3.6),

    dict(title="IT Excellence Award (sample)",
         provider="Sample Technical College", location="Kathmandu",
         description="For students of information technology and software engineering.",
         amount="NPR 60,000", deadline=date(2027, 2, 15),
         degree_level="Bachelor", field_of_study="IT",
         min_gpa=3.0),

    dict(title="Science and Technology Scholarship (sample)",
         provider="Sample University", location="Bhaktapur",
         description="Encourages students in science, technology and engineering.",
         amount="NPR 100,000", deadline=date(2027, 3, 1),
         degree_level="Bachelor, Master", field_of_study="Science, Engineering, IT",
         min_gpa=3.0, nationality="Nepali"),

    dict(title="Health Sciences Merit Award (sample)",
         provider="Sample Health Sciences Institute", location="Pokhara",
         description="Supports talented students in medicine and nursing.",
         amount="Full tuition", deadline=date(2027, 1, 10),
         degree_level="Bachelor", field_of_study="Medicine",
         min_gpa=3.5, max_income=500000),

    dict(title="Karnali Regional Scholarship (sample)",
         provider="Sample Provincial Fund", location="Surkhet",
         description="Open to students from the Karnali region continuing higher education.",
         amount="NPR 60,000", deadline=date(2027, 2, 28),
         degree_level="+2, Bachelor", field_of_study="",
         required_location="Karnali", nationality="Nepali"),
]


def main():
    app = create_app()
    with app.app_context():
        if Scholarship.query.count() > 0:
            print("The scholarship table already has data. Nothing added.")
            return

        for item in SAMPLES:
            db.session.add(Scholarship(status="verified",
                                       official_url="https://example.com", **item))

        # one pending record, so you can test the admin approval screen later
        db.session.add(Scholarship(title="Scraped Example (needs review)",
                                   provider="Sample Source", status="pending",
                                   source_url="https://example.com/source"))
        db.session.commit()
        print(f"{len(SAMPLES)} verified scholarships and 1 pending scholarship added.")


if __name__ == "__main__":
    main()
    