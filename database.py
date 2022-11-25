###
#   module:     database.py   
#   Database module
###
from flask import request
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy import PickleType
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

import globals
import backend

app = globals.app
db = SQLAlchemy(app)
ma = Marshmallow(app)
db_init_done = True

DB_STRING_SHORT_MAX = 150       # maximum characters for short strings  (name, e-mail, password)
DB_STRING_LONG_MAX = 500        # maximum characters for long strings   (address, description)
DB_INT_MAX = 2147483647         # C integer max, same for our database
DB_INT_MIN = -2147483648        # C integer min, same for our db

# Init
def init_db():
    global db
    global ma
    global db_init_done
    if db_init_done == True:
        return
    else:
        db_init_done = True
    db = SQLAlchemy(app)
    ma = Marshmallow(app)

init_db()

class FlaskUser():
    id = 0
    email = ""
    logged = False
    active = True

    def __init__(self, id, email):
        self.id = id
        self.email = email
        self.logged = False

    def is_authenticated(self):
        return self.logged

    def is_active(self):
        return self.active

    def is_anonymous(self):
        if (self.email == None):
            return True
        else:
            return False

    def get_id(self):
        return str(self.id) 

    def new_user(self, user_id, user_email):
        self.id = user_id
        self.email = user_email

    def set_logged(self, isLogged):
        self.logged = isLogged


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(DB_STRING_SHORT_MAX))
    name = db.Column(db.String(DB_STRING_SHORT_MAX))
    birth_date = db.Column(db.Date)
    address = db.Column(db.String(DB_STRING_LONG_MAX))
    password = db.Column(db.String(DB_STRING_SHORT_MAX))
    role = db.Column(db.Integer)
    phone_number = db.Column(db.Integer)
    calendar = db.Column(MutableList.as_mutable(PickleType), default=[])
    cart = db.Column(MutableList.as_mutable(PickleType), default=[])
    account_status = db.Column(db.Boolean)

    def __init__(self, email, name, birth_date, address, password, role, phone_number, calendar, cart, account_status):
        self.email = email
        self.name = name
        self.birth_date = birth_date
        self.address = address
        self.password = password
        self.role = role
        self.phone_number = phone_number
        self.calendar = calendar
        self.cart = cart
        self.account_status = account_status

class UserSchema(ma.Schema):
    class Meta:
        fields = ('id', 'email', 'name', 'birth_date', 'address', 'password', 'role', 'phone_number', 'calendar', 'cart', 'account_status')

unregistered_user = User(None, None, None, None, None, 4, None, None, None, False)
        

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(DB_STRING_SHORT_MAX))
    category = db.Column(db.Integer, db.ForeignKey('category.id'))
    quantity = db.Column(db.Integer)
    seller = db.Column(db.Integer, db.ForeignKey('user.id'))
    price = db.Column(db.Integer)
    sell_type = db.Column(db.Integer)
    description = db.Column(db.String(DB_STRING_LONG_MAX))
    self_harvest = db.Column(db.Boolean) 
    begin_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    
    def __init__(self, name, category, quantity, seller, price, sell_type, description, self_harvest, begin_date, end_date):
        self.name = name
        self.category = category
        self.quantity = quantity
        self.seller = seller 
        self.price = price
        self.sell_type = sell_type
        self.description = description
        self.self_harvest = self_harvest
        self.begin_date = begin_date
        self.end_date = end_date
        
class ProductSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'category', 'quantity', 'seller', 'price', 'sell_type', 'description', 'self_harvest', 'begin_date', 'end_date')

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(DB_STRING_SHORT_MAX))
    higher_category = db.Column(db.Integer, db.ForeignKey('category.id'))
    leaf = db.Column(db.Boolean)
    
    def __init__(self, name, higher_category, leaf):
        self.name = name
        self.higher_category = higher_category
        self.leaf = leaf

class CategorySchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'higher_category', 'leaf')
        
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    buyer = db.Column(db.Integer, db.ForeignKey('user.id'))
    product_list = db.Column(MutableList.as_mutable(PickleType), default=[])
    quantity_list = db.Column(MutableList.as_mutable(PickleType), default=[])
    price = db.Column(db.Integer)
    date = db.Column(db.Date)
    status = db.Column(db.Integer)
    
    def __init__(self, buyer, product_list, quantity_list, price, date, status):
        self.buyer = buyer
        self.product_list = product_list
        self.quantity_list = quantity_list
        self.price = price
        self.date = date
        self.status = status

class OrderSchema(ma.Schema):
    class Meta:
        fields = ('id', 'buyer', 'product_list', 'quantity_list', 'price', 'date', 'status')

class CalendarRow(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.Integer, db.ForeignKey('user.id'))
    quantity = db.Column(db.Integer)
    
    def __init__(self, buyer, product, quantity, price, date, status):
        self.buyer = buyer
        self.product = product
        self.quantity = quantity
        self.price = price
        self.date = date
        self.status = status

class CalendarRowSchema(ma.Schema):
    class Meta:
        fields = ('id', 'buyer', 'product', 'quantity', 'price', 'date', 'status')

class CategorySuggestion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(DB_STRING_SHORT_MAX))
    higher_category = db.Column(db.Integer, db.ForeignKey('category.id'))
    leaf = db.Column(db.Boolean)
    description = db.Column(db.String(DB_STRING_LONG_MAX))
    status = db.Column(db.Integer)
    suggester = db.Column(db.Integer, db.ForeignKey('user.id'))
    approver = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    def __init__(self, name, higher_category, leaf, description, status, suggester, approver):
        self.name = name
        self.higher_category = higher_category
        self.leaf = leaf
        self.description = description
        self.status = status
        self.suggester = suggester
        self.approver = approver

class CategorySuggestionSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'higher_category', 'leaf', 'description', 'status', 'suggester', 'approver')

class ProductReview(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    reviewer_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    text = db.Column(db.String(DB_STRING_LONG_MAX))
    evaluation = db.Column(db.Integer)

    def __init__(self, product_id, reviewer_id, text, evaluation):
        self.product_id = product_id
        self.reviewer_id = reviewer_id
        self.text = text
        self.evaluation = evaluation

class ProductReviewSchema(ma.Schema):
    class Meta:
        fields = ('id', 'product_id', 'reviewer_id', 'text', 'evaluation')


# Create database
def create_db():
    app.app_context().push()
    db.drop_all()
    db.create_all()

    # create root category
    db.session.add(Category('root', None, False))
    root = getCategoryByName('root')
    
    db.session.add(Category('Fruits', root['id'], False))
    db.session.add(Category('Vegetables', root['id'], False))
    db.session.commit()
    
    db.session.add(Category('Apple', getCategoryByName('Fruits')['id'], False))
    db.session.add(Category('Orange', getCategoryByName('Fruits')['id'], True))
    db.session.add(Category('Tomato', getCategoryByName('Vegetables')['id'], False))
    db.session.add(Category('Potato', getCategoryByName('Vegetables')['id'], False))
    db.session.add(Category('Cucumber', getCategoryByName('Vegetables')['id'], True))
    db.session.add(Category('Carrot', getCategoryByName('Vegetables')['id'], True))
    db.session.add(Category('Onion', getCategoryByName('Vegetables')['id'], False))
    db.session.add(Category('Garlic', getCategoryByName('Vegetables')['id'], True))
    db.session.add(Category('Lettuce', getCategoryByName('Vegetables')['id'], True))
    db.session.add(Category('Cabbage', getCategoryByName('Vegetables')['id'], False))
    db.session.add(Category('Grapes', getCategoryByName('Fruits')['id'], False))
    db.session.add(Category('Peach', getCategoryByName('Fruits')['id'], True))
    db.session.add(Category('Pear', getCategoryByName('Fruits')['id'], True))
    db.session.commit()
    
    db.session.add(Category('Red Apple', getCategoryByName('Apple')['id'], True))
    db.session.add(Category('Green Apple', getCategoryByName('Apple')['id'], True))
    db.session.add(Category('Yellow Apple', getCategoryByName('Apple')['id'], True))
    db.session.add(Category('Red Tomato', getCategoryByName('Tomato')['id'], True))
    db.session.add(Category('Yellow Tomato', getCategoryByName('Tomato')['id'], True))
    db.session.add(Category('Cherry Tomato', getCategoryByName('Tomato')['id'], True))
    db.session.add(Category('Red Potato', getCategoryByName('Potato')['id'], True))
    db.session.add(Category('White Potato', getCategoryByName('Potato')['id'], True))
    db.session.add(Category('White Onion', getCategoryByName('Onion')['id'], True))
    db.session.add(Category('Red Onion', getCategoryByName('Onion')['id'], True))
    db.session.add(Category('White Cabbage', getCategoryByName('Cabbage')['id'], True))
    db.session.add(Category('Red Cabbage', getCategoryByName('Cabbage')['id'], True))
    db.session.add(Category('White Grapes', getCategoryByName('Grapes')['id'], True))
    db.session.add(Category('Red Grapes', getCategoryByName('Grapes')['id'], True))
    db.session.commit()

    # add template users for show
    db.session.add(User('admin', 'RGB', '1995-1-1', '7th Street', 'admin', 0, 905240384, [], [], True))
    db.session.add(User('mod', 'RGB', '1995-1-1', '7th Street', 'mod', 1, 905240384, [], [], True))
    db.session.add(User('farmer', 'Frank Green', '1995-1-1', '7th Street', 'farmer', 2, 905240384, [], [], True))
    db.session.add(User('farmer2', 'Jim Helper', '1995-1-1', '7th Street', 'farmer2', 2, 905240384, [], [], True))
    db.session.add(User('farmer3', 'Joe Mama', '1995-1-1', '7th Street', 'farmer3', 2, 905240384, [], [], True))
    db.session.add(User('user', 'RGB', '1995-1-1', '7th Street', 'user', 3, 905240384, [], [], True))
    db.session.commit()

    # dummy data
    veggies = getCategoryByName('Vegetables')
    db.session.add(Category('Tomatoes', veggies['id'], False))
    toms = getCategoryByName('Tomatoes')
    db.session.add(Category('Pickles', veggies['id'], True))
    picks = getCategoryByName('Pickles')

    db.session.add(Category('Normal Tomatoes', toms['id'], True))
    norm_toms = getCategoryByName('Normal Tomatoes')

    user = getUserByEmail('farmer')
    db.session.add(Product('Tomato', norm_toms['id'], 100, user['id'], 50, 0, 'the great red tomato', None, None, None))
    db.session.add(Product('Blue Tomato', norm_toms['id'], 100, user['id'], 500, 0, 'the great blue tomato from 8428713 dimension', None, None, None))
    db.session.add(Product('Pickle', picks['id'], 690, user['id'], 40, 0, 'pickle rick', True, '2022-1-1', '2022-6-1'))
    db.session.commit()
    
    db.session.add(Product('Franks Golden Apple', getCategoryByName('Green Apple')['id'], 500, getUserByEmail('farmer')['id'], 10, 0, "Best apple ever", False, None, None))
    db.session.add(Product('Jims Green Apple', getCategoryByName('Green Apple')['id'], 200, getUserByEmail('farmer2')['id'], 5, 1, "Best apple ever", False, None, None))
    db.session.add(Product('Joes Golden Apple', getCategoryByName('Green Apple')['id'], 100, getUserByEmail('farmer3')['id'], 2, 1, "Best apple ever", False, None, None))
    db.session.add(Product('Golden Apple', getCategoryByName('Green Apple')['id'], 3300, getUserByEmail('farmer')['id'], 7, 0, "Best apple ever", True, '2022-12-12', '2022-12-20'))
    db.session.add(Product('Franks Red Apple', getCategoryByName('Red Apple')['id'], 500, getUserByEmail('farmer')['id'], 10, 0, "Best apple ever", False , None, None))
    db.session.add(Product('Franks Yellow Apple', getCategoryByName('Yellow Apple')['id'], 500, getUserByEmail('farmer')['id'], 10, 0, "Best apple ever", False, None, None))
    db.session.add(Product('Franks Red Tomato', getCategoryByName('Red Tomato')['id'], 500, getUserByEmail('farmer')['id'], 10, 0, "Best tomato ever", False, None, None))
    db.session.add(Product('Franks Yellow Tomato', getCategoryByName('Yellow Tomato')['id'], 500, getUserByEmail('farmer')['id'], 10, 0, "Best tomato ever", False, None, None))
    db.session.add(Product('Jims Cherry Tomato', getCategoryByName('Cherry Tomato')['id'], 500, getUserByEmail('farmer2')['id'], 10, 0, "Best tomato ever", False, None, None))
    db.session.add(Product('Jims Red Potato', getCategoryByName('Red Potato')['id'], 500, getUserByEmail('farmer2')['id'], 10, 0, "Best potato ever", False, None, None))
    db.session.add(Product('Jims White Potato', getCategoryByName('White Potato')['id'], 500, getUserByEmail('farmer2')['id'], 10, 0, "Best potato ever", False, None, None))
    db.session.add(Product('Jims White Onion', getCategoryByName('White Onion')['id'], 500, getUserByEmail('farmer2')['id'], 10, 0, "Best onion ever", False, None, None))
    db.session.add(Product('Jims Red Onion', getCategoryByName('Red Onion')['id'], 500, getUserByEmail('farmer2')['id'], 10, 0, "Best onion ever", False, None, None))
    db.session.add(Product('Joes White Cabbage', getCategoryByName('White Cabbage')['id'], 500, getUserByEmail('farmer3')['id'], 10, 0, "Best cabbage ever", False, None, None))
    db.session.add(Product('Joes Red Cabbage', getCategoryByName('Red Cabbage')['id'], 500, getUserByEmail('farmer3')['id'], 10, 0, "Best cabbage ever", False, None, None))
    db.session.add(Product('Joes White Grapes', getCategoryByName('White Grapes')['id'], 500, getUserByEmail('farmer3')['id'], 10, 0, "Best grapes ever", False, None, None))
    db.session.add(Product('Joes Red Grapes', getCategoryByName('Red Grapes')['id'], 500, getUserByEmail('farmer3')['id'], 10, 0, "Best grapes ever", False, None, None))
    db.session.commit()

#
##  Checkers
#
#   most of them: 
#   returning boolean value if <<x>> exists/is found or not

def isCategoryName(name):
    ctgs = getCategories()
    for cat in ctgs:
        if cat['name'] == name:
            return True
    return False

def isCategoryID(id):
    ctgs = getCategories()
    for cat in ctgs:
        if cat['id'] == id:
            return True
    return False

def isUserEmail(email):
    users_list = getUsers()
    for user in users_list:
        if user['email'] == email:
            return True
    return False

def isUserID(id):
    users_list = getUsers()
    for user in users_list:
        if user['id'] == id:
            return True
    return False

def isOrder(id):
    list = getOrders()
    for x in list:
        if x['id'] == id:
            return True
    return False

def isProduct(id):
    list = getProducts()
    for x in list:
        if x['id'] == id:
            return True
    return False

def isSellingProduct(product_id, seller_id):
    list = getProducts()
    for x in list:
        if x['id'] == product_id and x['seller'] == seller_id:
            return True
    return False

#
##  Getters
#

#
# Get "single row" (default search is by ID)
# returns: dict of <<x>> (see:XSchema) or None
def getUser(id):
    list = getUsers()
    for x in list:
        if x['id'] == id:
            return x
    return None

def getUserByEmail(email):
    list = getUsers()
    for x in list:
        if x['email'] == email:
            return x
    return None

def getUsersByRole(role, includeDeleted=False):
    list = getUsers()
    result = []
    for x in list:
        if x['role'] == role:
            if (includeDeleted == False and x['account_status'] == False):
                continue
            result.append(x)
    return result

def getCategory(id):
    list = getCategories(False)
    for x in list:
        if x['id'] == id:
            return x
    return None

def getCategoryByName(name):
    list = getCategories(False)
    for x in list:
        if x['name'].lower() == name.lower():
            return x
    return None

def getOrder(id):
    list = getOrders()
    for x in list:
        if x['id'] == id:
            return x
    return None

def getProduct(id):
    list = getProducts()
    for x in list:
        if x['id'] == id:
            return x
    return None

def getProductByName(name, category_id, seller_id):
    list = getProducts()
    for x in list:
        if x['name'] == name and x['category'] == category_id and x['seller'] == seller_id:
            return x
    return None

def getProductByNameOnly(name):
    list = getProducts()
    for x in list:
        if x['name'] == name:
            return x
    return None

def getProductsBySeller(seller_id):
    list = getProducts()
    result = []
    for x in list:
        if x['seller'] == seller_id:
            result.append(x)
    return result

def getCategorySuggestion(id):
    list = getCategorySuggestions()
    for x in list:
        if x['id'] == id:
            return x
    return None

def getCategoryNames():
    list = getCategories(True)
    result = []
    for x in list:
        result.append(x['name'])
    return result

def getProductReview(id):
    list = getProductReviews()
    for x in list:
        if x['id'] == id:
            return x
    return None

def getReviewsOfOrder(order_id):
    list = getProductReviews()
    result = []
    for x in list:
        if x['order_id'] == order_id:
            result.append(x)
    return result

def getReviewsOfProduct(product_id):
    list = getProductReviews()
    result = []
    for x in list:
        if x['product_id'] == product_id:
            result.append(x)
    return result

#
# Get everything
# returns: list of <<x>> (See: XSchema)
def getUsers():
    users = User.query.all()
    users_schema = UserSchema(many=True)
    return users_schema.dump(users)

def getCategories(no_root=True):
    if not no_root:
        categories = Category.query.all()
    else:
        categories = Category.query.filter(Category.id != '1').all()
    category_schema = CategorySchema(many=True)
    return category_schema.dump(categories)

def getSubCategories(id):
    subCategories = Category.query.filter(Category.higher_category == id ).all()
    subCategories_schema = CategorySchema(many=True)
    return subCategories_schema.dump(subCategories)

def getProductsByCategory(id):
    products = Product.query.filter(Product.category == id).all()
    if not products:
        return []
    products_schema = ProductSchema(many=True)
    return products_schema.dump(products)

def getOrders():
    orders = Order.query.all()
    orders_schema = OrderSchema(many=True)
    return orders_schema.dump(orders)

def getProducts():
    products = Product.query.all()
    products_schema = ProductSchema(many=True)
    return products_schema.dump(products)

def getCategorySuggestions():
    suggestions = CategorySuggestion.query.all()
    suggestions_schema = CategorySuggestionSchema(many=True)
    return suggestions_schema.dump(suggestions)

def getProductReviews():
    reviews = ProductReview.query.all()
    reviews_schema = ProductReviewSchema(many=True)
    return reviews_schema.dump(reviews)

#
##  Adders
#

# returns: 0 OK; 1 too long string; 2 user exists
# TODO: co je povinny udaj a co ne ? [pripsat sem jako parametr]
def addUser(email, name, password, role):
    if len(name) > DB_STRING_SHORT_MAX or len(password) > DB_STRING_SHORT_MAX:
        return 1
    if isUserEmail(email):
        return 2
    db.session.add(User(email, name, None, None, password, role, None, [], [], True))
    db.session.commit()
    return 0

# returns: 0 OK; 1 too long name; 2 category exists  
def addCategory(name, higher_category=None, leaf=False):
    if len(name) > DB_STRING_SHORT_MAX:
        return 1
    if isCategoryName(name):
        return 2
    db.session.add(Category(name, higher_category, leaf))
    db.session.commit()
    return 0

# returns: 0 OK; 1 buyer id invalid
def addOrder(buyer_id, product_id_list, quantity_list, total_price, date=None, status=None):
    if not isUserID(buyer_id):
        return 1
    db.session.add(Order(buyer_id, product_id_list, quantity_list, total_price, date, status))
    db.session.commit()
    return 0

# returns: 0 OK; 1 too long string; 2 product (same name + category + seller) exists; 3 invalid price
def addProduct(name, category, seller, price):
    if len(name) > DB_STRING_SHORT_MAX:
        return 1
    if isSellingProduct(name, category, seller):
        return 2
    if price < 0:
        return 3

    db.session.add(Product(name, category, None, seller, price, None, None, None, None, None))
    db.session.commit()
    return 0   

# returns: 0 OK; 1 too long string; 2 invalid higher category (ID);
def addCategorySuggestion(category_name, higher_category, leaf, description, suggester_id):
    if len(category_name) > DB_STRING_SHORT_MAX:
        return 1
    if not isCategoryID(higher_category):
        return 2

    db.session.add(CategorySuggestion(category_name, higher_category, leaf, description, 0, suggester_id, None))
    db.session.commit()
    return 0

# returns: 0 OK; 1 too long string; 2 invalid reviewer; 3 invalid product; 
def addProductReview(product_id, reviewer_id, text="", evaluation=5):
    if len(text) > DB_STRING_LONG_MAX:
        return 1
    if not isUserID(reviewer_id):
        return 2
    if not isProduct(product_id):
        return 3

    db.session.add(ProductReview(product_id, reviewer_id, text, evaluation))
    db.session.commit()
    return 0

#
##  Removers
#

# deletes element/table from database [without checking any dependencies aka PK, FK, ...]
# returns: None when ok; Description (exception) string on error
def removeData(Class, element_ID):
    removal = db.session.get(Class, element_ID)
    if (Class == Category):
        # check for subcategories
        sub = backend.getSubCategories(element_ID)
        if (len(sub) != 0):
            for subcat in sub:
                removeData(Category, subcat['id'])
        
        # if no subcategories, check for products
        prods = backend.getCategoryProducts(element_ID)
        if (len(prods) != 0):
            for product in prods:
                removeData(Product, product['id'])
    try:
        db.session.delete(removal)
        db.session.commit()
    except Exception as e:
        return str(e)
    return None

#
##  Setters
#

# modify single row in any class - for key see XSchema, for Class see Classes in database.py
# note: editing any ID will result in 'strelba do kolene'
# returns: None when success; Description (exception) string on error
def modifyData(Class, element_ID, key, value):
    element = None
    try:
        element = db.session.query(Class).filter(Class.id == element_ID)
    except Exception as e:
        return str(e)
    try:
        element.update({key:value}, synchronize_session=False)
    except Exception as e:
        return str(e)

    db.session.commit()
    return None
