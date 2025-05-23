from flask import Flask, session, request, redirect, url_for, render_template
from Models import Product, Customer, Account, Admin, Order, ShoppingCart
from AccountManager import AccountManager

app = Flask(__name__)
app.secret_key = 'HELLO123'

account_manager = AccountManager()

myaccount = Account("Dea", "123", "Deandra Arifin","dea@gmail.com")
account_manager.add_account(myaccount)
account_manager.register("Fawn", "123", "Fawn Pavano","fpavano@gmail.com", "tralala", "1234")
print(account_manager.accounts)

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
    return render_template('home.html')

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
    if 'username' in session:
        return f"Welcome, {session['username']}!"
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=False)
