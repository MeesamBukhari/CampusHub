import os
from datetime import timedelta

class Config:
    # Security keys
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-super-secret-key-change-in-prod'
    
    # Database Configuration (Update 'root:password' with your MySQL credentials)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'mysql+mysqlconnector://root:password@localhost/campushub'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # MySQL Connector Configuration
    DB_CONFIG = {
        'host': 'localhost',
        'user': 'root',
        'password': '',
        'database': 'campushub'
    }
    
    # Session Security (Req 7)
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30) # Auto-expiry
    SESSION_COOKIE_HTTPONLY = True # Prevent JS access to cookies
    SESSION_COOKIE_SAMESITE = 'Lax' # CSRF protection
    SESSION_COOKIE_SECURE = False # Set to True if using HTTPS