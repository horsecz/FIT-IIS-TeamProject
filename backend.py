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

def loadJinjaGlobals():
    app = globals.app
    app.jinja_env.globals.update(getSelfCollectionLocation=getSelfCollectionLocation)
    app.jinja_env.globals.update(getLoggedUserOrders=getLoggedUserOrders)
    app.jinja_env.globals.update(getLoggedUserSells=getLoggedUserSells)

def getLoggedUserSells():
    list = []
    product_list = []
    user = getLoggedUser()
    if user == None:
        return list

    for product in database.getProducts():
        if database.isSellingProduct(product['id'], user['id']):
            product_list.append(product)

    if len(product_list) == 0:
        return list
    
    for order in database.getOrders():
        if order['product'] in product_list:
            list.append(order)
    
    return list

def getLoggedUserOrders():
    list = []
    user = getLoggedUser()
    if user == None:
        return list
    
    for order in database.getOrders():
        if user['id'] == order['buyer']:
            list.append(order)
    
    return list


# returns address string if OK; 1 if product not found; 2 if seller/user not found
def getSelfCollectionLocation(event):
    product_id = event[0]
    product = database.getProduct(product_id)
    if (product == None):
        return 1
    seller = database.getUser(product['seller'])
    if (seller == None):
        return 2
    return seller['address']

def removeCalendarEvent(calendar, event):
    calendar.remove(event)

def addCalendarEvent(calendar, product_id):
    event = []
    prod = database.getProduct(product_id)
    date_f = prod['begin_date']
    date_t = prod['end_date']
    event.append(product_id)
    event.append(date_f)
    event.append(date_t)
    calendar.append(event)

def getUserCalendar(user):
    calendar_id_list = user['calendar']
    return calendar_id_list

def getUserOrders(user):
    id = user['id']
    order_id_list = []
    for order_row in database.getOrders():
        if (order_row['buyer'] == id):
            order_id_list.append(order_row['id'])
    return order_id_list

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
    ['offers', False, 'Farmers'], ['user_customer', False, 'Suggestions'], ['user_farmer', False, 'My Products'], 
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
    if (globals.logged_user == None or globals.user_logged_in == False):
        return database.unregistered_user
    user_id = globals.logged_user['id']
    new_user = database.getUser(user_id)
    globals.logged_user = new_user
    return globals.logged_user

def setLoggedUser(user):
    globals.logged_user = user