###
#   module:     backend.py   
#   Backend module
###

import globals
import database

db = database
nav_current_page = globals.nav_current_page
logged_user = globals.logged_user

def isUserModerator(user):
    if (user['role'] == 1):
        return True
    return False

def isUserAdmin(user):
    if (user['role'] == 2):
        return True
    return False

# loads navigation bar pages
def navigationLoadPages():
    globals.nav_pages = [['home', False, 'Domů'], 
    ['offers', False, 'Nabídky'], ['user_customer', False, 'Zákazník'], ['user_farmer', False, 'Farmář'], 
    ['admin_categories', False, 'Správa kategorií'], ['admin_suggestions', False, 'Správa návrhů'], ['admin_users', False, 'Správa uživatelů']]

# sets page active in navigation bar
def navigationSetPageActive(page_name):
    for x in globals.nav_pages:
        if x[0] == page_name:
            x[1] = True
        else:
            x[1] = False

# returns: 0 OK; 1 user exists; 2 bad password format; 3 too long name
def newUser(login, password, name, role, isFarmer):
    if (database.getUserByEmail(login) != None):
        return 1
    if (len(password) < 5 or len(password) > database.DB_STRING_SHORT_MAX):
        return 2
    if (len(name) > database.DB_STRING_SHORT_MAX):
        return 3
    if (len(name) < 1):
        name = "Uživatel"
    database.addUser(login, name, password, role, isFarmer)
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