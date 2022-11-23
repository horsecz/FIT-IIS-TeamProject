###
#   module:     backend.py   
#   Backend module
###

import globals
import database
import re
import datetime

db = database
nav_current_page = globals.nav_current_page
logged_user = globals.logged_user

###
#   Functions and variables available in FrontEnd (Jinja2)
###

# load and init all functions to jinja2
def loadJinjaGlobals():
    app = globals.app
    app.jinja_env.globals.update(getSelfCollectionLocation=getSelfCollectionLocation)
    app.jinja_env.globals.update(getLoggedUserOrders=getLoggedUserOrders)
    app.jinja_env.globals.update(getLoggedUserSells=getLoggedUserSells)
    app.jinja_env.globals.update(getUsedCurrency=getUsedCurrency)

def getUsedCurrency():
    return "ISC"

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

###
#   Backend functions
###

# returns user row element in UserSchema format
# primary searches by USER ID, if specified, EMAIL is used instead
# if both specified, searches by both and if found, returns first non NoneType value
def getUserRow(user_id=None, user_email=None):
    if (user_id == None) and (user_email == None):
        return None

    if (user_id != None) and (user_email != None):
        r = database.getUser(user_id)
        if (r != None):
            return r
        else:
            return database.getUser(user_email)
    
    if (user_id != None):
        return database.getUser(user_id)

    if (user_email != None):
        return database.getUserByEmail(user_email)

def editUserData(user_id, user_data, value):
    database.modifyData(database.User, user_id, user_data, value)

# returns None OK; or string of error/exception
def removeUser(user_id=None):
    if user_id == None:
        getLoggedUser()
        removal_id = globals.logged_user['id']
        r = database.removeData(database.User, removal_id)
        return r
    else:
        removal_id = user_id
        r = database.removeData(database.User, removal_id)
        return r


# returns 0 OK; 1 exceeded maximum product quantity
def addOrder(user_id, product_id, quantity, price=None, date=None, status=1):
    if (date == None):
        today = datetime.datetime.today()
        day = today.day
        month = today.month
        year = today.year
        date = str(year) + "-" + str(month) + "-" + str(day)

    prod = database.getProduct(product_id)
    if (price == None):
        price = prod['price'] * quantity

    if (prod['quantity'] < quantity):
        return 1

    database.addOrder(user_id, product_id, quantity, price, date, status)
    return 0

def removeCalendarEvent(user, event):
    calendar = user['calendar']
    calendar.remove(event)
    database.modifyData(database.User, user['id'], 'calendar', calendar)

def addCalendarEvent(user, product_id):
    calendar = user['calendar']
    event = []
    prod = database.getProduct(product_id)
    date_f = prod['begin_date']
    date_t = prod['end_date']
    event.append(product_id)
    event.append(date_f)
    event.append(date_t)
    calendar.append(event)
    database.modifyData(database.User, user['id'], 'calendar', calendar)

def getUserCalendar(user):
    calendar_id_list = user['calendar']
    return calendar_id_list

def getUserOrders(user):
    id = user['id']
    order_list = []
    for order_row in database.getOrders():
        if (order_row['buyer'] == id):
            order_list.append(order_row)
    return order_list

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
    globals.user_logged_in = True

def logoutUser():
    globals.user_logged_in = False
    globals.logged_user = database.unregistered_user

def printInternalError(additional_text):
    return "Internal error: Unable to remove this account. Please contact website administrator.<br><br>Error:<br>"+additional_text

def init():
    database.create_db()