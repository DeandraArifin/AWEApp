from flask import Flask, session, request, redirect, url_for, render_template, flash
from matplotlib.animation import subprocess_creation_flags
from Models import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy import and_


Session = sessionmaker(bind=engine)
db_session = Session()

app = Flask(__name__)
app.secret_key = 'HELLO123'

account_manager = AccountManager(db_session)

admin_acc = Admin('CillianM', '123', 'Cillian Murphy', 'cillianm@gmail.com', AccountType.ADMIN, 120001)
account_manager.register_admin('CillianM', '123', 'Cillian Murphy', 'cillianm@gmail.com', AccountType.ADMIN, 120001)
print(admin_acc.employee_id)

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
    category = request.args.get('category')
    catalogue = ProductCatalogue(db_session)
    if category and category in ProductCategory.__members__:
        filtered_products = catalogue.search_by_category(category)
    elif category and category=='sale':
        filtered_products = catalogue.get_sale_items()
    else:
        filtered_products = catalogue.get_all_products()
    
    return render_template('home.html', products=filtered_products, ProductCategory=ProductCategory, request=request)


@app.route("/login", methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        account = account_manager.login(username, password)
        
        if (account != None and isinstance(account, Customer)):
            session['username'] = username
            return redirect(url_for('customerdashboard'))
        
        elif (account != None and isinstance(account, Admin)):
            session['username'] = username
            return redirect(url_for('admindashboard'))
        else:
            return "Login failed", 401
    return render_template('login.html')

@app.route("/logout", methods=['POST', 'GET'])
def logout():
    session.clear()
    return redirect(url_for('home'))

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
        

# @app.route("/customerdashboard")
# def customerdashboard():
#     if 'username' not in session:
#         return redirect(url_for('login'))
    
#     customer_acc = db_session.query(Account).filter_by(username=session['username']).first()
    
    
#     return render_template('customerdashboard.html', customer = customer_acc)

@app.route("/customerdashboard")
def customerdashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    # Ensures only logged-in customers access the page.

    # Queries each order's receipt and attaches it to the order object.
    customer_acc = db_session.query(Account).filter_by(username=session['username']).first()

    if not isinstance(customer_acc, Customer):
        flash("Unauthorized access. Customer account required.", "danger")
        return redirect(url_for('login'))

    # Preload receipts for each order
    for order in customer_acc.orders:
        receipt = db_session.query(Receipt).filter_by(order_id=order.id).first()
        order.receipt = receipt  # Attach receipt to order object

    return render_template('customerdashboard.html', customer=customer_acc)


@app.route("/admindashboard")
def admindashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    admin_acc = db_session.query(Account).filter(
        and_(
            Account.username == session['username'],
            Account.account_type == 'ADMIN')
        ).first()
    
    admin_acc = db_session.query(Account).filter_by(username=session['username']).first()

    return render_template('admindashboard.html', admin = admin_acc)

@app.route("/ordermanager", methods=['POST', 'GET'])
def ordermanager():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        orders = db_session.query(Order).all()
        for order in orders:
            key = f"status_{order.id}"
            new_status = request.form.get(key)
            print(new_status)
            
            if new_status and new_status != order.status:
                order.status= OrderStatus[new_status]
        
        db_session.commit()
    
    orders = db_session.query(Order).all()
    return render_template('ordermanager.html', orders=orders, order_status = OrderStatus)
    

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

@app.route("/checkout", methods=['GET','POST'])
def checkout():
    customer = None
    if 'username' in session:
        account = db_session.query(Account).filter_by(username=session['username']).first()
        if account and isinstance(account, Customer):
            customer = account
        else:
            customer = None
    
    cart = get_or_create_cart(db_session)
    
    if request.method=='POST':
        full_name = request.form['fullname']
        email = request.form['email']
        phone_number = request.form['phone_number']
        shipping_address = request.form['address']
        order = cart.checkout(db_session, customer.id if customer else None, full_name, email, shipping_address, phone_number)
        cart.empty_cart(db_session)
        
        return "Order placed successfully! Please find an invoice to proceed with payment in your inboxes."

    
    return render_template('checkout.html', customer=customer, cart=cart)

@app.route("/productmanager", methods=["GET", "POST"])
def productmanager():
    if request.method == "POST":
        if 'username' in session:
            account = db_session.query(Account).filter_by(username=session['username']).first()
        
        products = db_session.query(Product).all()
        catalogue = ProductCatalogue(db_session)
        product_manager = ProductManager(account, catalogue)
        action = request.form.get("action")
        
        if action == 'update':
            has_errors = False
        
            for i in range(1, len(products) + 1):
                product_id = request.form.get(f"product_id_{i}")
                if request.form.get(f"delete_{i}"):
                    product_manager.remove_product(product_id, db_session)
                    continue

                name = request.form.get(f"name_{i}")
                description = request.form.get(f"description_{i}")
                price = float(request.form.get(f"price_{i}"))
                stock = int(request.form.get(f"stock_{i}"))
                category = ProductCategory[request.form.get(f"category_{i}")]
                on_sale = request.form.get(f"on_sale_{i}") == "True"
                discount_percentage = float(request.form.get(f"discount_{i}") or 0)
                
                error=product_manager.modify_product(
                    session=db_session, 
                    product_id=product_id, 
                    name=name, 
                    description=description, 
                    price=price, 
                    stock=stock, 
                    category=category, 
                    on_sale=on_sale, 
                    discount_percentage=discount_percentage)
                
                
                if error:
                    has_errors = True
                    flash(f"Product ID {product_id}: {error}", "danger")
                    
            if not has_errors:
                db_session.commit()
                flash("Catalog updated successfully.", "success")
            else:
                db_session.rollback()

        if action == 'add':  # if form was filled
            
            name=request.form.get("new_name")
            description=request.form.get("new_description")
            price=float(request.form.get("new_price"))
            stock=int(request.form.get("new_stock"))
            category=ProductCategory[request.form.get("new_category")]
            on_sale=request.form.get("new_on_sale") == "True"
            discount_percentage=float(request.form.get("new_discount") or 0)
            
            product_manager.add_product(name, description, price, stock, category, on_sale, discount_percentage, db_session)
        
            db_session.commit()
            flash("Catalog updated successfully.", "success")
        
        return redirect(url_for("productmanager"))

    products = db_session.query(Product).all()
    return render_template("productmanager.html", products=products, category_enum=ProductCategory)



# payment routing
@app.route("/payment", methods=['GET', 'POST'])
def payment():
    if request.method == 'POST':
        selected_method = request.form.get('payment_method')
        flash(f"Payment method '{selected_method}' selected. (This is a dummy page.)", "info")
        return redirect(url_for('home'))

    return render_template('payment.html')

# invoice routing
@app.route("/invoices")
def invoices():
    if 'username' not in session:
        return redirect(url_for('login'))

    account = db_session.query(Account).filter_by(username=session['username']).first()
    if not isinstance(account, Customer):
        return "Access Denied", 403

    customer_orders = db_session.query(Order).filter_by(customer_id=account.id).all()
    return render_template('invoices.html', orders=customer_orders)

from flask import render_template, request, flash, redirect, url_for

@app.route('/invoice/<int:order_id>', methods=['GET', 'POST'])
def invoice_detail(order_id):
    session_db = Session(bind=engine)
    order = session_db.get(Order, order_id)

    if not order:
        flash("Invoice not found.", "danger")
        return redirect(url_for('invoices'))

    if request.method == 'POST':
        payment_method = request.form.get('payment_method')

        if payment_method:
            # Strategy pattern
            if payment_method == 'CREDITCARD':
                strategy = CreditCardPayment()
            elif payment_method == 'BANKTRANSFER':
                strategy = BankTransferPayment()
            elif payment_method == 'PAYPAL':
                strategy = PayPalPayment()
            elif payment_method == 'CASH':
                strategy = CashOnDeliveryPayment()
            else:
                flash("Invalid payment method", "danger")
                return redirect(url_for('invoice_detail', order_id=order.id))

            strategy.process_payment(order, session_db)

            # ✅ Set status to PAID
            order.status = OrderStatus.PAID
            session_db.commit()

            return redirect(url_for('payment_confirmation', order_id=order.id))

    return render_template('invoice_detail.html', order=order)

# Payment confirmation routing
# Payment confirmation routing
@app.route('/invoice/<int:order_id>/confirmation')
def payment_confirmation(order_id):
    session = Session(bind=engine)

    try:
        order = session.get(Order, order_id)
        invoice = session.query(Invoice).filter_by(order_id=order_id).first()

        if not order or not invoice:
            flash("Order or Invoice not found for confirmation", "danger")
            return redirect(url_for('invoices'))

        # Optional: flash a success message
        flash(f"Payment for Order #{order.id} was successful.", "success")

        return render_template('payment_confirmation.html', order=order, invoice=invoice)

    finally:
        session.close()
# Receipt routing
@app.route('/receipt/<int:order_id>')
def view_receipt(order_id):
    session_db = Session(bind=engine)
    try:
        order = session_db.get(Order, order_id)
        receipt = session_db.query(Receipt).filter_by(order_id=order_id).first()

        if not order or not receipt:
            flash("Receipt not found.", "danger")
            return redirect(url_for('customerdashboard'))

        return render_template('receipt.html', order=order, receipt=receipt)
    finally:
        session_db.close()
           
if __name__ == "__main__":
    app.run(debug=False)
