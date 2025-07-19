import os

from dotenv import load_dotenv
load_dotenv()

allowed_extensions = os.getenv('ALLOWED_EXTENSIONS', 'pdf').split(',')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions