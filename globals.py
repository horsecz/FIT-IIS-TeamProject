###
#   module:     globals.py   
#   Sharing global variables (and other) across modules
###

from flask_cors import CORS
from flask import Flask

# App Core
app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://postgres:postgres@localhost:5432/postgres'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# User Data
user_logged_in = False          #   is user logged in?
logged_user = None              #   logged user data
nav_current_page = "index"      #   current opene page for navbar
nav_pages = []                  #   list of pages in navigation bar
path = []                       #   current navigation path