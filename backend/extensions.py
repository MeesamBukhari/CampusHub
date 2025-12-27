from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_cors import CORS

# Initialize extensions here to prevent circular imports
db = SQLAlchemy()
bcrypt = Bcrypt()
cors = CORS()