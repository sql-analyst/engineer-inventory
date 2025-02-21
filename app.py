from flask import Flask, render_template, request
import pandas as pd
import os

app = Flask(__name__)

# Define the base directory
#BASE_DIR = r"C:\Users\sross\OneDrive\Documents\Consulting\Engineer_marketplace_flask"
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

@app.route('/space')
def space():
    return render_template('space.html')

if __name__ == '__main__':
    app.run(debug=True)