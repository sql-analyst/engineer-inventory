from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

host = os.getenv("MYSQL_HOST")
user = os.getenv("MYSQL_USER")
password = os.getenv("MYSQL_PASSWORD")
db = os.getenv("MYSQL_DB")
port = os.getenv("MYSQL_PORT")
app_secret_key = os.getenv("APP_SECRET_KEY")
s3_access_key_id = os.getenv("S3_ACCESS_KEY_ID")
s3_secret_access_key = os.getenv("S3_SECRET_ACCESS_KEY")
s3_region = os.getenv("S3_REGION")
s3_bucket_name = os.getenv("S3_BUCKET_NAME")
