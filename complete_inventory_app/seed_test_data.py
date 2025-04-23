import os
from app import create_app
from datetime import datetime, timedelta

# Conditional import of database and models
if os.getenv('FLASK_ENV') == 'pos':
    from src.utils.db_utils import db
    from src.models import Supplier, ProductCategory, Product, Inventory, PurchaseOrder, PurchaseOrderItem
else:
    from extensions import db
    from models import Supplier, ProductCategory, Product, Inventory, PurchaseOrder, PurchaseOrderItem

# Initialize the Flask app
app = create_app()

with app.app_context():
    # Drop and recreate all inventory-related tables
    db.drop_all()
    db.create_all()

    # ========== Suppliers ==========
    supp1 = Supplier(
        Supplier_Name='Beautisa',
        Contact_Name='Laura Pierre',
        Contact_Email='laura.p@beautisa.com',
        Contact_Phone='919-991-1199',
    )
    supp2 = Supplier(
        Supplier_Name='Beats by Dre',
        Contact_Name='John Smith',
        Contact_Email='johnsmith@beatsbydre.com',
        Contact_Phone='209-902-2200',
    )

    supp3 = Supplier(
        Supplier_Name='GadgetZone',
        Contact_Name='Mike Thomson',
        Contact_Email='mike@gadgetzone.io',
        Contact_Phone='415-339-7771',
    )
    supp4 = Supplier(
        Supplier_Name='NaturalVibes',
        Contact_Name='Sophia Lee',
        Contact_Email='slee@naturalvibes.com',
        Contact_Phone='718-888-2345',
    )
    db.session.add_all([supp1, supp2, supp3, supp4])
    db.session.commit()

    # ========== Product Categories ==========
    cat1 = ProductCategory(
        Category_Name='Haircare',
        Category_Description='Products related to haircare maintenance'
    )
    cat2 = ProductCategory(
        Category_Name='Electronics',
        Category_Description='Products related to electronic devices'
    )
    cat3 = ProductCategory(
        Category_Name='Skincare',
        Category_Description='Products related to skincare'
    )
    cat4 = ProductCategory(
        Category_Name='Audio',
        Category_Description='Products relating to audio gear'
    )

    db.session.add_all([cat1, cat2, cat3, cat4])
    db.session.commit()

    # ========== Products ==========
    prod1 = Product(
        Product_Name='Hair Spray Bottle',
        Product_Description='Ultra fine mist water sprayer for hairstyling and cleaning 2 pack 6.8 oz',
        Category_ID=cat1.Category_ID,
        Supplier_ID=supp1.Supplier_ID,
        Image_URL=None
    )
    prod2 = Product(
        Product_Name='Beats Powerbeats Pro 2',
        Product_Description='Wireless bluetooth earbuds - noise cancelling',
        Category_ID=cat2.Category_ID,
        Supplier_ID=supp2.Supplier_ID,
        Image_URL=None
    )
    prod3 = Product(
        Product_Name='Lotion',
        Product_Description='Body Lotion',
        Category_ID=cat3.Category_ID,
        Supplier_ID=supp4.Supplier_ID,
        Image_URL=None
    )
    prod4 = Product(
        Product_Name='Crucial 1TB SSD',
        Product_Description='1TB portable SSD',
        Category_ID=cat2.Category_ID,
        Supplier_ID=supp3.Supplier_ID,
        Image_URL=None
    )
    db.session.add_all([prod1, prod2, prod3, prod4])
    db.session.commit()

    # ========== Inventory ==========
    inv1 = Inventory(
        Product_ID=prod1.Product_ID,
        Quantity=3000,
        Unit_Price=6.99
    )
    inv2 = Inventory(
        Product_ID=prod2.Product_ID,
        Quantity=100,
        Unit_Price=249.00
    )
    inv3 = Inventory(
        Product_ID=prod3.Product_ID,
        Quantity=40,
        Unit_Price=4.99
    )
    inv4 = Inventory(
        Product_ID=prod4.Product_ID,
        Quantity=20,
        Unit_Price=29.99
    )
    db.session.add_all([inv1, inv2, inv3, inv4])
    db.session.commit()

    # ========== Purchase Orders ==========
    po1 = PurchaseOrder(
        Supplier_ID=supp1.Supplier_ID,
        Order_Date=datetime.utcnow() - timedelta(days=5),
        Status='Received'
    )
    po2 = PurchaseOrder(
        Supplier_ID=supp2.Supplier_ID,
        Order_Date=datetime.utcnow() - timedelta(days=3),
        Status='Pending'
    )
    po3 = PurchaseOrder(
        Supplier_ID=supp1.Supplier_ID,
        Order_Date=datetime.utcnow() - timedelta(days=1),
        Status='Pending'
    )
    po4 = PurchaseOrder(
        Supplier_ID=supp4.Supplier_ID,
        Order_Date=datetime.utcnow() - timedelta(days=1),
        Status='Pending'
    )
    po5 = PurchaseOrder(
        Supplier_ID=supp3.Supplier_ID,
        Order_Date=datetime.utcnow() - timedelta(days=1),
        Status='Pending'
    )

    db.session.add_all([po1, po2, po3, po4, po5])
    db.session.commit()

    # ========== Purchase Order Items ==========
    poi1 = PurchaseOrderItem(
        Purchase_Order_ID=po1.Purchase_Order_ID,
        Product_ID=prod1.Product_ID,
        Quantity=500
    )
    poi2 = PurchaseOrderItem(
        Purchase_Order_ID=po2.Purchase_Order_ID,
        Product_ID=prod1.Product_ID,
        Quantity=250
    )
    poi3 = PurchaseOrderItem(
        Purchase_Order_ID=po3.Purchase_Order_ID,
        Product_ID=prod2.Product_ID,
        Quantity=75
    )
    poi4 = PurchaseOrderItem(
        Purchase_Order_ID=po4.Purchase_Order_ID,
        Product_ID=prod3.Product_ID,
        Quantity=75
    )
    poi5 = PurchaseOrderItem(
        Purchase_Order_ID=po5.Purchase_Order_ID,
        Product_ID=prod4.Product_ID,
        Quantity=75
    )
    db.session.add_all([poi1, poi2, poi3])
    db.session.commit()

    print("✅ Inventory test data seeded successfully.")
