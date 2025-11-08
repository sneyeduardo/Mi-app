import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'sistema-prestamos-secreto-2025'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///prestamos.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
