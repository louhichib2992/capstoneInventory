from app import create_app
from extensions import db
from models import Supplier, ProductCategory, Product, Inventory, PurchaseOrder, PurchaseOrderItem
import random
from datetime import datetime, timedelta

# Create Flask app
app = create_app()

with app.app_context():
    # Clear old data
    db.session.query(PurchaseOrderItem).delete()
    db.session.query(PurchaseOrder).delete()
    db.session.query(Inventory).delete()
    db.session.query(Product).delete()
    db.session.query(ProductCategory).delete()
    db.session.query(Supplier).delete()
    db.session.commit()

    # Add Suppliers
    suppliers = [
        Supplier(Supplier_Name="Tech Supplies Inc", Contact_Name="John Doe", Contact_Email="techsupplies@example.com", Contact_Phone="123-456-7890", Address="123 Tech Road"),
        Supplier(Supplier_Name="Office Depot", Contact_Name="Jane Smith", Contact_Email="officedepot@example.com", Contact_Phone="234-567-8901", Address="456 Office St"),
        Supplier(Supplier_Name="Furniture World", Contact_Name="Sam Wilson", Contact_Email="furnitureworld@example.com", Contact_Phone="345-678-9012", Address="789 Furniture Ave"),
        Supplier(Supplier_Name="Gadget Galaxy", Contact_Name="Alice Brown", Contact_Email="gadgetgalaxy@example.com", Contact_Phone="456-789-0123", Address="101 Gadget Blvd"),
        Supplier(Supplier_Name="Supply Hub", Contact_Name="Bob Johnson", Contact_Email="supplyhub@example.com", Contact_Phone="567-890-1234", Address="202 Supply Lane")
    ]
    db.session.add_all(suppliers)
    db.session.commit()

    # Add Categories
    categories = [
        ProductCategory(Category_Name="Electronics", Category_Description="Electronic devices"),
        ProductCategory(Category_Name="Office Supplies", Category_Description="Office equipment and supplies"),
        ProductCategory(Category_Name="Furniture", Category_Description="Furniture for office and home"),
        ProductCategory(Category_Name="Gaming", Category_Description="Gaming consoles and accessories"),
        ProductCategory(Category_Name="Accessories", Category_Description="General tech accessories")
    ]
    db.session.add_all(categories)
    db.session.commit()

    # Add Products
    product_names = [
        "Laptop", "Desk Chair", "Wireless Mouse", "Mechanical Keyboard", "Monitor",
        "Desk Lamp", "Headphones", "Printer", "Webcam", "Wi-Fi Router",
        "Smartphone", "Tablet", "Gaming Console", "Graphics Card", "Office Desk",
        "Bookshelf", "Coffee Machine", "Smartwatch", "External Hard Drive", "USB Hub"
    ]
    products = []
    for name in product_names:
        product = Product(
            Product_Name=name,
            Product_Description=f"{name} - high quality product",
            Category_ID=random.choice(categories).Category_ID,
            Supplier_ID=random.choice(suppliers).Supplier_ID,
            Image_URL="https://via.placeholder.com/150"
        )
        db.session.add(product)
        products.append(product)
    db.session.commit()

    # Add Inventory
    for product in products:
        inventory = Inventory(
            Product_ID=product.Product_ID,
            Quantity=random.randint(5, 100),
            Unit_Price=round(random.uniform(50.0, 500.0), 2)
        )
        db.session.add(inventory)
    db.session.commit()

    # Add Purchase Orders
    purchase_orders = []
    for _ in range(5):
        supplier = random.choice(suppliers)
        order_date = datetime.utcnow() - timedelta(days=random.randint(1, 30))

        po = PurchaseOrder(
            Supplier_ID=supplier.Supplier_ID,
            Status=random.choice(["Pending", "Received", "Cancelled"]),
            Order_Date=order_date
        )
        db.session.add(po)
        purchase_orders.append(po)
    db.session.commit()

    # Add Purchase Order Items
    for po in purchase_orders:
        num_items = random.randint(2, 5)
        products_for_order = random.sample(products, num_items)
        for product in products_for_order:
            poi = PurchaseOrderItem(
                Purchase_Order_ID=po.Purchase_Order_ID,
                Product_ID=product.Product_ID,
                Quantity=random.randint(1, 20),
                Created_At=datetime.utcnow(),
                Updated_At=datetime.utcnow()
            )
            db.session.add(poi)
    db.session.commit()

    print("Full mock data inserted successfully!")
