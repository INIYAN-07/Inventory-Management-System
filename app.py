# app.py
from flask import Flask, render_template, request, jsonify, redirect, url_for
import json
import os
from datetime import datetime
import uuid

app = Flask(__name__)

# Data storage paths
DATA_DIR = 'data'
PRODUCTS_FILE = os.path.join(DATA_DIR, 'products.json')
ORDERS_FILE = os.path.join(DATA_DIR, 'orders.json')

# Ensure data directory exists
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# Initialize data files if they don't exist
def initialize_data_files():
    if not os.path.exists(PRODUCTS_FILE):
        with open(PRODUCTS_FILE, 'w') as f:
            json.dump([], f)
    
    if not os.path.exists(ORDERS_FILE):
        with open(ORDERS_FILE, 'w') as f:
            json.dump([], f)

initialize_data_files()

# Helper functions for data operations
def load_data(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

def save_data(file_path, data):
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)

# Routes
@app.route('/')
def index():
    return render_template('index.html')

# FEATURE 1: Product Management
@app.route('/products')
def products():
    products_data = load_data(PRODUCTS_FILE)
    return render_template('products.html', products=products_data)

@app.route('/api/products', methods=['GET'])
def get_products():
    products_data = load_data(PRODUCTS_FILE)
    return jsonify(products_data)

@app.route('/api/products', methods=['POST'])
def add_product():
    data = request.get_json()
    products_data = load_data(PRODUCTS_FILE)
    
    # Generate unique ID
    product_id = str(uuid.uuid4())
    
    new_product = {
        'id': product_id,
        'name': data['name'],
        'description': data.get('description', ''),
        'quantity': int(data['quantity']),
        'price': float(data['price']),
        'low_stock_threshold': int(data.get('low_stock_threshold', 10)),
        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    products_data.append(new_product)
    save_data(PRODUCTS_FILE, products_data)
    
    return jsonify({'success': True, 'product': new_product})

@app.route('/api/products/<product_id>', methods=['PUT'])
def update_product(product_id):
    data = request.get_json()
    products_data = load_data(PRODUCTS_FILE)
    
    for i, product in enumerate(products_data):
        if product['id'] == product_id:
            products_data[i]['name'] = data.get('name', product['name'])
            products_data[i]['description'] = data.get('description', product['description'])
            products_data[i]['quantity'] = int(data.get('quantity', product['quantity']))
            products_data[i]['price'] = float(data.get('price', product['price']))
            products_data[i]['low_stock_threshold'] = int(data.get('low_stock_threshold', product['low_stock_threshold']))
            products_data[i]['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            save_data(PRODUCTS_FILE, products_data)
            return jsonify({'success': True, 'product': products_data[i]})
    
    return jsonify({'success': False, 'error': 'Product not found'}), 404

@app.route('/api/products/<product_id>', methods=['DELETE'])
def delete_product(product_id):
    products_data = load_data(PRODUCTS_FILE)
    
    for i, product in enumerate(products_data):
        if product['id'] == product_id:
            deleted_product = products_data.pop(i)
            save_data(PRODUCTS_FILE, products_data)
            return jsonify({'success': True, 'product': deleted_product})
    
    return jsonify({'success': False, 'error': 'Product not found'}), 404

# FEATURE 2: Stock Management
@app.route('/inventory')
def inventory():
    products_data = load_data(PRODUCTS_FILE)
    return render_template('inventory.html', products=products_data)

@app.route('/api/low-stock')
def get_low_stock():
    products_data = load_data(PRODUCTS_FILE)
    low_stock_products = [
        product for product in products_data
        if product['quantity'] <= product['low_stock_threshold']
    ]
    return jsonify(low_stock_products)

@app.route('/api/products/<product_id>/adjust-stock', methods=['POST'])
def adjust_stock(product_id):
    data = request.get_json()
    products_data = load_data(PRODUCTS_FILE)
    
    for i, product in enumerate(products_data):
        if product['id'] == product_id:
            # Adjust stock quantity
            adjustment = int(data.get('adjustment', 0))
            products_data[i]['quantity'] += adjustment
            
            # Ensure quantity doesn't go below zero
            if products_data[i]['quantity'] < 0:
                products_data[i]['quantity'] = 0
            
            products_data[i]['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            save_data(PRODUCTS_FILE, products_data)
            
            return jsonify({
                'success': True, 
                'product': products_data[i],
                'is_low_stock': products_data[i]['quantity'] <= products_data[i]['low_stock_threshold']
            })
    
    return jsonify({'success': False, 'error': 'Product not found'}), 404

# FEATURE 3: Order Processing
@app.route('/orders')
def orders():
    orders_data = load_data(ORDERS_FILE)
    products_data = load_data(PRODUCTS_FILE)
    return render_template('orders.html', orders=orders_data, products=products_data)

@app.route('/api/orders', methods=['GET'])
def get_orders():
    orders_data = load_data(ORDERS_FILE)
    return jsonify(orders_data)

@app.route('/api/orders', methods=['POST'])
def create_order():
    data = request.get_json()
    orders_data = load_data(ORDERS_FILE)
    products_data = load_data(PRODUCTS_FILE)
    
    # Generate unique ID
    order_id = str(uuid.uuid4())
    
    # Verify items and adjust stock
    order_items = data['items']
    total_amount = 0
    
    for item in order_items:
        product_id = item['product_id']
        quantity = int(item['quantity'])
        
        # Find product
        for i, product in enumerate(products_data):
            if product['id'] == product_id:
                # Verify stock availability
                if product['quantity'] < quantity:
                    return jsonify({
                        'success': False, 
                        'error': f"Insufficient stock for {product['name']}. Available: {product['quantity']}"
                    }), 400
                
                # Update item with product details
                item['name'] = product['name']
                item['price'] = product['price']
                item['subtotal'] = product['price'] * quantity
                
                # Add to total amount
                total_amount += item['subtotal']
                
                # Adjust stock
                products_data[i]['quantity'] -= quantity
                break
    
    # Create order
    new_order = {
        'id': order_id,
        'items': order_items,
        'total_amount': total_amount,
        'customer_name': data.get('customer_name', 'Guest'),
        'status': 'pending',
        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    # Save data
    orders_data.append(new_order)
    save_data(ORDERS_FILE, orders_data)
    save_data(PRODUCTS_FILE, products_data)
    
    return jsonify({'success': True, 'order': new_order})

@app.route('/api/orders/<order_id>/status', methods=['PUT'])
def update_order_status(order_id):
    data = request.get_json()
    orders_data = load_data(ORDERS_FILE)
    
    for i, order in enumerate(orders_data):
        if order['id'] == order_id:
            orders_data[i]['status'] = data['status']
            orders_data[i]['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            save_data(ORDERS_FILE, orders_data)
            return jsonify({'success': True, 'order': orders_data[i]})
    
    return jsonify({'success': False, 'error': 'Order not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)