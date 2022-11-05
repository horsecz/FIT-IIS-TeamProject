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

@app.route("/login", methods=["POST"])
def login():
    return render_template('/login.html')

##
### Actions, requests
##
@app.route('/', methods=['POST'])
def get_user():
    # get all results and return json
    users = User.query.all()
    user_schema = UserSchema(many=True)
    return jsonify(user_schema.dump(users))

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

@app.route("/login_user", methods=["POST"])
def login_user():
    global user_logged_in
    global username
    username = request.form.get("login")
    password = request.form.get("pass")
    if (username == "horse" and password == "horse"):
        user_logged_in = True
        return redirect(url_for('home'))
    else:
        return "Invalid username or password!"

@app.route("/logout", methods=["POST"])
def logout():
    global user_logged_in
    user_logged_in = False
    return redirect(url_for('home'))

@app.route('/product', methods=['GET'])
@cross_origin()
def get_product():
    # get all results and return json
    products = Product.query.all()
    product_schema = ProductSchema(many=True)
    return jsonify(product_schema.dump(products))

@app.route('/category', methods=['GET'])
@cross_origin()
def get_category():
    # get all results and return json
    categories = Category.query.all()
    category_schema = CategorySchema(many=True)
    return jsonify(category_schema.dump(categories))

@app.route('/orders', methods=['GET'])
@cross_origin()
def get_order():
    # get all results and return json
    orders = Order.query.all()
    order_schema = OrderSchema(many=True)
    return jsonify(order_schema.dump(orders))

@app.route('/edit', methods=['GET'])
@cross_origin()
def edit_user():
    try:
        db.session.query(User).filter(User.name == 'Peter').update({User.name:'Debilek'}, synchronize_session=False)
    except Exception as e:
        print('Chyba pri editu ('+str(e)+')')
    # get all results and return json
    users = User.query.all()
    user_schema = UserSchema(many=True)
    return jsonify(user_schema.dump(users))

    
#####
###     INIT AND RUN
#####

if __name__ == '__main__':
    database.create_db()
    app.run(debug=True)