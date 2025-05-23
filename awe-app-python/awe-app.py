from flask import Flask, session, request, redirect, url_for, render_template
from Models import engine, Product, Customer, Account, Admin, Order, ShoppingCart, AccountType, CartItem
from AccountManager import AccountManager
from sqlalchemy.orm import sessionmaker

Session = sessionmaker(bind=engine)
db_session = Session()

app = Flask(__name__)
app.secret_key = 'HELLO123'

account_manager = AccountManager(db_session)

myaccount = Account("Dea", "123", "Deandra Arifin","dea@gmail.com", AccountType.CUSTOMER)
account_manager.add_account(myaccount)
account_manager.register("Fawn", "123", "Fawn Pavano","fpavano@gmail.com", "tralala", "1234")

def get_or_create_cart(db_session):
    if 'cart_id' in session:
        cart = db_session.query(ShoppingCart).filter_by(id=session['cart_id']).first()
        if cart:
            return cart

    # Create a new guest cart
    cart = ShoppingCart()
    db_session.add(cart)
    db_session.commit()
    session['cart_id'] = cart.id
    return cart

@app.route("/")
def home():
    products = db_session.query(Product).all()
    return render_template('home.html', products=products)

@app.route("/login", methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        account = account_manager.login(username, password)
        if (account != None):
            session['username'] = username
            return redirect(url_for('customerdashboard'))
        else:
            return "Login failed", 401
    return render_template('login.html')

@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        name = request.form['fullname']
        email = request.form['email']
        shipping_address = request.form['shipping_address']
        phone_number = request.form['phone_number']
        success = account_manager.register(username, password, name, email, shipping_address, phone_number)
        
        if(success):
            return 'Registration succeeded, please <a href="{}">login</a>'.format(url_for("login"))
        else:
            return 'Username already exists. Please <a href="{}">try again</a>.'.format(url_for("register"))

    return render_template('register.html')
        

@app.route("/customerdashboard")
def customerdashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    customer_acc = db_session.query(Account).filter_by(username=session['username']).first()
    return render_template('customerdashboard.html', customer_name=customer_acc.full_name)

@app.route("/cart")
def view_cart():
    cart = get_or_create_cart(db_session)
    return render_template('cart.html', cart=cart)

@app.route("/update_cart/<int:item_id>", methods=['POST'])
def update_cart(item_id):
    action = request.form.get('action')
    cart_item = db_session.query(CartItem).filter_by(id=item_id).first()
    cart = get_or_create_cart(db_session)
    
    if cart_item:
        if action == 'increase':
            cart.add_item_quantity(cart_item, db_session)
        elif action == 'decrease':
            cart.reduce_item_quantity(cart_item, db_session)
            
    return redirect(url_for('view_cart'))

@app.route("/add_to_cart/<int:product_id>", methods=['POST'])
def add_to_cart(product_id):
    quantity = int(request.form.get("quantity", 1))
    
    product = db_session.query(Product).get(product_id)
    if not product:
        return "Product not found"
    
    cart = get_or_create_cart(db_session)
    
    cart.add_item_quantity(product, db_session)
    
    return redirect(url_for('home'))
    
    
            
if __name__ == "__main__":
    app.run(debug=False)
