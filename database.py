###
#   module:     database.py   
#   Database module
###
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask import request
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy import PickleType

import globals

app = globals.app
db = SQLAlchemy(app)
ma = Marshmallow(app)

DB_STRING_SHORT_MAX = 150       # maximum characters for short strings  (name, e-mail, password)
DB_STRING_LONG_MAX = 500        # maximum characters for long strings   (address, description)
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

    def __init__(self, email, name, birth_date, address, password, role, phone_number, calendar):
        self.email = email
        self.name = name
        self.birth_date = birth_date
        self.address = address
        self.password = password
        self.role = role
        self.phone_number = phone_number
        self.calendar = calendar

class UserSchema(ma.Schema):
    class Meta:
        fields = ('id', 'email', 'name', 'birth_date', 'address', 'password', 'role', 'phone_number', 'calendar')

unregistered_user = User(None, None, None, None, None, 4, None, None)
        

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
    product = db.Column(db.Integer, db.ForeignKey('product.id'))
    quantity = db.Column(db.Integer)
    price = db.Column(db.Integer)
    date = db.Column(db.Date)
    status = db.Column(db.Integer)
    
    def __init__(self, buyer, product, quantity, price, date, status):
        self.buyer = buyer
        self.product = product
        self.quantity = quantity
        self.price = price
        self.date = date
        self.status = status

class OrderSchema(ma.Schema):
    class Meta:
        fields = ('id', 'buyer', 'product', 'quantity', 'price', 'date', 'status')

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

# Create database
def create_db():
    app.app_context().push()
    db.drop_all()
    db.create_all()

    # create root category
    db.session.add(Category('root', None, False))
    root = getCategoryByName('root')
    
    db.session.add(Category('Fruit', root['id'], False))
    db.session.add(Category('Vegetables', root['id'], False))
    db.session.commit()

    # add template users for show
    db.session.add(User('admin', 'RGB', '1995-1-1', '7th Street', 'admin', 0, 905240384, []))
    db.session.add(User('mod', 'RGB', '1995-1-1', '7th Street', 'mod', 1, 905240384, []))
    db.session.add(User('farmer', 'RGB', '1995-1-1', '7th Street', 'farmer', 2, 905240384, []))
    db.session.add(User('user', 'RGB', '1995-1-1', '7th Street', 'user', 3, 905240384, []))
    db.session.commit()

    # dummy data
    veggies = getCategoryByName('Vegetables')
    user = getUserByEmail('farmer')
    db.session.add(Product('Tomato', veggies['id'], 100, user['id'], 50, 0, 'the great red tomato', None, None, None))
    db.session.add(Product('Pickle', veggies['id'], 690, user['id'], 40, 0, 'pickle rick', True, '2022-1-1', '2022-6-1'))
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

def getCategory(id):
    list = getCategories()
    for x in list:
        if x['id'] == id:
            return x
    return None

def getCategoryByName(name):
    list = getCategories()
    for x in list:
        if x['name'] == name:
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

#
# Get everything
# returns: list of <<x>> (See: XSchema)
def getUsers():
    users = User.query.all()
    users_schema = UserSchema(many=True)
    return users_schema.dump(users)

def getCategories():
    categories = Category.query.all()
    category_schema = CategorySchema(many=True)
    return category_schema.dump(categories)

def getOrders():
    orders = Order.query.all()
    orders_schema = OrderSchema(many=True)
    return orders_schema.dump(orders)

def getProducts():
    products = Product.query.all()
    products_schema = ProductSchema(many=True)
    return products_schema.dump(products)


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
    db.session.add(User(email, name, None, None, password, role, None, []))
    db.session.commit()
    return 0

# returns: 0 OK; 1 too long name; 2 category exists  
def addCategory(name):
    if len(name) > DB_STRING_SHORT_MAX:
        return 1
    if isCategoryName(name):
        return 2
    db.session.add(Category(name, None, False))
    db.session.commit()
    return 0

# returns: 0 OK; 1 buyer id invalid; 2 product id invalid; 3 quantity invalid; 4 price invalid
def addOrder(buyer_id, product_id, quantity, price):
    if not isUserID(buyer_id):
        return 1
    if not isProduct(product_id):
        return 2
    if quantity < 0:
        return 3
    if price < 0:
        return 4

    db.session.add(Order(buyer_id, product_id, quantity, price, None, None))
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

#
##  Removers
#

# deletes element/table from database [without checking any dependencies aka PK, FK, ...]
# returns: None when ok; Description (exception) string on error
def removeData(Class, element_ID):
    removal = db.session.get(Class, element_ID)
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
