import os
from dotenv import load_dotenv

load_dotenv()

db_username = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_host = os.getenv("DB_HOST")
db_name = os.getenv("DB_NAME")

DB_URL = f'postgresql+psycopg2://{db_username}:{db_password}@{db_host}/{db_name}'
POOL_SIZE = 5
MAX_OVERFLOW = 10

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

UPLOAD_DIR = "uploads"
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "gif"}