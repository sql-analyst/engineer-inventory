import pymysql
import pandas as pd
from configparser import ConfigParser
import os

# Define the base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def get_db_config():
    """Read database configuration from config file."""
    config = ConfigParser()
    config_path = os.path.join(BASE_DIR, 'config.ini')

    # Check if config file exists
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")
    
    config.read(config_path)
    
    if 'database' not in config:
        raise KeyError("Database section not found in config file")
    
    return {
        'host': config['database'].get('host', 'localhost'),
        'user': config['database'].get('user', 'root'),
        'password': config['database'].get('password', ''),
        'db': config['database'].get('db', 'inventory'),
        'port': config['database'].getint('port', 3306)
    }

def connect_to_db():
    """Connect to the database using configuration values."""
    try:
        config = get_db_config()
        connection = pymysql.connect(
            host=config['host'],
            user=config['user'],
            password=config['password'],
            database=config['db'],
            port=config['port'],
            cursorclass=pymysql.cursors.DictCursor
        )
        return connection
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

def test_connection():
    """Test the database connection and return a sample query result."""
    conn = connect_to_db()
    if conn:
        try:
            with conn.cursor() as cursor:
                sql = "SELECT 1"
                cursor.execute(sql)
                result = cursor.fetchall()
                
                # Check if the query returned a result
                if result:
                    print("Connection successful!")
                    return True
                else:
                    return False
        except Exception as e:
            print(f"Connection error: {e}")
            return False
        finally:
            if conn:
                conn.close()
    else:
        print("Failed to connect to database")
        return False

def search_products(search_term='', category=''):
    """
    Search products based on search term and/or category.
    Returns a pandas DataFrame with the results.
    """
    conn = connect_to_db()
    if not conn:
        print("Failed to connect to database")
        return pd.DataFrame(columns=['ID', 'product', 'quantity', 'category', 'active'])
    
    try:
        with conn.cursor() as cursor:
            # Base query
            sql = "SELECT * FROM products WHERE 1=1"  # 1=1 allows for flexible WHERE clause building
            params = []
            
            # Add search term condition if provided
            if search_term:
                sql += " AND (UPPER(product) LIKE UPPER(%s) OR ID LIKE UPPER(%s))"
                search_param = f"%{search_term}%"
                params.extend([search_param, search_param])
            
            # Add category condition if provided
            if category:
                sql += " AND category = %s"
                params.append(category)
            
            # Execute query
            cursor.execute(sql, params)
            result = cursor.fetchall()
            
            # Convert to DataFrame
            df = pd.DataFrame(result)
            
            # Rename columns to match the expected format in the app
            if not df.empty:
                df = df.rename(columns={
                    'ID': 'Code',
                    'product': 'Description',
                    'quantity': 'Quantity',
                    'category': 'Type'
                })
                
                # Filter out inactive products
                if 'active' in df.columns:
                    df = df[df['active'] == 1]
                    df = df.drop('active', axis=1)
            
            return df
    except Exception as e:
        print(f"Query error: {e}")
        return pd.DataFrame(columns=['Code', 'Description', 'Quantity', 'Type'])
    finally:
        conn.close()

# Add these functions to your existing db.py file

def get_all_products():
    """
    Get all products from the database.
    Returns a pandas DataFrame with all products.
    """
    conn = connect_to_db()
    if not conn:
        print("Failed to connect to database")
        return pd.DataFrame(columns=['Code', 'Description', 'Quantity', 'Type'])
    
    try:
        with conn.cursor() as cursor:
            # Get all active products
            sql = "SELECT ID, product, quantity, category FROM products WHERE active = 1"
            cursor.execute(sql)
            result = cursor.fetchall()
            
            # Convert to DataFrame
            df = pd.DataFrame(result)
            
            # Rename columns to match the expected format in the app
            if not df.empty:
                df = df.rename(columns={
                    'ID': 'Code',
                    'product': 'Description',
                    'quantity': 'Quantity',
                    'category': 'Type'
                })
            
            return df
    except Exception as e:
        print(f"Query error: {e}")
        return pd.DataFrame(columns=['Code', 'Description', 'Quantity', 'Type'])
    finally:
        conn.close()

def update_product_in_db(product_id, description, quantity, product_type):
    """
    Update a product in the database.
    Returns True if successful, False otherwise.
    """
    conn = connect_to_db()
    if not conn:
        print("Failed to connect to database")
        return False
    
    try:
        with conn.cursor() as cursor:
            # Update the product
            sql = """
            UPDATE products 
            SET product = %s, quantity = %s, category = %s 
            WHERE ID = %s
            """
            cursor.execute(sql, (description, quantity, product_type, product_id))
            
            # Commit the changes
            conn.commit()
            
            # Check if any rows were affected
            affected_rows = cursor.rowcount
            return affected_rows > 0
    except Exception as e:
        print(f"Update error: {e}")
        return False
    finally:
        conn.close()

def add_product_to_db(description, quantity, product_type):
    """
    Add a new product to the database.
    Returns True if successful, False otherwise.
    """
    conn = connect_to_db()
    if not conn:
        print("Failed to connect to database")
        return False
    
    try:
        with conn.cursor() as cursor:
            # Insert the new product
            sql = """
            INSERT INTO products (product, quantity, category, active) 
            VALUES (%s, %s, %s, 1)
            """
            cursor.execute(sql, (description, quantity, product_type))
            
            # Commit the changes
            conn.commit()
            
            # Check if any rows were affected
            affected_rows = cursor.rowcount
            return affected_rows > 0
    except Exception as e:
        print(f"Insert error: {e}")
        return False
    finally:
        conn.close()

# Example usage (will run when the script is executed directly)
if __name__ == "__main__":
    test_connection()
