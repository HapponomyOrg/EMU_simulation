import os

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'kjbfjehbrf ezhb 3ihdf'
    MONGO_URI = "mongodb://localhost:27017/myDatabase"
