"""TEMPORARY sample scholarships so the dashboard has something to show.
We will delete this file when scholarships come from the database."""
from datetime import date

SCHOLARSHIPS = [
    {"title": "Merit Scholarship (sample)",
     "provider": "Sample College of Management", "location": "Lalitpur",
     "description": "Awarded to students with outstanding results in their previous level.",
     "degree_level": "Bachelor", "field_of_study": "Management, IT",
     "amount": "50% tuition waiver", "deadline": date(2027, 1, 31),
     "official_url": "https://example.com"},

    {"title": "Need-Based Support (sample)",
     "provider": "Sample Education Trust", "location": "Kathmandu",
     "description": "Fee support for capable students from low-income families.",
     "degree_level": "+2, Bachelor", "field_of_study": "",
     "amount": "NPR 40,000 per year", "deadline": date(2026, 12, 20),
     "official_url": "https://example.com"},

    {"title": "Research Fellowship (sample)",
     "provider": "Sample University", "location": "Bhaktapur",
     "description": "Fellowship for research in artificial intelligence and data science.",
     "degree_level": "Master, PhD", "field_of_study": "IT, Science",
     "amount": "NPR 20,000 monthly", "deadline": None,
     "official_url": "https://example.com"},

    {"title": "IT Excellence Award (sample)",
     "provider": "Sample Technical College", "location": "Kathmandu",
     "description": "For students of information technology and software engineering.",
     "degree_level": "Bachelor", "field_of_study": "IT",
     "amount": "NPR 60,000", "deadline": date(2027, 2, 15),
     "official_url": "https://example.com"},

    {"title": "Women in Science Scholarship (sample)",
     "provider": "Sample University", "location": "Bhaktapur",
     "description": "Encourages women in science, technology and engineering.",
     "degree_level": "Bachelor, Master", "field_of_study": "Science, Engineering, IT",
     "amount": "NPR 100,000", "deadline": date(2027, 3, 1),
     "official_url": "https://example.com"},

    {"title": "Health Sciences Merit Award (sample)",
     "provider": "Sample Health Sciences Institute", "location": "Pokhara",
     "description": "Supports talented students in medicine and nursing.",
     "degree_level": "Bachelor", "field_of_study": "Medicine",
     "amount": "Full tuition", "deadline": date(2027, 1, 10),
     "official_url": "https://example.com"},
]
