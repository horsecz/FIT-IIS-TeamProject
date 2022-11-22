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
    cal = be.getUserCalendar(user)
    be.addCalendarEvent(cal, 2)
    return redirect(url_for('home'))

###
###
###

@app.route("/login", methods=["POST"])
def login_user():
    login = request.form.get("login")
    password = request.form.get("pass")
    if (be.validateUser(login, password)):
        globals.user_logged_in = True
        user = database.getUserByEmail(login)
        be.setLoggedUser(user)
        return redirect(url_for('home'))
    else:
        return render_template('/login.html', logged=globals.user_logged_in, user=be.getLoggedUser(), nav_pages=globals.nav_pages, error=True)

@app.route("/logout", methods=["GET"])
def logout():
    globals.user_logged_in = False
    globals.logged_user = database.unregistered_user
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
        globals.user_logged_in = True
        user = database.getUserByEmail(login)
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
        r = database.removeData(User, id)
        if (r != None):
            print(r)
            return "Internal error: Unable to remove this account. Please contact website administrator.<br><br>Error:<br>"+r
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

    user = database.getUser(id)
    # TODO: not working ... (wont detect 'no changes done' after Proceed button)
    if (user['name'] == name and user['email'] == email and str(user['role']) == new_role and str(user['birth_date']) == birthday and user['address'] == address and str(user['phone_number']) == phone):
        return render_template('/admin/users_selected.html', logged=globals.user_logged_in, user=be.getLoggedUser(), nav_pages=globals.nav_pages, all_users=database.getUsers(), selectedUser=database.getUser(id), error=-1)
    
    database.modifyData(database.User, id, 'name', name)
    database.modifyData(database.User, id, 'email', email)
    database.modifyData(database.User, id, 'role', new_role)
    database.modifyData(database.User, id, 'birth_date', birthday)
    database.modifyData(database.User, id, 'address', address)
    database.modifyData(database.User, id, 'phone_number', phone)
    return render_template('/admin/users_selected.html', logged=globals.user_logged_in, user=be.getLoggedUser(), nav_pages=globals.nav_pages, all_users=database.getUsers(), selectedUser=database.getUser(id), error=error)
    
@app.route("/nav/user/settings/orders", methods=["GET"])
def user_settings_orders():
    return render_template('/user/settings.html', logged=globals.user_logged_in, user=be.getLoggedUser(), nav_pages=globals.nav_pages, page=1, user_orders=be.getUserOrders(be.getLoggedUser()))

@app.route("/nav/user/settings/calendar", methods=["GET"])
def user_settings_calendar():
    return render_template('/user/settings.html', logged=globals.user_logged_in, user=be.getLoggedUser(), nav_pages=globals.nav_pages, page=2, user_calendar=be.getUserCalendar(be.getLoggedUser()))


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
        
        database.modifyData(database.User, user['id'], 'birth_date', bday)
        database.modifyData(database.User, user['id'], 'address', address)
        database.modifyData(database.User, user['id'], 'phone_number', phone)
        return render_template('/user/settings.html', logged=globals.user_logged_in, user=be.getLoggedUser(), nav_pages=globals.nav_pages, page=0, user_calendar=be.getUserCalendar(be.getLoggedUser()), editType=0, saved=True, error=0)
    elif (t == 1):
        print('t=1')
        email = request.form['email']
        password = request.form['password']
        user = be.getLoggedUser()
        
        if (email == user['email'] and password == user['password']):
            return render_template('/user/settings.html', logged=globals.user_logged_in, user=be.getLoggedUser(), nav_pages=globals.nav_pages, page=0, user_calendar=be.getUserCalendar(be.getLoggedUser()), editType=1, saved=True, error=1)
        
        if (email == user['email']):
            return render_template('/user/settings.html', logged=globals.user_logged_in, user=be.getLoggedUser(), nav_pages=globals.nav_pages, page=0, user_calendar=be.getUserCalendar(be.getLoggedUser()), edit=True, editType=1, confirmPass=False, newPass=password)
        
        database.modifyData(database.User, user['id'], 'email', email)
        if (password == user['password']):
            return render_template('/user/settings.html', logged=globals.user_logged_in, user=be.getLoggedUser(), nav_pages=globals.nav_pages, page=0, user_calendar=be.getUserCalendar(be.getLoggedUser()), editType=1, saved=True, error=0)
        return render_template('/user/settings.html', logged=globals.user_logged_in, user=be.getLoggedUser(), nav_pages=globals.nav_pages, page=0, user_calendar=be.getUserCalendar(be.getLoggedUser()), edit=True, editType=1, confirmPass=False, newPass=password)
    else:
        print('t=2')
        email = request.form['email']
        password = request.form['password']
        repeat = request.form['passconfirm']
        user = be.getLoggedUser()

        if (repeat != password):
            return render_template('/user/settings.html', logged=globals.user_logged_in, user=be.getLoggedUser(), nav_pages=globals.nav_pages, page=0, user_calendar=be.getUserCalendar(be.getLoggedUser()), editType=1, saved=True, error=2)
        
        database.modifyData(database.User, user['id'], 'email', email)
        database.modifyData(database.User, user['id'], 'password', password)
        return render_template('/user/settings.html', logged=globals.user_logged_in, user=be.getLoggedUser(), nav_pages=globals.nav_pages, page=0, user_calendar=be.getUserCalendar(be.getLoggedUser()), editType=1, saved=True, error=0)
    
@app.route("/nav/user/settings/remove", methods=["POST"])
def user_settings_removeAccount():
    password = request.form['password']
    if (password != globals.logged_user['password']):
            return render_template('/user/settings.html', logged=globals.user_logged_in, user=be.getLoggedUser(), nav_pages=globals.nav_pages, page=3, user_calendar=be.getUserCalendar(be.getLoggedUser()), error=0)
    
    be.getLoggedUser()
    removal_id = globals.logged_user['id']
    removal_data = globals.logged_user
    r = database.removeData(User, removal_id)
    if (r != None):
        print(r)
        return "Internal error: Unable to remove this account. Please contact website administrator.<br><br>Error:<br>"+r

    globals.user_logged_in = False
    globals.logged_user = database.unregistered_user
    return redirect(url_for('home')) 

#####
###     INIT AND RUN
#####

if __name__ == '__main__':
    be.navigationLoadPages()
    be.loadJinjaGlobals()
    globals.user_logged_in = False
    globals.logged_user = database.unregistered_user
    database.create_db()
    app.run(debug=True)