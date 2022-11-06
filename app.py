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
username = globals.username
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
    return render_template('/index.html', categories=database.getCategories(), products=database.getProducts(), orders=database.getOrders(), logged=user_logged_in, username=be.getUsername())

@app.route("/nav/offers", methods=["GET"])
def offers():
    return render_template('/offers.html', logged=user_logged_in, username=be.getUsername())

@app.route("/nav/login", methods=["GET"])
def login():
    return render_template('/login.html', logged=user_logged_in, username=be.getUsername())

@app.route("/nav/registration", methods=["GET"])
def registration():
    return render_template('/registration.html', logged=user_logged_in, username=be.getUsername())

@app.route("/nav/user/customer", methods=["GET"])
def user_customer():
    return render_template('/user/customer.html', logged=user_logged_in, username=be.getUsername())

@app.route("/nav/user/farmer", methods=["GET"])
def user_farmer():
    return render_template('/user/farmer.html', logged=user_logged_in, username=be.getUsername())

@app.route("/nav/user/settings", methods=["GET"])
def user_settings():
    return render_template('/user/settings.html', logged=user_logged_in, username=be.getUsername())

@app.route("/nav/admin/categories", methods=["GET"])
def admin_categories():
    return render_template('/admin/categories.html', logged=user_logged_in, username=be.getUsername())

@app.route("/nav/admin/suggestions", methods=["GET"])
def admin_suggestions():
    return render_template('/admin/suggestions.html', logged=user_logged_in, username=be.getUsername())
    
@app.route("/nav/admin/users", methods=["GET"])
def admin_users():
    return render_template('/admin/users.html', logged=user_logged_in, username=be.getUsername())


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
    global username
    login = request.form.get("login")
    password = request.form.get("pass")
    if (be.validateUser(login, password)):
        user_logged_in = True
        user = database.getUserByEmail(login)
        be.setUsername(user['name'])
        return redirect(url_for('home'))
    else:
        return "Invalid username or password!"

@app.route("/logout", methods=["GET"])
def logout():
    global user_logged_in
    user_logged_in = False
    return redirect(url_for('home'))

@app.route("/register", methods=["POST"])
def register_user():
    global user_logged_in
    global username
    login = request.form.get("login")
    password = request.form.get("pass")
    password2 = request.form.get("pass_repeat")
    name = request.form.get("name")
    role = request.form.get("role")
    if (password != password2):
        return "Both passwords must match!"
    result = be.newUser(login, password, name, role)
    if (result == 0):
        user_logged_in = True
        user = database.getUserByEmail(login)
        be.setUsername(user['name'])
        return redirect(url_for('home'))     # or: after registration page
    elif (result == 1):
        return "User exists!"
    elif (result == 2):
        return "Invalid password!"

    
#####
###     INIT AND RUN
#####

if __name__ == '__main__':
    database.create_db()
    app.run(debug=True)