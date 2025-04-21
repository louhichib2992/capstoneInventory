from flask import Blueprint, request, render_template, redirect, url_for, jsonify, flash, session
from functools import wraps

# ======================
# AUTHENTICATION
# ======================
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('inventory.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


from extensions import db
from models import Product, Supplier, Inventory, PurchaseOrder, PurchaseOrderItem, ProductCategory
from datetime import datetime, timedelta
import random

inventory_bp = Blueprint('inventory', __name__)

# =========================
# HOME REDIRECT
# =========================
@inventory_bp.route('/')
def home():
    return redirect(url_for('inventory.login'))


# =========================
# INVENTORY MANAGEMENT
# =========================
@inventory_bp.route('/inventory', methods=['GET'])
def get_inventory():
    supplier_id = request.args.get('supplier_id')
    category_id = request.args.get('category_id')
    low_stock = request.args.get('low_stock')

    query = Inventory.query.join(Product)

    if supplier_id:
        query = query.filter(Product.Supplier_ID == supplier_id)
    if category_id:
        query = query.filter(Product.Category_ID == category_id)
    if low_stock == '1':
        query = query.filter(Inventory.Quantity <= 10)

    inventory_list = query.all()
    suppliers = Supplier.query.all()
    categories = ProductCategory.query.all()

    return render_template('inventory.html',
                           inventory_list=inventory_list,
                           suppliers=suppliers,
                           categories=categories,
                           selected_supplier=int(supplier_id) if supplier_id else None,
                           selected_category=int(category_id) if category_id else None,
                           low_stock_filter=(low_stock == '1'))


@inventory_bp.route('/add_inventory', methods=['GET', 'POST'])
def add_inventory_item():
    products = Product.query.all()

    if request.method == 'POST':
        product_id = request.form['Product_ID']
        quantity = request.form['Quantity']
        unit_price = request.form['Unit_Price']

        new_item = Inventory(
            Product_ID=product_id,
            Quantity=quantity,
            Unit_Price=unit_price
        )
        db.session.add(new_item)
        db.session.commit()
        return redirect(url_for('inventory.get_inventory'))

    return render_template('add_item.html', products=products)


@inventory_bp.route('/update_inventory/<int:id>', methods=['GET', 'POST'])
def update_inventory_quantity(id):
    item = Inventory.query.get_or_404(id)

    if request.method == 'POST':
        item.Quantity = request.form['Quantity']
        db.session.commit()
        return redirect(url_for('inventory.get_inventory'))

    return render_template('update_item.html', item=item)



# =========================
# LOW STOCK MANAGEMENT
# =========================
@inventory_bp.route('/low_stock', methods=['GET'])
def low_stock():
    low_stock_items = Inventory.query.filter(Inventory.Quantity <= 10).all()
    return render_template('low_stock.html', low_stock_items=low_stock_items)


@inventory_bp.route('/inventory/reorder_low_stock', methods=['POST'])
def reorder_low_stock():
    critical_items = Inventory.query.filter(Inventory.Quantity <= 5).all()

    if not critical_items:
        flash("⚠️ No low stock items to reorder!", "error")
        return redirect(url_for('inventory.low_stock'))

    for item in critical_items:
        product = Product.query.get(item.Product_ID)
        if not product or not product.Supplier_ID:
            continue

        order = PurchaseOrder(
            Supplier_ID=product.Supplier_ID,
            Status="Pending",
            Order_Date=datetime.utcnow()
        )
        db.session.add(order)
        db.session.commit()

        order_item = PurchaseOrderItem(
            Purchase_Order_ID=order.Purchase_Order_ID,
            Product_ID=product.Product_ID,
            Quantity=50,
            Created_At=datetime.utcnow(),
            Updated_At=datetime.utcnow()
        )
        db.session.add(order_item)
        db.session.commit()

    flash("✅ Reorders placed successfully!", "success")
    return redirect(url_for('inventory.low_stock'))



# =========================
# SUPPLIER MANAGEMENT
# =========================
@inventory_bp.route('/suppliers', methods=['GET'])
def list_suppliers():
    suppliers = Supplier.query.all()
    return render_template('suppliers.html', suppliers=suppliers)


@inventory_bp.route('/add_supplier', methods=['GET', 'POST'])
def add_supplier():
    if request.method == 'POST':
        new_supplier = Supplier(
            Supplier_Name=request.form['Supplier_Name'],
            Contact_Name=request.form['Contact_Name'],
            Contact_Email=request.form['Contact_Email'],
            Contact_Phone=request.form['Contact_Phone'],
            Address=request.form['Address']
        )
        db.session.add(new_supplier)
        db.session.commit()
        return redirect(url_for('inventory.list_suppliers'))

    return render_template('add_supplier.html')


@inventory_bp.route('/delete_supplier/<int:supplier_id>', methods=['POST'])
def delete_supplier(supplier_id):
    supplier = Supplier.query.get_or_404(supplier_id)
    db.session.delete(supplier)
    db.session.commit()
    return redirect(url_for('inventory.list_suppliers'))


# =========================
# PURCHASE ORDER MANAGEMENT
# =========================
@inventory_bp.route('/purchase_orders', methods=['GET'])
def list_purchase_orders():
    status_filter = request.args.get('status')

    if status_filter:
        purchase_orders = PurchaseOrder.query.filter_by(Status=status_filter).all()
    else:
        purchase_orders = PurchaseOrder.query.all()

    return render_template('purchase_orders.html', purchase_orders=purchase_orders)


@inventory_bp.route('/purchase_order/<int:order_id>', methods=['GET'])
def view_purchase_order_items(order_id):
    order = PurchaseOrder.query.get_or_404(order_id)
    items = PurchaseOrderItem.query.filter_by(Purchase_Order_ID=order_id).all()
    return render_template('purchase_order_items.html', order=order, items=items)


@inventory_bp.route('/receive_order/<int:order_id>', methods=['POST'])
def receive_order(order_id):
    order = PurchaseOrder.query.get_or_404(order_id)

    if order.Status == "Received":
        return redirect(url_for('inventory.list_purchase_orders'))

    for item in order.items:
        inventory_item = Inventory.query.filter_by(Product_ID=item.Product_ID).first()
        if inventory_item:
            inventory_item.Quantity += item.Quantity
        else:
            new_inventory = Inventory(
                Product_ID=item.Product_ID,
                Quantity=item.Quantity,
                Unit_Price=random.uniform(50, 500)
            )
            db.session.add(new_inventory)

    order.Status = "Received"
    db.session.commit()

    return redirect(url_for('inventory.list_purchase_orders'))


# =========================
# DASHBOARD
# =========================
@inventory_bp.route('/dashboard', methods=['GET'])
def dashboard():
    total_products = Product.query.count()
    total_inventory_items = db.session.query(db.func.sum(Inventory.Quantity)).scalar() or 0
    total_stock_value = db.session.query(db.func.sum(Inventory.Quantity * Inventory.Unit_Price)).scalar() or 0
    low_stock_items = Inventory.query.filter(Inventory.Quantity <= 10).count()
    critical_low_stock = Inventory.query.filter(Inventory.Quantity <= 5).all()
    low_stock_alert = len(critical_low_stock) > 0

    return render_template('dashboard.html',
                           total_products=total_products,
                           total_inventory_items=total_inventory_items,
                           total_stock_value=round(total_stock_value, 2),
                           low_stock_items=low_stock_items,
                           low_stock_alert=low_stock_alert)


@inventory_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['logged_in'] = True
        flash('Login successful!', 'success')
        next_page = request.args.get('next')
        return redirect(next_page or url_for('inventory.dashboard'))
    return render_template('login.html')

@inventory_bp.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('inventory.login'))