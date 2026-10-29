import os
from dotenv import load_dotenv

load_dotenv()  # reads the .env file


class Config:
       SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")
       SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///scholarship.db")