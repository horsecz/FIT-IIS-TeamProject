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
    return render_template('/index.html', categories=database.getSubCategories(1), category=None, products=database.getProducts(), orders=database.getOrders(), logged=user_logged_in, user=be.getLoggedUser(), nav_pages=globals.nav_pages, all_cats=database.getCategories())

@app.route("/nav/offers", methods=["GET"])
def offers():
    be.navigationSetPageActive('offers')
    return render_template('/offers.html', logged=user_logged_in, user=be.getLoggedUser(), nav_pages=globals.nav_pages, farmers=database.getUsersByRole(2))

@app.route("/nav/login", methods=["GET"])
def login():
    be.navigationSetPageActive('login')
    return render_template('/login.html', logged=user_logged_in, user=be.getLoggedUser(), nav_pages=globals.nav_pages, error=False)

@app.route("/nav/registration", methods=["GET"])
def registration():
    be.navigationSetPageActive('registration')
    return render_template('/registration.html', logged=user_logged_in, user=be.getLoggedUser(), nav_pages=globals.nav_pages, error=0)

@app.route("/nav/user/customer", methods=["GET"])
def user_customer():
    be.navigationSetPageActive('user_customer')
    return render_template('/user/customer.html', logged=user_logged_in, user=be.getLoggedUser(), nav_pages=globals.nav_pages)

@app.route("/nav/user/farmer", methods=["GET"])
def user_farmer():
    be.navigationSetPageActive('user_farmer')
    return render_template('/user/farmer.html', logged=user_logged_in, user=be.getLoggedUser(), nav_pages=globals.nav_pages)

@app.route("/nav/user/settings", methods=["GET"])
def user_settings():
    be.navigationSetPageActive('user_settings')
    return render_template('/user/settings.html', logged=user_logged_in, user=be.getLoggedUser(), nav_pages=globals.nav_pages)

@app.route("/nav/admin/categories", methods=["GET"])
def admin_categories():
    be.navigationSetPageActive('admin_categories')
    return render_template('/admin/categories.html', logged=user_logged_in, user=be.getLoggedUser(), nav_pages=globals.nav_pages)

@app.route("/nav/admin/suggestions", methods=["GET"])
def admin_suggestions():
    be.navigationSetPageActive('admin_suggestions')
    return render_template('/admin/suggestions.html', logged=user_logged_in, user=be.getLoggedUser(), nav_pages=globals.nav_pages)
    
@app.route("/nav/admin/users", methods=["GET"])
def admin_users():
    be.navigationSetPageActive('admin_users')
    return render_template('/admin/users.html', logged=user_logged_in, user=be.getLoggedUser(), nav_pages=globals.nav_pages, all_users=database.getUsers(), selectedID=None)

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
    x = database.getCategoryByName('root')
    if x == None:
        print('not found this shit')
        return redirect(url_for('home'))

    #result = database.modifyData(database.Category, x['id'], 'name', 'definitely not fruit')
    result = database.removeData(database.Category, x['id'])
    if (result != None):
        print(result)
    return redirect(url_for('home'))

###
###
###

@app.route("/login", methods=["POST"])
def login_user():
    global user_logged_in
    login = request.form.get("login")
    password = request.form.get("pass")
    if (be.validateUser(login, password)):
        user_logged_in = True
        user = database.getUserByEmail(login)
        be.setLoggedUser(user)
        return redirect(url_for('home'))
    else:
        return render_template('/login.html', logged=user_logged_in, user=be.getLoggedUser(), nav_pages=globals.nav_pages, error=True)

@app.route("/logout", methods=["GET"])
def logout():
    global user_logged_in
    user_logged_in = False
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
        return render_template('/registration.html', logged=user_logged_in, user=be.getLoggedUser(), nav_pages=globals.nav_pages, error=-1)
    result = be.newUser(login, password, name, 2 + isFarmer)
    if (result == 0):
        user_logged_in = True
        user = database.getUserByEmail(login)
        be.setLoggedUser(user)
        return redirect(url_for('home'))     # or: after registration page
    else:
        return render_template('/registration.html', logged=user_logged_in, user=be.getLoggedUser(), nav_pages=globals.nav_pages, error=result)

@app.route("/nav/admin/users/<int:id>")
def admin_selected_user(id):
    return render_template('/admin/users.html', logged=user_logged_in, user=be.getLoggedUser(), nav_pages=globals.nav_pages, all_users=database.getUsers(), selectedID=id, error=0, confirm=None)

@app.route("/nav/admin/users/<int:id>", methods=["POST"])
def admin_selected_user_action(id):
    if 'user_btn' in request.form.keys() and request.form['user_btn'] == "0":
        return render_template('/admin/users.html', logged=user_logged_in, user=be.getLoggedUser(), nav_pages=globals.nav_pages, all_users=database.getUsers(), selectedID=id, error=0, confirm=True)

    if 'modify_btn' in request.form.keys() and request.form['modify_btn'] == "0":
        return render_template('/admin/users_selected.html', logged=user_logged_in, user=be.getLoggedUser(), nav_pages=globals.nav_pages, all_users=database.getUsers(), selectedUser=database.getUser(id), error=-1)
    
    if globals.logged_user['id'] == id:
        s = id
        error = 1
    else:
        database.removeData(User, id)
        s = None
        error = 0
    return render_template('/admin/users.html', logged=user_logged_in, user=be.getLoggedUser(), nav_pages=globals.nav_pages, all_users=database.getUsers(), selectedID=s, error=error, confirm=False)
    
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
    if (user['name'] == name and user['email'] == email and user['role'] == new_role and user['birth_date'] == birthday and user['address'] == address and user['phone_number'] == phone):
        return render_template('/admin/users_selected.html', logged=user_logged_in, user=be.getLoggedUser(), nav_pages=globals.nav_pages, all_users=database.getUsers(), selectedUser=database.getUser(id), error=-1)
    
    database.modifyData(database.User, id, 'name', name)
    database.modifyData(database.User, id, 'email', email)
    database.modifyData(database.User, id, 'role', new_role)
    database.modifyData(database.User, id, 'birth_date', birthday)
    database.modifyData(database.User, id, 'address', address)
    database.modifyData(database.User, id, 'phone_number', phone)
    return render_template('/admin/users_selected.html', logged=user_logged_in, user=be.getLoggedUser(), nav_pages=globals.nav_pages, all_users=database.getUsers(), selectedUser=database.getUser(id), error=error)
  
#renders home page with all subcategories of selected category
@app.route("/home/<string:id>", methods=["GET"])
def category(id):
    cat = database.getCategory(int(id))
    is_leaf = cat['leaf']
    if is_leaf:
        return render_template('/index.html', logged=user_logged_in, user=be.getLoggedUser(), nav_pages=globals.nav_pages, category=cat, products=database.getProductsByCategory(id))
    else:
        return render_template('/index.html', logged=user_logged_in, user=be.getLoggedUser(), nav_pages=globals.nav_pages, category=cat, categories=database.getSubCategories(id))
    
@app.route("/product/<int:id>", methods=["GET"])
def product(id):
    return render_template('/product.html', logged=user_logged_in, user=be.getLoggedUser(), nav_pages=globals.nav_pages, product=database.getProduct(id), seller=database.getUser(database.getProduct(id)['seller']))

@app.route("/product/<int:id>", methods=["POST"])
def add_to_calendar(id):
    return render_template('/product.html', logged=user_logged_in, user=be.getLoggedUser(), nav_pages=globals.nav_pages, product=database.getProduct(id), seller=database.getUser(database.getProduct(id)['seller']))

@app.route("/product/<int:id>", methods=["POST"])
def create_order(id):
    return render_template('/product.html', logged=user_logged_in, user=be.getLoggedUser(), nav_pages=globals.nav_pages, product=database.getProduct(id), seller=database.getUser(database.getProduct(id)['seller']))

@app.route("/farmer/<int:id>", methods=["GET"])
def open_farmer(id):
    return render_template('/user/farmer.html', logged=user_logged_in, user=be.getLoggedUser(), nav_pages=globals.nav_pages, farmer=database.getUser(id))

# @app.route("/home/name", methods=["GET"])
# def search():
#     name = request.form['q']
#     cat = database.getCategoryByName(name)
#     if cat:
#         if cat['leaf']:
#             return render_template('/index.html', logged=user_logged_in, user=be.getLoggedUser(), nav_pages=globals.nav_pages, category=cat, products=database.getProductsByCategory(id))
#         else:
#             return render_template('/index.html', logged=user_logged_in, user=be.getLoggedUser(), nav_pages=globals.nav_pages, category=cat, categories=database.getSubCategories(id))
#     else:
#         return render_template('/index.html', logged=user_logged_in, user=be.getLoggedUser(), nav_pages=globals.nav_pages, category=None)




#####
###     INIT AND RUN
#####

if __name__ == '__main__':
    be.navigationLoadPages()
    globals.logged_user = database.unregistered_user
    database.create_db()
    app.run(debug=True)