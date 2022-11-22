###
#   module:     backend.py   
#   Backend module
###

import globals
import database
import re

db = database
nav_current_page = globals.nav_current_page
logged_user = globals.logged_user

def isUserModerator(user):
    if (user['role'] == 1):
        return True
    return False

def isUserAdmin(user):
    if (user['role'] == 0):
        return True
    return False

# loads navigation bar pages
def navigationLoadPages():
    globals.nav_pages = [['home', False, 'Home'], 
    ['offers', False, 'Offers'], ['user_customer', False, 'Customer'], ['user_farmer', False, 'Farmer'], 
    ['admin_categories', False, 'Category suggestions'], ['admin_suggestions', False, 'Category management'], ['admin_users', False, 'User management']]

# sets page active in navigation bar
def navigationSetPageActive(page_name):
    for x in globals.nav_pages:
        if x[0] == page_name:
            x[1] = True
        else:
            x[1] = False

# returns: 0 OK; 1 user exists; 2 bad password format; 3 too long name; 4 invalid email format
def newUser(login, password, name, role):
    if (database.getUserByEmail(login) != None):
        return 1
    if (len(password) < 5 or len(password) > database.DB_STRING_SHORT_MAX):
        return 2
    if (len(name) > database.DB_STRING_SHORT_MAX):
        return 3
    if not (re.search("[A-z0-9.]+@[A-z0-9]+([.][A-z0-9])+", login)):
        return 4
    if (len(name) < 1):
        name = "User"
    database.addUser(login, name, password, role)
    return 0

def validateUser(login, password):
    user = database.getUserByEmail(login)
    if (user != None and user['password'] == password):
        return True
    return False

def getLoggedUser():
    return globals.logged_user

def setLoggedUser(user):
    globals.logged_user = user