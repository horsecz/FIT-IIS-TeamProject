###
#   module:     backend.py   
#   Backend module
###

import globals
import database

db = database
username = globals.username

def getUsername():
    global username
    return username