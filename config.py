import os
from dotenv import load_dotenv

load_dotenv()

base_dir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(base_dir, os.getenv('DATABASE_NAME', 'database.db'))

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'secret_key')
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{db_path}'
