import os
from flask import Blueprint, request, render_template, redirect, url_for, jsonify, flash, session, abort
from functools import wraps
from datetime import datetime
import random

# Conditional import of database and models
if os.getenv('FLASK_ENV') == 'pos':
    from src.utils.db_utils import db
    from src.models import Product, Supplier, Inventory, PurchaseOrder, PurchaseOrderItem, ProductCategory
else:
    from extensions import db
    from models import Product, Supplier, Inventory, PurchaseOrder, PurchaseOrderItem, ProductCategory

inventory_bp = Blueprint('inventory', __name__)

# ======================
# AUTHENTICATION HELPERS
# ======================
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('inventory.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

# =========================
# HOME REDIRECT
# =========================
@inventory_bp.route('/')
def home():
    return redirect(url_for('inventory.get_inventory'))

# =========================
# INVENTORY MANAGEMENT
# =========================
@inventory_bp.route('/inventory', methods=['GET'])
@login_required
def get_inventory():
    supplier_id = request.args.get('supplier_id')
    category_id = request.args.get('category_id')
    low_stock = request.args.get('low_stock')
    product_id = request.args.get('product_id', type=int)

    query = db.session.query(Inventory).join(Product)

    if product_id:
        query = query.filter(Product.Product_ID == product_id)
    if supplier_id:
        query = query.filter(Product.Supplier_ID == supplier_id)
    if category_id:
        query = query.filter(Product.Category_ID == category_id)
    if low_stock == '1':
        query = query.filter(Inventory.Quantity <= 10)

    inventory_list = query.all()
    suppliers = db.session.query(Supplier).all()
    categories = db.session.query(ProductCategory).all()
    products = query.all()


    return render_template('inventory.html',
                           inventory_list=inventory_list,
                           products = products,
                           suppliers=suppliers,
                           categories=categories,
                           selected_supplier=int(supplier_id) if supplier_id else None,
                           selected_category=int(category_id) if category_id else None,
                           low_stock_filter=(low_stock == '1'))

@inventory_bp.route('/add_inventory', methods=['GET', 'POST'])
@login_required
def add_inventory_item():
    categories = db.session.query(ProductCategory).all()
    suppliers = db.session.query(Supplier).all()

    if request.method == 'POST':
        product_name = request.form['Product_Name']
        description = request.form.get('Description')
        quantity = int(request.form['Quantity'])
        unit_price = float(request.form['Unit_Price'])
        category_name = request.form['Category_Name']
        supplier_name = request.form['Supplier_Name']

        category = db.session.query(ProductCategory).filter_by(Category_Name=category_name).first()
        if not category:
            category = ProductCategory(Category_Name=category_name)
            db.session.add(category)
            db.session.commit()

        supplier = db.session.query(Supplier).filter_by(Supplier_Name=supplier_name).first()
        if not supplier:
            supplier = Supplier(Supplier_Name=supplier_name)
            db.session.add(supplier)
            db.session.commit()

        product = Product(
            Product_Name=product_name,
            Product_Description=description,
            Category_ID=category.Category_ID,
            Supplier_ID=supplier.Supplier_ID
        )
        db.session.add(product)
        db.session.commit()

        inventory_item = Inventory(
            Product_ID=product.Product_ID,
            Quantity=quantity,
            Unit_Price=unit_price
        )
        db.session.add(inventory_item)
        db.session.commit()

        flash("✅ Inventory item added successfully!", "success")
        return redirect(url_for('inventory.get_inventory'))

    return render_template('add_item.html', categories=categories, suppliers=suppliers)

@inventory_bp.route('/update_inventory/<int:id>', methods=['GET', 'POST'])
@login_required
def update_inventory_quantity(id):
    item = db.session.query(Inventory).get(id)
    if item is None:
        abort(404)

    if request.method == 'POST':
        item.Quantity = request.form['Quantity']
        db.session.commit()
        return redirect(url_for('inventory.get_inventory'))

    return render_template('update_item.html', item=item)

# =========================
# LOW STOCK MANAGEMENT
# =========================
@inventory_bp.route('/low_stock', methods=['GET'])
@login_required
def low_stock():
    low_stock_items = db.session.query(Inventory).filter(Inventory.Quantity <= 10).all()
    return render_template('low_stock.html', low_stock_items=low_stock_items)

@inventory_bp.route('/inventory/reorder_low_stock', methods=['POST'])
@login_required
def reorder_low_stock():
    critical_items = db.session.query(Inventory).filter(Inventory.Quantity <= 5).all()

    if not critical_items:
        flash("⚠️ No low stock items to reorder!", "error")
        return redirect(url_for('inventory.low_stock'))

    for item in critical_items:
        product = db.session.query(Product).get(item.Product_ID)
        if not product or not product.Supplier_ID:
            continue

        order = PurchaseOrder(
            Supplier_ID=product.Supplier_ID,
            Purchase_Order_Status="Pending",
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
@login_required
def list_suppliers():
    suppliers = db.session.query(Supplier).all()
    return render_template('suppliers.html', suppliers=suppliers)

@inventory_bp.route('/add_supplier', methods=['GET', 'POST'])
@login_required
def add_supplier():
    if request.method == 'POST':
        new_supplier = Supplier(
            Supplier_Name=request.form['Supplier_Name'],
            Contact_Name=request.form['Contact_Name'],
            Contact_Email=request.form['Contact_Email'],
            Contact_Phone=request.form['Contact_Phone']
        )
        db.session.add(new_supplier)
        db.session.commit()
        return redirect(url_for('inventory.list_suppliers'))

    return render_template('add_supplier.html')

@inventory_bp.route('/delete_supplier/<int:supplier_id>', methods=['POST'])
@login_required
def delete_supplier(supplier_id):
    supplier = db.session.query(Supplier).get(supplier_id)
    if supplier is None:
        abort(404)
    db.session.delete(supplier)
    db.session.commit()
    return redirect(url_for('inventory.list_suppliers'))

# =========================
# PURCHASE ORDER MANAGEMENT
# =========================
@inventory_bp.route('/purchase_orders', methods=['GET'])
@login_required
def list_purchase_orders():
    status_filter = request.args.get('purchase_order_status')

    purchase_orders = None
    if status_filter:
        purchase_orders = db.session.query(PurchaseOrder).filter_by(Purchase_Order_Status=status_filter).all()
    else:
        purchase_orders = db.session.query(PurchaseOrder).all()
    
    return render_template('purchase_orders.html', purchase_orders=purchase_orders)

@inventory_bp.route('/purchase_order/<int:order_id>', methods=['GET'])
@login_required
def view_purchase_order_items(order_id):
    order = db.session.query(PurchaseOrder).get(order_id)
    if order is None:
        abort(404)
    items = db.session.query(PurchaseOrderItem).filter_by(Purchase_Order_ID=order_id).all()
    return render_template('purchase_order_items.html', order=order, items=items)

@inventory_bp.route('/receive_order/<int:order_id>', methods=['POST'])
@login_required
def receive_order(order_id):
    order = db.session.query(PurchaseOrder).get(order_id)
    if order is None:
        abort(404)
    if order.Purchase_Order_Status == "Received":
        return redirect(url_for('inventory.list_purchase_orders'))

    for item in order.items:
        inventory_item = db.session.query(Inventory).filter_by(Product_ID=item.Product_ID).first()
        if inventory_item:
            inventory_item.Quantity += item.Quantity
        else:
            new_inventory = Inventory(
                Product_ID=item.Product_ID,
                Quantity=item.Quantity,
                Unit_Price=random.uniform(50, 500)
            )
            db.session.add(new_inventory)

    order.Purchase_Order_Status = "Received"
    db.session.commit()
    return redirect(url_for('inventory.list_purchase_orders'))

# =========================
# DASHBOARD
# =========================
@inventory_bp.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    total_products = db.session.query(db.func.count(Product.Product_ID)).scalar() or 0
    total_inventory_items = db.session.query(db.func.sum(Inventory.Quantity)).scalar() or 0
    total_stock_value = db.session.query(db.func.sum(Inventory.Quantity * Inventory.Unit_Price)).scalar() or 0
    low_stock_items = db.session.query(Inventory).filter(Inventory.Quantity <= 10).count()
    critical_low_stock = db.session.query(Inventory).filter(Inventory.Quantity <= 5).all()
    low_stock_alert = len(critical_low_stock) > 0

    return render_template('dashboard.html',
                           total_products=total_products,
                           total_inventory_items=total_inventory_items,
                           total_stock_value=round(total_stock_value, 2),
                           low_stock_items=low_stock_items,
                           low_stock_alert=low_stock_alert)

# =========================
# AUTH VIEWS
# =========================
@inventory_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['logged_in'] = True
        flash('Login successful!', 'success')
        next_page = request.args.get('next')
        return redirect(next_page or url_for('inventory.dashboard'))
    return render_template('inventory_login.html')

@inventory_bp.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('inventory.login'))
