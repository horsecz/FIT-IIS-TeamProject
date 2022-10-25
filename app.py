from unicodedata import category
from flask import request, jsonify
from flask_marshmallow import Marshmallow
from flask_cors import CORS, cross_origin
from flask_sqlalchemy import SQLAlchemy
from flask import Flask

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://postgres:postgres@localhost:5432/postgres'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
ma = Marshmallow(app)

@app.route('/', methods=['GET'])
@cross_origin()
def get():
    # test if db is created and data is inserted
    print(User.query.all())
    return jsonify({'msg': 'Hello World'})

@app.route('/user', methods=['GET'])
@cross_origin()
def get_user():
    # get all results and return json
    users = User.query.all()
    user_schema = UserSchema(many=True)
    return jsonify(user_schema.dump(users))


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

if __name__ == '__main__':
    app.run(debug=True)

def create_db():
    app.app_context().push()
    db.drop_all()
    db.create_all()
    db.session.add(User('email@email.com', 'Peter', '1995-1-1', '7th Street', 'abc123', 1, 905240384))
    db.session.add(User('email@email2.com', 'Peter2', '1996-1-1', '8th Street', 'abc1234', 1, 905240354))
    db.session.add(Category('root', None, False))
    db.session.commit()
    db.session.add(Category('fruit', 1, False))
    db.session.commit()
    db.session.add(Category('vegetable', 1, False))
    db.session.commit()
    db.session.add(Category('apple', 2, True))
    db.session.commit()
    db.session.add(Product('green_apple', 1, 250, 2, 24, 1, 'fajne jabko', False, None, None))
    db.session.commit()
    db.session.add(Order(1, 1, 2, 48, '2021-01-01', 1))
    db.session.commit()
    
    
# schemas;

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100))
    name = db.Column(db.String(100))
    birth_date = db.Column(db.Date)
    address = db.Column(db.String(100))
    password = db.Column(db.String(100))
    role = db.Column(db.Integer)
    phone_number = db.Column(db.Integer)
    
    def __init__(self, email, name, birth_date, address, password, role, phone_number):
        self.email = email
        self.name = name
        self.birth_date = birth_date
        self.address = address
        self.password = password
        self.role = role
        self.phone_number = phone_number

class UserSchema(ma.Schema):
    class Meta:
        fields = ('id', 'email', 'name', 'birth_date', 'address', 'password', 'role', 'phone_number')
        

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    category = db.Column(db.Integer, db.ForeignKey('category.id'))
    quantity = db.Column(db.Integer)
    seller = db.Column(db.Integer, db.ForeignKey('user.id'))
    price = db.Column(db.Integer)
    sell_type = db.Column(db.Integer)
    description = db.Column(db.String(100))
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
    name = db.Column(db.String(100))
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
