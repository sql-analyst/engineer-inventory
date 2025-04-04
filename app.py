from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import pandas as pd
import os
import json
import functools
from env_cred import app_secret_key  # Import from env_cred.py

app = Flask(__name__)
app.secret_key = app_secret_key  # Use environment variable instead of hardcoded value

# Define the base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Correct password - Consider moving this to environment variables as well
CORRECT_PASSWORD = "engineerPWD"

# Login required decorator
def login_required(func):
    @functools.wraps(func)
    def secure_function(*args, **kwargs):
        if "logged_in" not in session:
            return redirect(url_for('login'))
        return func(*args, **kwargs)
    return secure_function

# Load data from AWS SQL db
def load_inventory_data(search_query='', type_filter=''):
    from db_equipment_inventory import search_products
    
    # Use the search_products function to get data from the database
    df = search_products(search_term=search_query, category=type_filter)
    
    # If DataFrame is empty, return empty DataFrame with correct columns
    if df.empty:
        return pd.DataFrame(columns=['Code', 'Description', 'Price', 'Type'])
    
    return df

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        password = request.form.get('password')
        if password == CORRECT_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('home'))
        else:
            error = 'Invalid password. Please try again.'
    
    # If GET request or invalid login
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/', methods=['GET'])
@login_required
def home():
    search_query = request.args.get('search', '').lower()
    type_filter = request.args.get('type', '')
    
    # Load data from database with search parameters
    df = load_inventory_data(search_query, type_filter)
    
    # Get unique types for dropdown
    unique_types = sorted(df['Type'].unique()) if not df.empty else []
    
    # If there's a search or filter, we already have filtered results
    if search_query or type_filter:
        results = df
        # Add image URLs using S3
        from s3_utils import get_product_image_url
        df['ImageUrl'] = df['Code'].apply(lambda x: get_product_image_url(str(x)))        
    else:
        # If no search or filter, show empty results
        results = pd.DataFrame()
        
    return render_template('index.html', 
                         results=results.to_dict('records'), 
                         types=unique_types,
                         selected_type=type_filter)

@app.route('/enquiry', methods=['POST'])
@login_required
def enquiry():
    # Get the selected item codes from the form
    selected_items = request.form.getlist('selected_items')
    
    # Debug logging
    print("Selected items (raw):", selected_items)
    
    # If no items selected, redirect back to home
    if not selected_items:
        print("No items selected")
        return redirect(url_for('home'))
    
    # Convert selected_items from strings to integers
    selected_items_int = []
    try:
        selected_items_int = [int(item) for item in selected_items]
        print("Selected items (converted to int):", selected_items_int)
    except ValueError as e:
        print(f"Error converting to integers: {e}")
        # If conversion fails, use the original strings
        selected_items_int = selected_items
    
    # Load the inventory data to get details of selected items
    df = load_inventory_data()
    
    # Debug the dataframe
    print("DataFrame columns:", df.columns)
    print("DataFrame dtypes:", df.dtypes)
    print("First few rows:", df.head())
    
    # Filter the dataframe to get only selected items
    # Try both string and integer comparison
    try:
        # Try with integers first
        selected_df = df[df['Code'].isin(selected_items_int)]
        print("Selected DataFrame using integers:", selected_df)
        
        # If no results, try with strings
        if selected_df.empty:
            print("No results with integer comparison, trying string comparison")
            # Convert 'Code' column to string type
            df['Code'] = df['Code'].astype(str)
            selected_df = df[df['Code'].isin(selected_items)]
            print("Selected DataFrame using strings:", selected_df)
    except Exception as e:
        print(f"Error filtering DataFrame: {e}")
        selected_df = pd.DataFrame(columns=df.columns)
    
    # Create a text representation for the message field
    selected_items_text = "I would like to enquire about the following items:\n\n"
    
    if not selected_df.empty:
        for index, item in selected_df.iterrows():
            selected_items_text += f"- {item['Code']}: {item['Description']} ({item['Type']})\n"
    else:
        # Fallback if no matching items found in the DataFrame
        selected_items_text += "Items selected but details not found in inventory.\n"
        selected_items_text += f"Selected IDs: {', '.join(selected_items)}\n"
    
    print("Final message text:", selected_items_text)
    
    # Store selected items for potential further processing
    return render_template('enquiry.html', 
                         selected_items_text=selected_items_text)

@app.route('/submit_enquiry', methods=['POST'])
@login_required
def submit_enquiry():
    # In a real application, you would process the form data here
    # For example, save to database or send email
    flash('Your enquiry has been submitted successfully!')
    return redirect(url_for('home'))

@app.route('/all_products')
@login_required
def all_products():
    """Display all products with edit functionality"""
    # Load all products from the database
    try:
        from db_equipment_inventory import get_all_products
        products = get_all_products()
        print(len(products))
        print(products)
    except Exception as e:
        print(f"Error fetching products: {e}")
        products = []
    
    return render_template('all_products.html', products=products.to_dict('records'))

@app.route('/item_admin/<item_code>', methods=['GET'])
@app.route('/item_admin', methods=['GET'])
@login_required
def item_admin(item_code=None):
    """Display form to add or edit an equipment item"""
    # Default values for a new item
    item_data = {
        'item_code': '',
        'category': '',
        'sub_category': '',
        'category_description': '',
        'make': '',
        'model': '',
        'certification': '',
        'specification': '',
        'location': '',
        'price': ''
    }
    
    form_title = "Add New Equipment"
    
    # If item_code provided, fetch the existing item data
    if item_code:
        try:
            from db_equipment_inventory import get_item_by_code
            item_df = get_item_by_code(item_code)
            
            if not item_df.empty:
                # Convert the first row of the DataFrame to a dictionary
                row = item_df.iloc[0]
                item_data = {
                    'item_code': row['Item_Code'],
                    'category': row['Category'],
                    'sub_category': row['Sub_Category'],
                    'category_description': row['Category_Description'],
                    'make': row['Make'],
                    'model': row['Model'],
                    'certification': row['Certification'],
                    'specification': row['Specification'],
                    'location': row['Location'],
                    'price': row['Price']
                }
                form_title = "Edit Equipment"
        except Exception as e:
            print(f"Error fetching item details: {e}")
            flash(f"Error fetching item details: {str(e)}")
    
    return render_template('item_admin.html', 
                          form_title=form_title,
                          **item_data)  # Unpack the dictionary as template variables

@app.route('/submit_form', methods=['POST'])
@login_required
def submit_form():
    """Process the submitted item form (add or edit)"""
    try:
        # Extract form data
        item_code = request.form.get('item_code')
        category = request.form.get('category')
        sub_category = request.form.get('sub_category')
        category_description = request.form.get('category_description')
        make = request.form.get('make')
        model = request.form.get('model')
        certification = request.form.get('certification')
        specification = request.form.get('specification')
        location = request.form.get('location')
        price = request.form.get('price')
        
        # Create a dictionary of the form data
        item_data = {
            'Item_Code': item_code,
            'Category': category,
            'Sub_Category': sub_category,
            'Category_Description': category_description,
            'Make': make,
            'Model': model,
            'Certification': certification,
            'Specification': specification,
            'Location': location,
            'Price': price
        }
        
        # Determine if this is an add or update operation
        from db_equipment_inventory import add_or_update_item
        if item_code:  # If item_code exists, it's an update
            success = add_or_update_item(item_data, is_update=True)
            message = "Equipment updated successfully!"
        else:  # Otherwise it's a new item
            success = add_or_update_item(item_data, is_update=False)
            message = "New equipment added successfully!"
        
        if success:
            flash(message)
        else:
            flash("Error processing the form.")
            
    except Exception as e:
        print(f"Error submitting form: {e}")
        flash(f"Error: {str(e)}")
    
    return redirect(url_for('all_products'))

if __name__ == '__main__':
    app.run(debug=True)