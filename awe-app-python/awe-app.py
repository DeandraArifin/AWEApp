from flask import Flask, session, request, redirect, url_for, render_template
from AccountManager import AccountManager
from Account import Account

app = Flask(__name__)
app.secret_key = 'HELLO123'

account_manager = AccountManager()

myaccount = Account("Dea", "123", "Deandra Arifin","dea@gmail.com")
account_manager.add_account(myaccount)

@app.route("/")
def home():
    return render_template('home.html')

@app.route("/login", methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        account = account_manager.login(username, password)
        if (account):
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
        account_manager.register(username, password, name, email, shipping_address, phone_number)
        
        if(account_manager.account_exists(username)):
            return "Registration succeeded, please login"
    return render_template('register.html')
        

@app.route("/customerdashboard")
def customerdashboard():
    if 'username' in session:
        return f"Welcome, {session['username']}!"
    return redirect(url_for('login'))