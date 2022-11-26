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
    active = db.Column(db.Boolean)
    
    def __init__(self, name, category, quantity, seller, price, sell_type, description, self_harvest, begin_date, end_date, active):
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
        self.active = active
        
class ProductSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'category', 'quantity', 'seller', 'price', 'sell_type', 'description', 'self_harvest', 'begin_date', 'end_date', 'active')

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
    
    #Fruits
    db.session.add(Category('Apple', getCategoryByName('Fruits')['id'], False))
    db.session.add(Category('Citrus', getCategoryByName('Fruits')['id'], False))
    db.session.add(Category('Berries', getCategoryByName('Fruits')['id'], False))
    db.session.add(Category('Melon', getCategoryByName('Fruits')['id'], False))
    db.session.add(Category('Grapes', getCategoryByName('Fruits')['id'], False))
    db.session.add(Category('Pear', getCategoryByName('Fruits')['id'], True))
    db.session.add(Category('Banana', getCategoryByName('Fruits')['id'], True))
    db.session.add(Category('Cherry', getCategoryByName('Fruits')['id'], True))
    db.session.add(Category('Pineapple', getCategoryByName('Fruits')['id'], True))
    db.session.add(Category('Peach', getCategoryByName('Fruits')['id'], True))
    #db.session.add(Category('Pomegranate', getCategoryByName('Fruit')['id'], True))
    db.session.add(Category('Mango', getCategoryByName('Fruits')['id'], True))
    db.session.add(Category('Kiwi', getCategoryByName('Fruits')['id'], True))
    db.session.commit()
    
    #Melon subcategories
    db.session.add(Category('Red Watermelon', getCategoryByName('Melon')['id'], True))
    db.session.add(Category('Yellow Melon', getCategoryByName('Melon')['id'], True))
    
    #Berries subcategories
    db.session.add(Category('Raspberry', getCategoryByName('Berries')['id'], True))
    db.session.add(Category('Blueberry', getCategoryByName('Berries')['id'], True))
    db.session.add(Category('Blackberry', getCategoryByName('Berries')['id'], True))
    db.session.add(Category('Cranberry', getCategoryByName('Berries')['id'], True))
    db.session.add(Category('Strawberry', getCategoryByName('Berries')['id'], True))
    
    #Citrus subcategories
    db.session.add(Category('Orange', getCategoryByName('Citrus')['id'], True))  
    db.session.add(Category('Tangerine', getCategoryByName('Citrus')['id'], True))
    db.session.add(Category('Lemon', getCategoryByName('Citrus')['id'], True))
    db.session.add(Category('Lime', getCategoryByName('Citrus')['id'], True))
    db.session.add(Category('Grapefruit', getCategoryByName('Citrus')['id'], True))
    db.session.add(Category('Pomelo', getCategoryByName('Citrus')['id'], True))
    
    #Apple subcategories
    db.session.add(Category('Red Apple', getCategoryByName('Apple')['id'], True))
    db.session.add(Category('Green Apple', getCategoryByName('Apple')['id'], True))
    db.session.add(Category('Yellow Apple', getCategoryByName('Apple')['id'], True))
    
    #Grapes subcategories
    db.session.add(Category('White Grapes', getCategoryByName('Grapes')['id'], True))
    db.session.add(Category('Red Grapes', getCategoryByName('Grapes')['id'], True))
    db.session.commit()
    
    #Vegetables
    db.session.add(Category('Tomato', getCategoryByName('Vegetables')['id'], False))
    db.session.add(Category('Potato', getCategoryByName('Vegetables')['id'], False))
    db.session.add(Category('Cabbage', getCategoryByName('Vegetables')['id'], False))
    db.session.add(Category('Onion', getCategoryByName('Vegetables')['id'], False))
    db.session.add(Category('Cucumber', getCategoryByName('Vegetables')['id'], False))
    db.session.add(Category('Carrot', getCategoryByName('Vegetables')['id'], False))
    db.session.add(Category('Garlic', getCategoryByName('Vegetables')['id'], False))
    db.session.add(Category('Mushroom', getCategoryByName('Vegetables')['id'], False))
    db.session.add(Category('Pepper', getCategoryByName('Vegetables')['id'], False))
    db.session.add(Category('Corn', getCategoryByName('Vegetables')['id'], False))
    db.session.add(Category('Pumpkin', getCategoryByName('Vegetables')['id'], False))
    db.session.add(Category('Radish', getCategoryByName('Vegetables')['id'], False))
    db.session.add(Category('Beans', getCategoryByName('Vegetables')['id'], False))      
    db.session.add(Category('Lettuce', getCategoryByName('Vegetables')['id'], True))
    db.session.add(Category('Brocolli', getCategoryByName('Vegetables')['id'], True))
    db.session.add(Category('Spinach', getCategoryByName('Vegetables')['id'], True))
    db.session.add(Category('Eggplant', getCategoryByName('Vegetables')['id'], True))
    db.session.add(Category('Zuchini', getCategoryByName('Vegetables')['id'], True))
    db.session.add(Category('Cauliflower', getCategoryByName('Vegetables')['id'], True))
    db.session.add(Category('Celery', getCategoryByName('Vegetables')['id'], True))
    db.session.add(Category('Asparagus', getCategoryByName('Vegetables')['id'], True))
    db.session.add(Category('Beet', getCategoryByName('Vegetables')['id'], True)) 

    db.session.commit()
    
    #Beans subcategories
    db.session.add(Category('Green Bean', getCategoryByName('Beans')['id'], True))
    db.session.add(Category('Black Bean', getCategoryByName('Beans')['id'], True))
    db.session.add(Category('Lentil', getCategoryByName('Beans')['id'], True))
    db.session.add(Category('SoyBean', getCategoryByName('Beans')['id'], True))
    db.session.add(Category('Peas', getCategoryByName('Beans')['id'], True))

    #Radish subcategories
    db.session.add(Category('Red Radish', getCategoryByName('Radish')['id'], True))
    db.session.add(Category('White Radish', getCategoryByName('Radish')['id'], True))
    
    #Pumpkin subcategories
    db.session.add(Category('Jack O Lantern', getCategoryByName('Pumpkin')['id'], True))
    db.session.add(Category('Sweet Pumpkin', getCategoryByName('Pumpkin')['id'], True))
    db.session.add(Category('Hokkaido Pumpkin', getCategoryByName('Pumpkin')['id'], True))
    
    #Corn subcategories
    db.session.add(Category('Sweet Corn', getCategoryByName('Corn')['id'], True))
    db.session.add(Category('Dent Corn', getCategoryByName('Corn')['id'], True))
 
    #Pepper subcategories
    db.session.add(Category('Red Pepper', getCategoryByName('Pepper')['id'], True))
    db.session.add(Category('Green Pepper', getCategoryByName('Pepper')['id'], True))
    db.session.add(Category('Yellow Pepper', getCategoryByName('Pepper')['id'], True))
    db.session.add(Category('Orange Pepper', getCategoryByName('Pepper')['id'], True))
    db.session.add(Category('Chilli Pepper', getCategoryByName('Pepper')['id'], False))
    
    #Chilli Pepper subcategories
    db.session.add(Category('Red Chili Pepper', getCategoryByName('Chilli Pepper')['id'], True))
    db.session.add(Category('Green Chili Pepper', getCategoryByName('Chilli Pepper')['id'], True))
    db.session.add(Category('Jalapeno Pepper', getCategoryByName('Chilli Pepper')['id'], True))
    db.session.add(Category('Habanero Pepper', getCategoryByName('Chilli Pepper')['id'], True))
    db.session.add(Category('Cayenne Pepper', getCategoryByName('Chilli Pepper')['id'], True))
    
    #Mushroom subcategories
    db.session.add(Category('Champignon Mushroom', getCategoryByName('Mushroom')['id'], True))
    db.session.add(Category('Portobello Mushroom', getCategoryByName('Mushroom')['id'], True))
    db.session.add(Category('Oyster Mushroom', getCategoryByName('Mushroom')['id'], True))
    db.session.add(Category('Shiitake Mushroom', getCategoryByName('Mushroom')['id'], True))

    #Garlic subcategories
    db.session.add(Category('White Garlic', getCategoryByName('Garlic')['id'], True))
    db.session.add(Category('Red Garlic', getCategoryByName('Garlic')['id'], True))
    
    #Carrot subcategories
    db.session.add(Category('Baby Carrot', getCategoryByName('Carrot')['id'], True))
    db.session.add(Category('Regular Carrot', getCategoryByName('Carrot')['id'], True))
    
    #Cucumber subcategories
    db.session.add(Category('Salad Cucumber', getCategoryByName('Cucumber')['id'], True))
    db.session.add(Category('Pickling Cucumber', getCategoryByName('Cucumber')['id'], True))
    db.session.add(Category('Garden Cucumber', getCategoryByName('Cucumber')['id'], True))
    
    #Tomato subcategories
    db.session.add(Category('Red Tomato', getCategoryByName('Tomato')['id'], True))
    db.session.add(Category('Yellow Tomato', getCategoryByName('Tomato')['id'], True))
    db.session.add(Category('Cherry Tomato', getCategoryByName('Tomato')['id'], True))
    
    #Potato subcategories
    db.session.add(Category('Red Potato', getCategoryByName('Potato')['id'], True))
    db.session.add(Category('White Potato', getCategoryByName('Potato')['id'], True))
    db.session.add(Category('Sweet Potato', getCategoryByName('Potato')['id'], True))
    
    #Onion subcategories
    db.session.add(Category('White Onion', getCategoryByName('Onion')['id'], True))
    db.session.add(Category('Red Onion', getCategoryByName('Onion')['id'], True))
    
    #Cabbage subcategories
    db.session.add(Category('White Cabbage', getCategoryByName('Cabbage')['id'], True))
    db.session.add(Category('Red Cabbage', getCategoryByName('Cabbage')['id'], True))
    db.session.commit()

    # add template users for show
    db.session.add(User('admin', 'RGB', '1995-1-1', '7th Street', 'admin', 0, 905240384, [], [], True))
    db.session.add(User('mod', 'RGB', '1995-1-1', '7th Street', 'mod', 1, 905240384, [], [], True))
    db.session.add(User('farmer', 'Frank Green', '1995-1-1', '7th Street', 'farmer', 2, 905240384, [], [], True))
    db.session.add(User('user', 'RGB', '1995-1-1', '7th Street', 'user', 3, 905240384, [], [], True))
    
    db.session.add(User('jhelper@gmail.com', 'Jim Helper', '1995-2-1', '7th Street', 'farmer2', 2, 905240384, [], [], True))
    db.session.add(User('bigmama69@gmail.com', 'Joe Mama', '1969-5-21', 'Red Light Street 21', 'farmer3', 2, 905253384, [], [], True))
    db.session.add(User('smith112@gmail.com', 'John Smith', '1978-6-4', 'Lincoln Street', 'farmer4', 2, 905247434, [], [], True))
    db.session.add(User('acook@gmail.com', 'Alice Cook', '1999-10-4', '7th Street', 'farmer5', 2, 950010384, [], [], True))
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
    user1 = getUserByEmail('jhelper@gmail.com')
    user2 = getUserByEmail('bigmama69@gmail.com')
    user3 = getUserByEmail('smith112@gmail.com')
    user4 = getUserByEmail('acook@gmail.com')
    
    #Pear Products
    db.session.add(Product('Franks Pear', getCategoryByName('Pear')['id'], 100, user['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Joes Pear', getCategoryByName('Pear')['id'], 100, user2['id'], 3, 1, "Best ever", False, None, None, True))
    
    #Banana Products
    db.session.add(Product('Jims Banana', getCategoryByName('Banana')['id'], 100, user1['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Special Banana', getCategoryByName('Banana')['id'], 100, user3['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Big Banana', getCategoryByName('Banana')['id'], 100, user2['id'], 3, 1, "Best ever", False, None, None, True))
    
    #Cherry Products
    db.session.add(Product('Morello Cherry', getCategoryByName('Cherry')['id'], 100, user4['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Quenn Ann Cherry', getCategoryByName('Cherry')['id'], 100, user3['id'], 3, 1, "Best ever", False, None, None, True))
    
    #Pineapple Products
    db.session.add(Product('Queen Pineapple', getCategoryByName('Pineapple')['id'], 100, user['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Jims Pineapple', getCategoryByName('Pineapple')['id'], 100, user1['id'], 3, 1, "Best ever", False, None, None, True))
    
    #Peach Products
    db.session.add(Product('Donut Peach', getCategoryByName('Peach')['id'], 100, user2['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Yellow Peach', getCategoryByName('Peach')['id'], 100, user1['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('White Peach', getCategoryByName('Peach')['id'], 100, user4['id'], 3, 1, "Best ever", False, None, None, True))
    
    #Pomegranate Products
    #db.session.add(Product('Eversweet Pomegranate', getCategoryByName('Pomegranate')['id'], 100, user3['id'], 3, 1, "Best ever", False, None, None, True))
    #db.session.add(Product('Red Silk Pomegranate', getCategoryByName('Pomegranate')['id'], 100, user2['id'], 3, 1, "Best ever", False, None, None, True))
    #db.session.add(Product('Purple Heart Pomegranate', getCategoryByName('Pomegranate')['id'], 100, user['id'], 3, 1, "Best ever", False, None, None, True))
    
    #Mango Products
    db.session.add(Product('Alphonso Mango', getCategoryByName('Mango')['id'], 100, user4['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Kent Mango', getCategoryByName('Mango')['id'], 100, user3['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Dasher Mango', getCategoryByName('Mango')['id'], 100, user2['id'], 3, 1, "Best ever", False, None, None, True))

    #Kiwi Products
    db.session.add(Product('Jims Kiwi', getCategoryByName('Kiwi')['id'], 100, user1['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Alices Kiwi', getCategoryByName('Kiwi')['id'], 100, user4['id'], 3, 1, "Best ever", False, None, None, True))
    
    #Red Watermelon Products
    db.session.add(Product('Sultan Watermelon', getCategoryByName('Red Watermelon')['id'], 100, user3['id'], 3, 1, "Best ever", False, None, None, True))
    
    #Yellow Watermelon Products
    db.session.add(Product('Yellow Crimson Watermelon', getCategoryByName('Yellow Melon')['id'], 100, user1['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Yellow Sugar Baby', getCategoryByName('Yellow Melon')['id'], 100, user2['id'], 3, 1, "Best ever", False, None, None, True))
    
    #Raspberry Products
    db.session.add(Product('Royalty Raspberry', getCategoryByName('Raspberry')['id'], 100, user1['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Fall Gold Raspberry', getCategoryByName('Raspberry')['id'], 100, user4['id'], 3, 1, "Best ever", False, None, None, True))
    
    #Blueberry Products
    db.session.add(Product('Jims Blueberry', getCategoryByName('Blueberry')['id'], 100, user1['id'], 3, 1, "Best ever", False, None, None, True))
    
    #Strawberry Products
    db.session.add(Product('Pineberry', getCategoryByName('Strawberry')['id'], 100, user1['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Joes Strawberry', getCategoryByName('Strawberry')['id'], 100, user2['id'], 3, 1, "Best ever", False, None, None, True))
    
    #Blackberry Products
    db.session.add(Product('Arapaho', getCategoryByName('Blackberry')['id'], 100, user3['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Kiowa Blackberry', getCategoryByName('Blackberry')['id'], 100, user1['id'], 3, 1, "Best ever", False, None, None, True))
    
    #Cranberry Products
    db.session.add(Product('Nicolaus Cranberry', getCategoryByName('Cranberry')['id'], 100, user['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Early Black Cranberry', getCategoryByName('Cranberry')['id'], 100, user1['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Scarlet Knight', getCategoryByName('Blackberry')['id'], 100, user3['id'], 3, 1, "Best ever", False, None, None, True))
    
    #Orange Products
    db.session.add(Product('Valencia Orange', getCategoryByName('Orange')['id'], 100, user['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Navel Orange', getCategoryByName('Orange')['id'], 100, user1['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Blood Orange', getCategoryByName('Orange')['id'], 100, user2['id'], 3, 1, "Best ever", False, None, None, True))
    
    #Lemon Products
    db.session.add(Product('Eureka Lemon', getCategoryByName('Lemon')['id'], 100, user3['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Lisbon Lemon', getCategoryByName('Lemon')['id'], 100, user4['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Avalon Lemon', getCategoryByName('Lemon')['id'], 100, user['id'], 3, 1, "Best ever", False, None, None, True))
    
    #Lime Products
    db.session.add(Product('Key Lime', getCategoryByName('Lime')['id'], 100, user1['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Persian Lime', getCategoryByName('Lime')['id'], 100, user2['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Australian Finger', getCategoryByName('Lime')['id'], 100, user4['id'], 3, 1, "Best ever", False, None, None, True))
    
    #Tangerine Products
    db.session.add(Product('Mandarin', getCategoryByName('Tangerine')['id'], 100, user3['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Satsuma', getCategoryByName('Tangerine')['id'], 100, user['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Clementines', getCategoryByName('Tangerine')['id'], 100, user4['id'], 3, 1, "Best ever", False, None, None, True))
    
    #Pomelo Products
    db.session.add(Product('Alices Pomelo', getCategoryByName('Pomelo')['id'], 100, user4['id'], 3, 1, "Best ever", False, None, None, True))
    
    #Grapefruit Products
    db.session.add(Product('Ruby Red Grapefruit', getCategoryByName('Grapefruit')['id'], 100, user3['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('White Grapefruit', getCategoryByName('Grapefruit')['id'], 100, user1['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Pink Grapefruit', getCategoryByName('Grapefruit')['id'], 100, user2['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Oro Blanco Grapefruit', getCategoryByName('Grapefruit')['id'], 100, user3['id'], 3, 1, "Best ever", False, None, None, True))
    
    #Green Apple Products
    db.session.add(Product('Franks Golden Apple', getCategoryByName('Green Apple')['id'], 500, user['id'], 10, 1, "Best apple ever", False, None, None, True))
    db.session.add(Product('Smeralda Apple', getCategoryByName('Green Apple')['id'], 200, user1['id'], 5, 1, "Best apple ever", False, None, None, True))
    db.session.add(Product('Granny Smith Apple', getCategoryByName('Green Apple')['id'], 100, user3['id'], 2, 1, "Best apple ever", False, None, None, True))
    db.session.add(Product('Golden Apple', getCategoryByName('Green Apple')['id'], 3300, user4['id'], 7, 0, "Best apple ever", True, '2022-12-12', '2022-12-20', True))
    
    #Red Apple Products
    db.session.add(Product('Franks Red Apple', getCategoryByName('Red Apple')['id'], 500, user['id'], 10, 0, "Best apple ever", False , None, None, True))
    db.session.add(Product('Fuji Apple', getCategoryByName('Red Apple')['id'], 200, user1['id'], 5, 0, "Best apple ever", False, None, None, True))
    db.session.add(Product('Red Delicious Apple', getCategoryByName('Red Apple')['id'], 100, user3['id'], 2, 0, "Best apple ever", False, None, None, True))
    
    #Yellow Apple Products
    db.session.add(Product('Franks Yellow Apple', getCategoryByName('Yellow Apple')['id'], 500, user['id'], 10, 0, "Best apple ever", False, None, None, True))
    db.session.add(Product('Jonagold Apple', getCategoryByName('Yellow Apple')['id'], 200, user1['id'], 5, 0, "Best apple ever", False, None, None, True))
     
    #White Grape Products
    db.session.add(Product('Thompson Seedless', getCategoryByName('White Grapes')['id'], 100, user3['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Concord Grape', getCategoryByName('White Grapes')['id'], 100, user4['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Chardonnay', getCategoryByName('White Grapes')['id'], 100, user['id'], 3, 1, "Best ever", False, None, None, True))

    #Red Grape Products
    db.session.add(Product('Red Globe', getCategoryByName('Red Grapes')['id'], 100, user1['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Red Flame', getCategoryByName('Red Grapes')['id'], 100, user2['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Red Seedless', getCategoryByName('Red Grapes')['id'], 100, user4['id'], 3, 1, "Best ever", False, None, None, True))
    
    #Lettuce Products
    db.session.add(Product('Iceberg Lettuce', getCategoryByName('Lettuce')['id'], 100, user3['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Romaine Lettuce', getCategoryByName('Lettuce')['id'], 100, user4['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Red Leaf Lettuce', getCategoryByName('Lettuce')['id'], 100, user['id'], 3, 1, "Best ever", False, None, None, True))    

    #Brocolli Products
    db.session.add(Product('Purple Brocolli', getCategoryByName('Brocolli')['id'], 100, user1['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Belstar Brocolli', getCategoryByName('Brocolli')['id'], 100, user2['id'], 3, 1, "Best ever", False, None, None, True))
    
    #Spinach Products
    db.session.add(Product('Pepek Spinach', getCategoryByName('Spinach')['id'], 100, user2['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Baby Spinach', getCategoryByName('Spinach')['id'], 100, user4['id'], 3, 1, "Best ever", False, None, None, True))
    
    #Eggplant Products
    db.session.add(Product('Black Beauty Eggplant', getCategoryByName('Eggplant')['id'], 100, user3['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Purple Eggplant', getCategoryByName('Eggplant')['id'], 100, user4['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Chinese Eggplant', getCategoryByName('Eggplant')['id'], 100, user2['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Fairy Tail Eggplant', getCategoryByName('Eggplant')['id'], 100, user1['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Graffiti Eggplant', getCategoryByName('Eggplant')['id'], 100, user['id'], 3, 1, "Best ever", False, None, None, True))
    
    #Zuchini Products
    db.session.add(Product('Black Beauty Zuchini', getCategoryByName('Zuchini')['id'], 100, user3['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Golden Egg Zuchini', getCategoryByName('Zuchini')['id'], 100, user3['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Magda Zuchini', getCategoryByName('Zuchini')['id'], 100, user4['id'], 3, 1, "Best ever", False, None, None, True))

    #Couliflower Products
    db.session.add(Product('Purple Cauliflower', getCategoryByName('Cauliflower')['id'], 100, user3['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Green Cauliflower', getCategoryByName('Cauliflower')['id'], 100, user4['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Romanesco Cauliflower', getCategoryByName('Cauliflower')['id'], 100, user2['id'], 3, 1, "Best ever", False, None, None, True))
    
    #Celery Products
    db.session.add(Product('Pascal Celery', getCategoryByName('Celery')['id'], 100, user3['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Green Celery', getCategoryByName('Celery')['id'], 100, user4['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('White Celery', getCategoryByName('Celery')['id'], 100, user1['id'], 3, 1, "Best ever", False, None, None, True))
    
    #Asparagus Products
    db.session.add(Product('Erasmus Asparagus', getCategoryByName('Asparagus')['id'], 100, user3['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Jersey Giant Asparagus', getCategoryByName('Asparagus')['id'], 100, user4['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Grande Hybrid Asparagus', getCategoryByName('Asparagus')['id'], 100, user1['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Purple Passion Asparagus', getCategoryByName('Asparagus')['id'], 100, user['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Spartakus Asparagus', getCategoryByName('Asparagus')['id'], 100, user2['id'], 3, 1, "Best ever", False, None, None, True))
    
    #Beet Products
    db.session.add(Product('Bulls Blood Beet', getCategoryByName('Beet')['id'], 100, user3['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Detroit Dark Red Beet', getCategoryByName('Beet')['id'], 100, user4['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Chioggia Beet', getCategoryByName('Beet')['id'], 100, user1['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Cylindra Beet', getCategoryByName('Beet')['id'], 100, user['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Golden Beet', getCategoryByName('Beet')['id'], 100, user2['id'], 3, 1, "Best ever", False, None, None, True))
    
    #Green Bean Products
    db.session.add(Product('French Green Bean', getCategoryByName('Green Bean')['id'], 100, user3['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Romano Bean', getCategoryByName('Green Bean')['id'], 100, user4['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Purple String Bean', getCategoryByName('Green Bean')['id'], 100, user1['id'], 3, 1, "Best ever", False, None, None, True))
    
    #Black Bean Products
    db.session.add(Product('Domino Bean', getCategoryByName('Black Bean')['id'], 100, user3['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Raven Bean', getCategoryByName('Black Bean')['id'], 100, user4['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Black Magic Bean', getCategoryByName('Black Bean')['id'], 100, user1['id'], 3, 1, "Best ever", False, None, None, True))
    
    #Lentil Products
    db.session.add(Product('Black Lentil', getCategoryByName('Lentil')['id'], 100, user['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Red Lentil', getCategoryByName('Lentil')['id'], 100, user2['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Green Lentil', getCategoryByName('Lentil')['id'], 100, user1['id'], 3, 1, "Best ever", False, None, None, True))

    #Soybean Products
    db.session.add(Product('Black Soybean', getCategoryByName('Soybean')['id'], 100, user['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Yellow Soybean', getCategoryByName('Soybean')['id'], 100, user4['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Green Soybean', getCategoryByName('Soybean')['id'], 100, user3['id'], 3, 1, "Best ever", False, None, None, True))
    
    #Peas Products
    db.session.add(Product('English Peas', getCategoryByName('Peas')['id'], 100, user['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Snow Peas', getCategoryByName('Peas')['id'], 100, user2['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Sugar Snap Peas', getCategoryByName('Peas')['id'], 100, user3['id'], 3, 1, "Best ever", False, None, None, True))
    
    #Red Radish Products
    db.session.add(Product('Cherry Belle Radish', getCategoryByName('Red Radish')['id'], 100, user3['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('White Beuty Radish', getCategoryByName('Red Radish')['id'], 100, user2['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Japanese Radish', getCategoryByName('Red Radish')['id'], 100, user1['id'], 3, 1, "Best ever", False, None, None, True))
    
    #White Radish Products
    db.session.add(Product('White Icicle Radish', getCategoryByName('White Radish')['id'], 100, user['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('White Daikon Radish', getCategoryByName('White Radish')['id'], 100, user4['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('White Plum Radish', getCategoryByName('White Radish')['id'], 100, user3['id'], 3, 1, "Best ever", False, None, None, True))
    
    #Jack O Lantern Products
    db.session.add(Product('Franks Jack O Lantern', getCategoryByName('Jack O Lantern')['id'], 100, user['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Jims Jack O Lantern', getCategoryByName('Jack O Lantern')['id'], 100, user1['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Joes Jack O Lantern', getCategoryByName('Jack O Lantern')['id'], 100, user2['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Johns Jack O Lantern', getCategoryByName('Jack O Lantern')['id'], 100, user3['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Alices Jack O Lantern', getCategoryByName('Jack O Lantern')['id'], 100, user4['id'], 3, 1, "Best ever", False, None, None, True))
    
    #Sweet Pumpkin Products
    db.session.add(Product('Sugar Pie Pumpkin', getCategoryByName('Sweet Pumpkin')['id'], 100, user['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Sugar Baby Pumpkin', getCategoryByName('Sweet Pumpkin')['id'], 100, user1['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Sugar Cube Pumpkin', getCategoryByName('Sweet Pumpkin')['id'], 100, user2['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Cinderella Pumpkin', getCategoryByName('Sweet Pumpkin')['id'], 100, user3['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Sugar Pie Pumpkin', getCategoryByName('Sweet Pumpkin')['id'], 100, user4['id'], 3, 1, "Best ever", False, None, None, True))
    
    #Hokkaido Pumpkin Products
    db.session.add(Product('Frank Hokkaido Pumpkin', getCategoryByName('Hokkaido Pumpkin')['id'], 100, user['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Jim Hokkaido Pumpkin', getCategoryByName('Hokkaido Pumpkin')['id'], 100, user1['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Joe Hokkaido Pumpkin', getCategoryByName('Hokkaido Pumpkin')['id'], 100, user2['id'], 3, 1, "Best ever", False, None, None, True))
    
    #Sweet Corn Products
    db.session.add(Product('Blue Hopy Corn', getCategoryByName('Sweet Corn')['id'], 100, user['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Ambrosia Hybrid Corn', getCategoryByName('Sweet Corn')['id'], 100, user1['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Nirvana Hybrid Corn', getCategoryByName('Sweet Corn')['id'], 100, user2['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Peaches and Cream Corn', getCategoryByName('Sweet Corn')['id'], 100, user3['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Picasso Hybrid Corn', getCategoryByName('Sweet Corn')['id'], 100, user4['id'], 3, 1, "Best ever", False, None, None, True))
    
    #Dent Corn Products
    db.session.add(Product('Frank Dent Corn', getCategoryByName('Dent Corn')['id'], 100, user['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Jim Dent Corn', getCategoryByName('Dent Corn')['id'], 100, user1['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('joe Dent Corn', getCategoryByName('Dent Corn')['id'], 100, user2['id'], 3, 1, "Best ever", False, None, None, True))
    
    #Red Pepper Products
    db.session.add(Product('Red Bell Pepper', getCategoryByName('Red Pepper')['id'], 100, user['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Red Cherry Pepper', getCategoryByName('Red Pepper')['id'], 100, user1['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Red Banana Pepper', getCategoryByName('Red Pepper')['id'], 100, user3['id'], 3, 1, "Best ever", False, None, None, True))
    
    #Yellow Pepper Products
    db.session.add(Product('Yellow Bell Pepper', getCategoryByName('Yellow Pepper')['id'], 100, user['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Lemon Drop Pepper', getCategoryByName('Yellow Pepper')['id'], 100, user1['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Yellow Banana Pepper', getCategoryByName('Yellow Pepper')['id'], 100, user2['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Hungarian Wax Pepper', getCategoryByName('Yellow Pepper')['id'], 100, user4['id'], 3, 1, "Best ever", False, None, None, True))
    
    #Orange Pepper Products
    db.session.add(Product('Orange Bell Pepper', getCategoryByName('Orange Pepper')['id'], 100, user['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Orange Cherry Pepper', getCategoryByName('Orange Pepper')['id'], 100, user1['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Orange Banana Pepper', getCategoryByName('Orange Pepper')['id'], 100, user2['id'], 3, 1, "Best ever", False, None, None, True))
    
    #Green Pepper Products
    db.session.add(Product('Green Bell Pepper', getCategoryByName('Green Pepper')['id'], 100, user['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Green Cherry Pepper', getCategoryByName('Green Pepper')['id'], 100, user1['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Green Banana Pepper', getCategoryByName('Green Pepper')['id'], 100, user2['id'], 3, 1, "Best ever", False, None, None, True))
    
    #Red Chili Pepper Products
    db.session.add(Product('Red Chili Pepper', getCategoryByName('Red Chili Pepper')['id'], 100, user['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Red Cherry Chili Pepper', getCategoryByName('Red Chili Pepper')['id'], 100, user1['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Red Banana Chili Pepper', getCategoryByName('Red Chili Pepper')['id'], 100, user3['id'], 3, 1, "Best ever", False, None, None, True))
    
    #Green Chili Pepper Products
    db.session.add(Product('Green Chili Pepper', getCategoryByName('Green Chili Pepper')['id'], 100, user['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Poblano Greeb Chili Pepper', getCategoryByName('Green Chili Pepper')['id'], 100, user1['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Green Banana Chili Pepper', getCategoryByName('Green Chili Pepper')['id'], 100, user2['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Serrano Chili Pepper', getCategoryByName('Green Chili Pepper')['id'], 100, user3['id'], 3, 1, "Best ever", False, None, None, True))
    
    #Jalapeno Pepper Products
    db.session.add(Product('Purple Jalapeno', getCategoryByName('Jalapeno Pepper')['id'], 100, user['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Lemon Spice Jalapeno', getCategoryByName('Jalapeno Pepper')['id'], 100, user1['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Mucho Nacho Jalapeno', getCategoryByName('Jalapeno Pepper')['id'], 100, user2['id'], 3, 1, "Best ever", False, None, None, True))

    #Habanero Pepper Products
    db.session.add(Product('Big Sun Habanero', getCategoryByName('Habanero Pepper')['id'], 100, user['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Caribbean Red Habanero', getCategoryByName('Habanero Pepper')['id'], 100, user1['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Mustard Habanero', getCategoryByName('Habanero Pepper')['id'], 100, user2['id'], 3, 1, "Best ever", False, None, None, True))

    #Cayenne Pepper Products
    db.session.add(Product('Carolina Cayenne Pepper', getCategoryByName('Cayenne Pepper')['id'], 100, user['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Dagger Pod Pepper', getCategoryByName('Cayenne Pepper')['id'], 100, user1['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Golden Cayenne Pepper', getCategoryByName('Cayenne Pepper')['id'], 100, user2['id'], 3, 1, "Best ever", False, None, None, True))
    
    #Champignon Mushroom Products
    db.session.add(Product('Joe Champignon Mushroom', getCategoryByName('Champignon Mushroom')['id'], 100, user2['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('John Champignon Mushroom', getCategoryByName('Champignon Mushroom')['id'], 100, user3['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Alice Champignon Mushroom', getCategoryByName('Champignon Mushroom')['id'], 100, user4['id'], 3, 1, "Best ever", False, None, None, True))
    
    #Portobello Mushroom Products
    db.session.add(Product('Joe Portobello Mushroom', getCategoryByName('Portobello Mushroom')['id'], 100, user2['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('John Portobello Mushroom', getCategoryByName('Portobello Mushroom')['id'], 100, user3['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Alice Portobello Mushroom', getCategoryByName('Portobello Mushroom')['id'], 100, user4['id'], 3, 1, "Best ever", False, None, None, True))
    
    #Oyster Mushroom Products
    db.session.add(Product('Joe Oyster Mushroom', getCategoryByName('Oyster Mushroom')['id'], 100, user2['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('John Oyster Mushroom', getCategoryByName('Oyster Mushroom')['id'], 100, user3['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Alice Oyster Mushroom', getCategoryByName('Oyster Mushroom')['id'], 100, user4['id'], 3, 1, "Best ever", False, None, None, True))
    
    #Shiitake Mushroom Products
    db.session.add(Product('Joe Shiitake Mushroom', getCategoryByName('Shiitake Mushroom')['id'], 100, user2['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('John Shiitake Mushroom', getCategoryByName('Shiitake Mushroom')['id'], 100, user3['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Alice Shiitake Mushroom', getCategoryByName('Shiitake Mushroom')['id'], 100, user4['id'], 3, 1, "Best ever", False, None, None, True))
    
    #White Garlic Products
    db.session.add(Product('Frank White Garlic', getCategoryByName('White Garlic')['id'], 100, user['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Jim White Garlic', getCategoryByName('White Garlic')['id'], 100, user1['id'], 3, 1, "Best ever", False, None, None, True))
    
    #Red Garlic Products
    db.session.add(Product('Red Toch Garlic', getCategoryByName('Red Garlic')['id'], 100, user4['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Jim Red Garlic', getCategoryByName('Red Garlic')['id'], 100, user3['id'], 3, 1, "Best ever", False, None, None, True))
    
    #Baby Carrot Products
    db.session.add(Product('Baby Chantenay Carrot', getCategoryByName('Baby Carrot')['id'], 100, user2['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Joe Baby Carrot', getCategoryByName('Baby Carrot')['id'], 100, user1['id'], 3, 1, "Best ever", False, None, None, True))

    #Regular Carrot Products
    db.session.add(Product('Regular Chantenay Carrot', getCategoryByName('Regular Carrot')['id'], 100, user2['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Joe Regular Carrot', getCategoryByName('Regular Carrot')['id'], 100, user1['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Danvers Carrot', getCategoryByName('Regular Carrot')['id'], 100, user['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Imperator Carrot', getCategoryByName('Regular Carrot')['id'], 100, user3['id'], 3, 1, "Best ever", False, None, None, True))
    
    #Salad cucumber Products
    db.session.add(Product('Frank Salad Cucumber', getCategoryByName('Salad cucumber')['id'], 100, user['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Joe Salad Cucumber', getCategoryByName('Salad cucumber')['id'], 100, user2['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('John Salad Cucumber', getCategoryByName('Salad cucumber')['id'], 100, user3['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Alice Salad Cucumber', getCategoryByName('Salad cucumber')['id'], 100, user4['id'], 3, 1, "Best ever", False, None, None, True))
    
    #Pickling cucumber Products
    db.session.add(Product('Kalipso Pickling Cucumber', getCategoryByName('Pickling cucumber')['id'], 100, user['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Burpee Pickling Cucumber', getCategoryByName('Pickling cucumber')['id'], 100, user2['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Fresh Pickling Cucumber', getCategoryByName('Pickling cucumber')['id'], 100, user3['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Hokus Pickling Cucumber', getCategoryByName('Pickling cucumber')['id'], 100, user4['id'], 3, 1, "Best ever", False, None, None, True))
    
    #Garden cucumber Products
    db.session.add(Product('Frank Garden Cucumber', getCategoryByName('Garden cucumber')['id'], 100, user['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Joe Garden Cucumber', getCategoryByName('Garden cucumber')['id'], 100, user2['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('John Garden Cucumber', getCategoryByName('Garden cucumber')['id'], 100, user3['id'], 3, 1, "Best ever", False, None, None, True))
    
    #Red Tomato Products
    db.session.add(Product('Sunset Red Horizon Tomato', getCategoryByName('Red Tomato')['id'], 100, user['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Red Roma Tomato', getCategoryByName('Red Tomato')['id'], 100, user1['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Red Beefsteak Tomato', getCategoryByName('Red Tomato')['id'], 100, user2['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Red Grape Tomato', getCategoryByName('Red Tomato')['id'], 100, user3['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Red Plum Tomato', getCategoryByName('Red Tomato')['id'], 100, user4['id'], 3, 1, "Best ever", False, None, None, True))
    
    #Yellow Tomato Products
    db.session.add(Product('Yellow Pear Tomato', getCategoryByName('Yellow Tomato')['id'], 100, user['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Yellow Cherry Tomato', getCategoryByName('Yellow Tomato')['id'], 100, user1['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Yellow Grape Tomato', getCategoryByName('Yellow Tomato')['id'], 100, user2['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Golden Queen Tomato', getCategoryByName('Yellow Tomato')['id'], 100, user3['id'], 3, 1, "Best ever", False, None, None, True))
    
    #Cherry Tomato Products
    db.session.add(Product('Black Pearl Cherry Tomato', getCategoryByName('Cherry Tomato')['id'], 100, user['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Midnight Snack Cherry Tomato', getCategoryByName('Cherry Tomato')['id'], 100, user1['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Orange Sunsugar Cherry Tomato', getCategoryByName('Cherry Tomato')['id'], 100, user2['id'], 3, 1, "Best ever", False, None, None, True))
    
    #Red Potato Products
    db.session.add(Product('Red Pontiac Potato', getCategoryByName('Red Potato')['id'], 100, user['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Red Norland Potato', getCategoryByName('Red Potato')['id'], 100, user1['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('La Rouge Potato', getCategoryByName('Red Potato')['id'], 100, user2['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('NorDonna Potato', getCategoryByName('Red Potato')['id'], 100, user3['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Red Thumbelina Potato', getCategoryByName('Red Potato')['id'], 100, user3['id'], 3, 1, "Best ever", False, None, None, True))
    
    #White Potato Products
    db.session.add(Product('Lamoka Potato', getCategoryByName('White Potato')['id'], 100, user['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Mont Blanc Potato', getCategoryByName('White Potato')['id'], 100, user1['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Lady Rosetta Potato', getCategoryByName('White Potato')['id'], 100, user2['id'], 3, 1, "Best ever", False, None, None, True))
    
    #Sweet Potato Products
    db.session.add(Product('Batata Sweet Potato', getCategoryByName('Sweet Potato')['id'], 100, user['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Covington Sweet Potato', getCategoryByName('Sweet Potato')['id'], 100, user1['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Georgia Jet Sweet Potato', getCategoryByName('Sweet Potato')['id'], 100, user2['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Okinawa Sweet Potato', getCategoryByName('Sweet Potato')['id'], 100, user3['id'], 3, 1, "Best ever", False, None, None, True))
    
    #White Onion Products
    db.session.add(Product('White Sweet Spanish Onion', getCategoryByName('White Onion')['id'], 100, user['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('White Bermuda Onion', getCategoryByName('White Onion')['id'], 100, user1['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('White Granex Onion', getCategoryByName('White Onion')['id'], 100, user2['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('White Granex Onion', getCategoryByName('White Onion')['id'], 100, user3['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Pearl Onion', getCategoryByName('White Onion')['id'], 100, user4['id'], 3, 1, "Best ever", False, None, None, True))
    
    #Red Onion Products
    db.session.add(Product('Red Bermuda Onion', getCategoryByName('Red Onion')['id'], 100, user['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Red Beuty Onion', getCategoryByName('Red Onion')['id'], 100, user1['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Mars Red Onion', getCategoryByName('Red Onion')['id'], 100, user2['id'], 3, 1, "Best ever", False, None, None, True))
    
    #White Cabbage Products
    db.session.add(Product('White Savoy Cabbage', getCategoryByName('White Cabbage')['id'], 100, user['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('White Napa Cabbage', getCategoryByName('White Cabbage')['id'], 100, user1['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('White Chinese Cabbage', getCategoryByName('White Cabbage')['id'], 100, user2['id'], 3, 1, "Best ever", False, None, None, True))
    
    #Red Cabbage Products
    db.session.add(Product('Red Savoy Cabbage', getCategoryByName('Red Cabbage')['id'], 100, user['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Red Napa Cabbage', getCategoryByName('Red Cabbage')['id'], 100, user1['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.add(Product('Red Chinese Cabbage', getCategoryByName('Red Cabbage')['id'], 100, user2['id'], 3, 1, "Best ever", False, None, None, True))
    db.session.commit()

    id1 = getUserByEmail('farmer')
    id1 = id1['id']

    id2 = getUserByEmail('user')
    id2 = id2['id']

    prods = getProducts()

    db.session.add(Order(id1, [prods[0]['id'], prods[1]['id']], [5, 10], 69, '1999-01-01', 1))
    db.session.add(Order(id2, [prods[3]['id'], prods[4]['id']], [10, 1], 120, '1999-01-01', 1))
    db.session.add(Order(id2, [prods[5]['id'], prods[6]['id'], prods[7]['id']], [10, 1, 5], 200, '1999-01-01', 0))
    db.session.add(Order(id2, [prods[9]['id']], [15], 100, '1999-01-01', -1))
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

def isProductActive(id):
    list = getProduct()
    for x in list:
        if x['id'] == id and x['active'] == True:
            return True
        else:
            return False
    return None

def isSellingProduct(product_id, seller_id, inactive=False):
    list = getProducts()
    for x in list:
        if x['id'] == product_id and x['seller'] == seller_id:
            if x['active']:
                return True
            elif x['active'] == False and inactive == True:
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

def getProduct(id, inactive=False):
    list = getProducts()
    for x in list:
        if x['id'] == id:
            if x['active'] == False and inactive == True:
                return x
            elif x['active'] == True:
                return x
    return None

def getProductByName(name, category_id, seller_id, inactive=False):
    list = getProducts()
    for x in list:
        if x['name'] == name and x['category'] == category_id and x['seller'] == seller_id:
            if x['active']:
                return x
            elif x['active'] == False and inactive == True:
                return x
    return None

def getProductByNameOnly(name, inactive=False):
    list = getProducts()
    for x in list:
        if x['name'] == name:
            if x['active']:
                return x
            elif x['active'] == False and inactive == True:
                return x
    return None

def getProductsBySeller(seller_id, inactive=False):
    list = getProducts()
    result = []
    for x in list:
        if x['seller'] == seller_id:
            if x['active']:
                result.append(x)
            elif x['active'] == False and inactive == True:
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

def getLeafCategories():
    list = getCategories(True)
    result = []
    for x in list:
        if x['leaf'] == True:
            result.append(x['name'])
    return result

def getProductReview(id, inactive=False):
    list = getProductReviews()
    for x in list:
        if x['id'] == id:
            if x['active']:
                return x
            elif x['active'] and inactive == True:
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
def getUsers(inactive=False):
    if (inactive == True):
        users = User.query.all()
    else:
        users = User.query.filter(User.account_status == True).all()
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

def getProductsByCategory(id, inactive=False):
    if inactive == True:
        products = Product.query.filter(Product.category == id).all()
    else:
        products = Product.query.filter(Product.category == id and Product.active == True).all()
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
def addProduct(name, category, quantity, seller, price, sell_type, description, self_harvest, begin_date, end_date, active=True):
    if len(name) > DB_STRING_SHORT_MAX:
        return 1
    # if isSellingProduct(name, category, seller):
    #     return 2
    # if price < 0:
    #     return 3

    db.session.add(Product(name, category, quantity, seller, price, sell_type, description, self_harvest, begin_date, end_date, active))
    db.session.commit()
    return 0   

# returns: 0 OK; 1 too long string; 2 invalid higher category (ID);
def addCategorySuggestion(category_name, higher_category, leaf, description, suggester_id):
    if len(category_name) > DB_STRING_SHORT_MAX:
        return 1
    if not isCategoryID(higher_category):
        return 2
    print(leaf)
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
