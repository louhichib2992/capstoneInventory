from extensions import db
from datetime import datetime

# ========== Product Table ==========
class Product(db.Model):
    __tablename__ = 'Product'

    Product_ID = db.Column(db.Integer, primary_key=True)
    Product_Name = db.Column(db.String(100), nullable=False)
    Product_Description = db.Column(db.Text)
    Category_ID = db.Column(db.Integer, db.ForeignKey('Product_Category.Category_ID'))
    Supplier_ID = db.Column(db.Integer, db.ForeignKey('Supplier.Supplier_ID'))
    Image_URL = db.Column(db.String(255))
    Deleted_At = db.Column(db.DateTime)

    # Relationships
    category = db.relationship('ProductCategory', backref='products')
    supplier = db.relationship('Supplier', backref='products')
    inventory = db.relationship('Inventory', backref='product', uselist=False)

# ========== Product Category Table ==========
class ProductCategory(db.Model):
    __tablename__ = 'Product_Category'

    Category_ID = db.Column(db.Integer, primary_key=True)
    Category_Name = db.Column(db.String(100), nullable=False)
    Category_Description = db.Column(db.Text)

# ========== Supplier Table ==========
class Supplier(db.Model):
    __tablename__ = 'Supplier'

    Supplier_ID = db.Column(db.Integer, primary_key=True)
    Supplier_Name = db.Column(db.String(100), nullable=False)
    Contact_Name = db.Column(db.String(100))
    Contact_Email = db.Column(db.String(255))
    Contact_Phone = db.Column(db.String(20))
    Address = db.Column(db.String(255))

# ========== Inventory Table ==========
class Inventory(db.Model):
    __tablename__ = 'Inventory'

    Inventory_ID = db.Column(db.Integer, primary_key=True)
    Product_ID = db.Column(db.Integer, db.ForeignKey('Product.Product_ID'))
    Quantity = db.Column(db.Integer, default=0)
    Unit_Price = db.Column(db.Float)
    Deleted_At = db.Column(db.DateTime)

# ========== Purchase Order Table ==========
class PurchaseOrder(db.Model):
    __tablename__ = 'Purchase_Order'

    Purchase_Order_ID = db.Column(db.Integer, primary_key=True)
    Supplier_ID = db.Column(db.Integer, db.ForeignKey('Supplier.Supplier_ID'))
    Status = db.Column(db.String(50), nullable=False)
    Order_Date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    Created_At = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    Updated_At = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    supplier = db.relationship('Supplier', backref='purchase_orders')
    items = db.relationship('PurchaseOrderItem', backref='order')

# ========== Purchase Order Item Table ==========
class PurchaseOrderItem(db.Model):
    __tablename__ = 'Purchase_Order_Item'

    Purchase_Order_Item_ID = db.Column(db.Integer, primary_key=True)
    Purchase_Order_ID = db.Column(db.Integer, db.ForeignKey('Purchase_Order.Purchase_Order_ID'))
    Product_ID = db.Column(db.Integer, db.ForeignKey('Product.Product_ID'))
    Quantity = db.Column(db.Integer, nullable=False)
    Created_At = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    Updated_At = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    product = db.relationship('Product')
