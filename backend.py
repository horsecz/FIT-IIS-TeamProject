###
#   module:     backend.py   
#   Backend module
###

import globals
import database

db = database
username = globals.username

# returns: 0 OK; 1 user exists; 2 bad password format
def newUser(login, password, name, role):
    if (database.getUserByEmail(login) != None):
        return 1
    if (len(password) < 5 or len(password) > database.DB_STRING_SHORT_MAX):
        return 2

    database.addUser(login, name, password, role)
    return 0

def validateUser(login, password):
    user = database.getUserByEmail(login)
    if (user != None and user['password'] == password):
        return True
    return False

def getUsername():
    global username
    return username

def setUsername(name):
    global username
    username = name