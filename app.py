###
#   module:     app.py   
#   Main app module
###

### external modules
from multiprocessing import synchronize
from unicodedata import category
from flask_cors import cross_origin
from flask import render_template, redirect, url_for, request, jsonify

### our modules
import database
import backend as be
import globals

### make global variables and cross module variables/classes less ugly
app = globals.app
db = database.db
user_logged_in = globals.user_logged_in
User = database.User
UserSchema = database.UserSchema
Category = database.Category
CategorySchema = database.CategorySchema
Order = database.Order
OrderSchema = database.OrderSchema
Product = database.Product
ProductSchema = database.ProductSchema

##
### Pages
##
@app.route('/', methods=['GET'])
@cross_origin()
def home():
    be.navigationSetPageActive('home')
    return render_template('/index.html', categories=database.getCategories(), products=database.getProducts(), orders=database.getOrders(), logged=globals.user_logged_in, user=be.getLoggedUser(), nav_pages=globals.nav_pages)

@app.route("/nav/offers", methods=["GET"])
def offers():
    be.navigationSetPageActive('offers')
    return render_template('/offers.html', logged=globals.user_logged_in, user=be.getLoggedUser(), nav_pages=globals.nav_pages)

@app.route("/nav/login", methods=["GET"])
def login():
    be.navigationSetPageActive('login')
    return render_template('/login.html', logged=globals.user_logged_in, user=be.getLoggedUser(), nav_pages=globals.nav_pages, error=False)

@app.route("/nav/registration", methods=["GET"])
def registration():
    be.navigationSetPageActive('registration')
    return render_template('/registration.html', logged=globals.user_logged_in, user=be.getLoggedUser(), nav_pages=globals.nav_pages, error=0)

@app.route("/nav/user/customer", methods=["GET"])
def user_customer():
    be.navigationSetPageActive('user_customer')
    return render_template('/user/customer.html', logged=globals.user_logged_in, user=be.getLoggedUser(), nav_pages=globals.nav_pages)

@app.route("/nav/user/farmer", methods=["GET"])
def user_farmer():
    be.navigationSetPageActive('user_farmer')
    return render_template('/user/farmer.html', logged=globals.user_logged_in, user=be.getLoggedUser(), nav_pages=globals.nav_pages)

@app.route("/nav/user/settings", methods=["GET"])
def user_settings():
    be.navigationSetPageActive('user_settings')
    return render_template('/user/settings.html', logged=globals.user_logged_in, user=be.getLoggedUser(), nav_pages=globals.nav_pages, page=0, showPassword=None)

@app.route("/nav/admin/categories", methods=["GET"])
def admin_categories():
    be.navigationSetPageActive('admin_categories')
    return render_template('/admin/categories.html', logged=globals.user_logged_in, user=be.getLoggedUser(), nav_pages=globals.nav_pages)

@app.route("/nav/admin/suggestions", methods=["GET"])
def admin_suggestions():
    be.navigationSetPageActive('admin_suggestions')
    return render_template('/admin/suggestions.html', logged=globals.user_logged_in, user=be.getLoggedUser(), nav_pages=globals.nav_pages)
    
@app.route("/nav/admin/users", methods=["GET"])
def admin_users():
    be.navigationSetPageActive('admin_users')
    return render_template('/admin/users.html', logged=globals.user_logged_in, user=be.getLoggedUser(), nav_pages=globals.nav_pages, all_users=database.getUsers(), selectedID=None)

@app.route("/nav/user/settings/order/<int:id>", methods=["GET"])
def user_settings_order(id):
    be.navigationSetPageActive('user_settings')
    order = database.getOrder(id)
    prod = database.getProduct(order['product'])
    seller = database.getUser(prod['seller'])
    return render_template('/user/settings/order.html', logged=globals.user_logged_in, user=be.getLoggedUser(), nav_pages=globals.nav_pages, order=order, product=prod, seller=seller, actionShow=True)

@app.route("/nav/user/settings/calendar/<int:id>", methods=["GET"])
def user_settings_event(id):
    be.navigationSetPageActive('user_settings')
    cal = be.getUserCalendar(be.getLoggedUser())
    print(id)
    event = be.getCalendarEvent(cal, id)
    prod = database.getProduct(event[0])
    seller = database.getUser(prod['seller'])
    return render_template('/user/settings/calendar.html', logged=globals.user_logged_in, user=be.getLoggedUser(), nav_pages=globals.nav_pages, product=prod, seller=seller, eventDate=event[1], eventIndex=id, actionShow=True)


##
### Actions, requests
##
@app.route('/', methods=['POST'])
def get_user():
    # get all results and return json
    users = User.query.all()
    user_schema = UserSchema(many=True)
    return jsonify(user_schema.dump(users))

###
### For development purposes only
###

@app.route('/testFunction', methods=['POST'])
def testFunction():
    user = be.getLoggedUser()
    be.addCalendarEvent(user, 2)

    prod = database.getProduct(1)
    be.addOrder(user['id'], 1, 5)
    return redirect(url_for('home'))

###
###
###

@app.route("/login", methods=["POST"])
def login_user():
    login = request.form.get("login")
    password = request.form.get("pass")
    if (be.validateUser(login, password)):
        user = be.getUserRow(user_email=login)
        be.setLoggedUser(user)
        return redirect(url_for('home'))
    else:
        return render_template('/login.html', logged=globals.user_logged_in, user=be.getLoggedUser(), nav_pages=globals.nav_pages, error=True)

@app.route("/logout", methods=["GET"])
def logout():
    be.logoutUser()
    return redirect(url_for('home')) 

@app.route("/register", methods=["POST"])
def register_user():
    global user_logged_in
    login = request.form.get("login")
    password = request.form.get("pass")
    password2 = request.form.get("pass_repeat")
    name = request.form.get("name")
    isFarmer = request.form.get("role")
    if (password != password2):
        return render_template('/registration.html', logged=globals.user_logged_in, user=be.getLoggedUser(), nav_pages=globals.nav_pages, error=-1)
    result = be.newUser(login, password, name, 2 + isFarmer)
    if (result == 0):
        user = be.getUserRow(user_email=login)
        be.setLoggedUser(user)
        return redirect(url_for('home'))     # or: after registration page
    else:
        return render_template('/registration.html', logged=globals.user_logged_in, user=be.getLoggedUser(), nav_pages=globals.nav_pages, error=result)

@app.route("/nav/admin/users/<int:id>")
def admin_selected_user(id):
    return render_template('/admin/users.html', logged=globals.user_logged_in, user=be.getLoggedUser(), nav_pages=globals.nav_pages, all_users=database.getUsers(), selectedID=id, error=0, confirm=None)

@app.route("/nav/admin/users/<int:id>", methods=["POST"])
def admin_selected_user_action(id):
    if 'user_btn' in request.form.keys() and request.form['user_btn'] == "0":
        return render_template('/admin/users.html', logged=globals.user_logged_in, user=be.getLoggedUser(), nav_pages=globals.nav_pages, all_users=database.getUsers(), selectedID=id, error=0, confirm=True)

    if 'modify_btn' in request.form.keys() and request.form['modify_btn'] == "0":
        return render_template('/admin/users_selected.html', logged=globals.user_logged_in, user=be.getLoggedUser(), nav_pages=globals.nav_pages, all_users=database.getUsers(), selectedUser=database.getUser(id), error=-1)
    
    if globals.logged_user['id'] == id:
        s = id
        error = 1
    else:
        r = be.removeUser(id)
        if (r != None):
            return be.printInternalError(r)
        s = None
        error = 0
    return render_template('/admin/users.html', logged=globals.user_logged_in, user=be.getLoggedUser(), nav_pages=globals.nav_pages, all_users=database.getUsers(), selectedID=s, error=error, confirm=False)
    
@app.route("/nav/admin/user_selected/<int:id>", methods=["POST"])
def admin_user_selected(id):
    error = 0
    name = request.form['name']
    email = request.form['email']
    role = request.form['role']
    permissions = request.form['permissions']
    birthday = request.form['birthday']
    address = request.form['address']
    phone = request.form['phone']

    new_role = 4
    if (int(role) < 0):
        new_role = permissions
    else:
        new_role = role

    user = be.getUserRow(id)
    # TODO: not working ... (wont detect 'no changes done' after Proceed button)
    if (user['name'] == name and user['email'] == email and str(user['role']) == new_role and str(user['birth_date']) == birthday and user['address'] == address and str(user['phone_number']) == phone):
        return render_template('/admin/users_selected.html', logged=globals.user_logged_in, user=be.getLoggedUser(), nav_pages=globals.nav_pages, all_users=database.getUsers(), selectedUser=database.getUser(id), error=-1)
    
    be.editUserData(id, 'name', name)
    be.editUserData(id, 'email', email)
    be.editUserData(id, 'role', new_role)
    be.editUserData(id, 'birth_date', birthday)
    be.editUserData(id, 'address', address)
    be.editUserData(id, 'phone_number', phone)
    return render_template('/admin/users_selected.html', logged=globals.user_logged_in, user=be.getLoggedUser(), nav_pages=globals.nav_pages, all_users=database.getUsers(), selectedUser=database.getUser(id), error=error)
    
@app.route("/nav/user/settings/orders", methods=["GET"])
def user_settings_orders():
    user = be.getLoggedUser()
    orders = be.getUserOrders(user)
    return render_template('/user/settings.html', logged=globals.user_logged_in, user=be.getLoggedUser(), nav_pages=globals.nav_pages, page=1, user_orders=orders)

@app.route("/nav/user/settings/calendar", methods=["GET"])
def user_settings_calendar():
    user = be.getLoggedUser()
    cal = be.getUserCalendar(user)
    return render_template('/user/settings.html', logged=globals.user_logged_in, user=be.getLoggedUser(), nav_pages=globals.nav_pages, page=2, user_calendar=cal)


@app.route("/nav/user/settings/account_removal", methods=["GET"])
def user_settings_accountRemoval():
    return render_template('/user/settings.html', logged=globals.user_logged_in, user=be.getLoggedUser(), nav_pages=globals.nav_pages, page=3, user_calendar=be.getUserCalendar(be.getLoggedUser()))

@app.route("/nav/user/settings/edit_personal", methods=["GET"])
def user_settings_edit_personal():
    return render_template('/user/settings.html', logged=globals.user_logged_in, user=be.getLoggedUser(), nav_pages=globals.nav_pages, page=0, user_calendar=be.getUserCalendar(be.getLoggedUser()), edit=True, editType=0)

@app.route("/nav/user/settings/edit_login", methods=["GET"])
def user_settings_edit_login():
    return render_template('/user/settings.html', logged=globals.user_logged_in, user=be.getLoggedUser(), nav_pages=globals.nav_pages, page=0, user_calendar=be.getUserCalendar(be.getLoggedUser()), edit=True, editType=1)

@app.route("/nav/user/settings/edit_save/<int:t>", methods=["POST"])
def user_settings_edit_save(t):
    if (t == 0):
        bday = request.form['birthday']
        address = request.form['address']
        phone = request.form['phone']
        user = be.getLoggedUser()
        
        if (bday == user['birth_date'] and address == user['address'] and phone == str(user['phone_number'])):
            return render_template('/user/settings.html', logged=globals.user_logged_in, user=be.getLoggedUser(), nav_pages=globals.nav_pages, page=0, user_calendar=be.getUserCalendar(be.getLoggedUser()), editType=0, saved=True, error=1)
        
        be.editUserData(user['id'], 'birth_date', bday)
        be.editUserData(user['id'], 'address', address)
        be.editUserData(user['id'], 'phone_number', phone)
        return render_template('/user/settings.html', logged=globals.user_logged_in, user=be.getLoggedUser(), nav_pages=globals.nav_pages, page=0, user_calendar=be.getUserCalendar(be.getLoggedUser()), editType=0, saved=True, error=0)
    elif (t == 1):
        email = request.form['email']
        password = request.form['password']
        user = be.getLoggedUser()
        
        if (email == user['email'] and password == user['password']):
            return render_template('/user/settings.html', logged=globals.user_logged_in, user=be.getLoggedUser(), nav_pages=globals.nav_pages, page=0, user_calendar=be.getUserCalendar(be.getLoggedUser()), editType=1, saved=True, error=1)
        
        if (email == user['email']):
            return render_template('/user/settings.html', logged=globals.user_logged_in, user=be.getLoggedUser(), nav_pages=globals.nav_pages, page=0, user_calendar=be.getUserCalendar(be.getLoggedUser()), edit=True, editType=1, confirmPass=False, newPass=password)
        
        be.editUserData(user['id'], 'email', email)
        if (password == user['password']):
            return render_template('/user/settings.html', logged=globals.user_logged_in, user=be.getLoggedUser(), nav_pages=globals.nav_pages, page=0, user_calendar=be.getUserCalendar(be.getLoggedUser()), editType=1, saved=True, error=0)
        return render_template('/user/settings.html', logged=globals.user_logged_in, user=be.getLoggedUser(), nav_pages=globals.nav_pages, page=0, user_calendar=be.getUserCalendar(be.getLoggedUser()), edit=True, editType=1, confirmPass=False, newPass=password)
    else:
        email = request.form['email']
        password = request.form['password']
        repeat = request.form['passconfirm']
        user = be.getLoggedUser()

        if (repeat != password):
            return render_template('/user/settings.html', logged=globals.user_logged_in, user=be.getLoggedUser(), nav_pages=globals.nav_pages, page=0, user_calendar=be.getUserCalendar(be.getLoggedUser()), editType=1, saved=True, error=2)
        
        be.editUserData(user['id'], 'email', email)
        be.editUserData(user['id'], 'password', password)
        return render_template('/user/settings.html', logged=globals.user_logged_in, user=be.getLoggedUser(), nav_pages=globals.nav_pages, page=0, user_calendar=be.getUserCalendar(be.getLoggedUser()), editType=1, saved=True, error=0)
    
@app.route("/nav/user/settings/remove", methods=["POST"])
def user_settings_removeAccount():
    password = request.form['password']
    if (password != globals.logged_user['password']):
            return render_template('/user/settings.html', logged=globals.user_logged_in, user=be.getLoggedUser(), nav_pages=globals.nav_pages, page=3, user_calendar=be.getUserCalendar(be.getLoggedUser()), error=0)
    
    r = be.removeUser()
    if (r != None):
        return be.printInternalError(r)
    be.logoutUser()
    return redirect(url_for('home')) 

@app.route("/nav/user/settings/order/cancel%id=<int:id>", methods=["GET"])
def user_settings_order_cancel(id):
    be.navigationSetPageActive('user_settings')
    order = database.getOrder(id)
    prod = database.getProduct(order['product'])
    seller = database.getUser(prod['seller'])
    return render_template('/user/settings/order_cancel.html', logged=globals.user_logged_in, user=be.getLoggedUser(), nav_pages=globals.nav_pages, order=order, product=prod, seller=seller)

@app.route("/nav/user/settings/order/cancel/go%id=<int:id>", methods=["POST"])
def user_settings_order_cancel_go(id):
    be.navigationSetPageActive('user_settings')
    order = database.getOrder(id)
    prod = database.getProduct(order['product'])
    seller = database.getUser(prod['seller'])
    database.modifyData(database.Order, id, 'status', -1)
    return redirect(url_for('user_settings_orders'))

@app.route("/nav/user/settings/order/repeat%id=<int:id>%page=<int:page>", methods=["GET"])
def user_settings_order_repeat(id, page):
    be.navigationSetPageActive('user_settings')
    order = database.getOrder(id)
    prod = database.getProduct(order['product'])
    seller = database.getUser(prod['seller'])
    if (page == 0):
        return render_template('/user/settings/order_repeat.html', logged=globals.user_logged_in, user=be.getLoggedUser(), nav_pages=globals.nav_pages, order=order, product=prod, seller=seller, page=0)
    elif (page == 1):
        return render_template('/user/settings/order_repeat.html', logged=globals.user_logged_in, user=be.getLoggedUser(), nav_pages=globals.nav_pages, order=order, product=prod, seller=seller, page=1)
    elif (page == 2):
        return render_template('/user/settings/order_repeat.html', logged=globals.user_logged_in, user=be.getLoggedUser(), nav_pages=globals.nav_pages, order=order, product=prod, seller=seller, page=2)
    else:
        print('order created')
        return redirect(url_for('user_settings_orders'))

@app.route("/nav/new_order/<int:id><int:isRepeat>", methods=["GET"])
def new_order(id, isRepeat):
    if (isRepeat == 1):
        order = database.getOrder(id)
        prod = database.getProduct(order['product'])
        quantity = order['quantity']
        seller = database.getUser(prod['seller'])
        sProds = []
        for prods in database.getProducts():
            if prods['seller'] == seller['id']:
                sProds.append(prods)
        return render_template('/new_order.html', repeatedOrder=True, sellerProducts=sProds, logged=globals.user_logged_in, user=be.getLoggedUser(), nav_pages=globals.nav_pages, order=order, product=prod, seller=seller, oldQuantity=quantity)
    else:
        prod = database.getProduct(id)
        seller = database.getUser(prod['seller'])
        sProds = []
        for prods in database.getProducts():
            if prods['seller'] == seller['id']:
                sProds.append(prods)
        return render_template('/new_order.html', sellerProducts=sProds, logged=globals.user_logged_in, user=be.getLoggedUser(), nav_pages=globals.nav_pages, product=prod, seller=seller)
    
@app.route("/nav/user/settings/calendar/remove_q%id=<int:id>", methods=["GET"])
def user_settings_calendar_remove_q(id):
    be.navigationSetPageActive('user_settings')
    cal = be.getUserCalendar(be.getLoggedUser())
    event = be.getCalendarEvent(cal, id)
    prod = database.getProduct(event[0])
    seller = database.getUser(prod['seller'])
    return render_template('/user/settings/calendar_cancel.html', logged=globals.user_logged_in, user=be.getLoggedUser(), nav_pages=globals.nav_pages, product=prod, seller=seller, eventDate=event[1], eventIndex=id)

@app.route("/nav/user/settings/calendar/remove%id=<int:id>", methods=["POST"])
def user_settings_calendar_remove(id):
    be.navigationSetPageActive('user_settings')
    loggedUser = be.getLoggedUser()
    cal = be.getUserCalendar(loggedUser)
    event = be.getCalendarEvent(cal, id)
    cal.remove(event)

    database.modifyData(database.User, loggedUser['id'], 'calendar', cal)
    return redirect(url_for('user_settings_calendar'))



### TODO:
### Dont create order immediately but create sub-step 'summary' page and then create order
@app.route("/nav/new_order/go", methods=["POST"])
def new_order_go():
    buyer = request.form['buyer_id']
    product = request.form['product']
    quantity = request.form['quantity']

    be.addOrder(buyer, product, quantity)
    print('order created!')
    return redirect(url_for('home'))
#####
###     INIT AND RUN
#####

if __name__ == '__main__':
    be.navigationLoadPages()
    be.loadJinjaGlobals()
    be.logoutUser()
    be.init()
    app.run(debug=True)