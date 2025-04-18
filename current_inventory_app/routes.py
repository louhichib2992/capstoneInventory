from flask import session, redirect, url_for, flash, render_template, request, Blueprint, jsonify
from functools import wraps
from extensions import db
from models import Product, Supplier, Inventory, PurchaseOrder, PurchaseOrderItem, ProductCategory
from datetime import datetime, timedelta
import random
#hello
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

# ======================
# AUTH ROUTES
# ======================
@inventory_bp.route('/')
def root():
    """Root route that redirects to login or dashboard based on auth status"""
    if session.get('logged_in'):
        return redirect(url_for('inventory.dashboard'))
    return redirect(url_for('inventory.login'))

@inventory_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login route that handles both GET and POST requests"""
    if session.get('logged_in'):
        return redirect(url_for('inventory.dashboard'))
    
    if request.method == 'POST':
        # Simple authentication - accepts any username/password
        session['logged_in'] = True
        flash('Login successful!', 'success')
        
        # Redirect to next page if it exists, otherwise dashboard
        next_page = request.args.get('next') or url_for('inventory.dashboard')
        return redirect(next_page)
    
    return render_template('login.html')

@inventory_bp.route('/logout')
def logout():
    """Logout route that clears the session"""
    session.pop('logged_in', None)
    return redirect(url_for('inventory.login'))

# ======================
# PROTECTED ROUTES
# ======================
@inventory_bp.route('/dashboard')
@login_required
def dashboard():
    """Dashboard route - only accessible when logged in"""
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

@inventory_bp.route('/inventory', methods=['GET'])
@login_required
def get_inventory():
    """Inventory route - only accessible when logged in"""
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

# All other protected routes...
@inventory_bp.route("/suppliers")
@login_required
def list_suppliers():
    return render_template("suppliers.html")

@inventory_bp.route("/purchase-orders")
@login_required
def list_purchase_orders():
    return render_template("purchase_orders.html")

@inventory_bp.route("/low-stock")
@login_required
def low_stock():
    return render_template("low_stock.html")

@inventory_bp.route("/inventory/update/<int:id>", methods=["GET", "POST"])
@login_required
def update_inventory_quantity(id):
    return render_template("update_inventory.html", item_id=id)

@inventory_bp.route("/inventory/add", methods=["GET", "POST"])
@login_required
def add_inventory_item():
    return render_template("add_inventory_item.html")