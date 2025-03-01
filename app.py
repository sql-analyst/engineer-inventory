from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import pandas as pd
import os
import json

app = Flask(__name__)
app.secret_key = 'engineering_inventory_secret_key'  # Required for session

# Define the base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Load data from Excel file
def load_inventory_data():
    excel_path = os.path.join(BASE_DIR, 'data', 'Stock.csv')
    try:
        df = pd.read_csv(excel_path)
        # Ensure column names match your Excel file
        df.columns = ['Code', 'Description', 'Quantity', 'Type']
        return df
    except Exception as e:
        print(f"Error loading Excel file: {e}")
        return pd.DataFrame(columns=['Code', 'Description', 'Quantity', 'Type'])

@app.route('/', methods=['GET'])
def home():
    df = load_inventory_data()
    search_query = request.args.get('search', '').lower()
    type_filter = request.args.get('type', '')
    
    # Get unique types for dropdown
    unique_types = sorted(df['Type'].unique())
    
    if search_query or type_filter:
        # Initialize mask for filtering
        mask = pd.Series(True, index=df.index)
        
        # Apply search filter if exists
        if search_query:
            mask &= (
                df['Code'].str.lower().str.contains(search_query) |
                df['Description'].str.lower().str.contains(search_query)
            )
        
        # Apply type filter if selected
        if type_filter:
            mask &= (df['Type'] == type_filter)
            
        results = df[mask]
    else:
        results = pd.DataFrame()
        
    return render_template('index.html', 
                         results=results.to_dict('records'), 
                         types=unique_types,
                         selected_type=type_filter)

@app.route('/enquiry', methods=['POST'])
def enquiry():
    # Get the selected item codes from the form
    selected_items = request.form.getlist('selected_items')
    
    # If no items selected, redirect back to home
    if not selected_items:
        return redirect(url_for('home'))
    
    # Load the inventory data to get details of selected items
    df = load_inventory_data()
    
    # Filter the dataframe to get only selected items
    selected_df = df[df['Code'].isin(selected_items)]
    
    # Create a text representation for the message field
    selected_items_text = "I would like to enquire about the following items:\n\n"
    for index, item in selected_df.iterrows():
        selected_items_text += f"- {item['Code']}: {item['Description']} ({item['Type']})\n"
    
    # Store selected items in JSON format for potential further processing
    selected_items_json = json.dumps(selected_df.to_dict('records'))
    
    return render_template('enquiry.html', 
                         selected_items_text=selected_items_text,
                         selected_items_json=selected_items_json)

@app.route('/submit_enquiry', methods=['POST'])
def submit_enquiry():
    # In a real application, you would process the form data here
    # For example, save to database or send email
    flash('Your enquiry has been submitted successfully!')
    return redirect(url_for('home'))

@app.route('/space')
def space():
    return render_template('space.html')

if __name__ == '__main__':
    app.run(debug=True)