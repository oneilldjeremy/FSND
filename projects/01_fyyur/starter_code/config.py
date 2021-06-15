import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

database_name = "fyyur"
USER = os.getenv('PGUSER')
PASSWORD = os.environ.get('PGPASSWORD')

database_path = "postgresql://{}:{}@{}/{}".format(USER, PASSWORD,'localhost:5432', database_name)

# Enable debug mode.
DEBUG = True

SQLALCHEMY_TRACK_MODIFICATIONS = False

SQLALCHEMY_DATABASE_URI = database_path
