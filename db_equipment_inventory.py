import pymysql
import pandas as pd
import os
from env_cred import host, user, password, db, port  # Import from env_cred.py

# Define the base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


#######################################################
##### CONFIG AND CONNECTIONS
#######################################################

def connect_to_db():
    """Connect to the database using environment variables."""
    try:
        connection = pymysql.connect(
            host=host,
            user=user,
            password=password,
            database=db,
            port=int(port) if port else 3306,
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

#######################################################
##### CLIENT SEARCH PAGE
#######################################################

def search_products(search_term='', category=''):
    """
    Search products based on search term and/or category.
    Returns a pandas DataFrame with the results.
    """
    conn = connect_to_db()
    if not conn:
        print("Failed to connect to database")
        return pd.DataFrame(columns=['ID', 'Code', 'Description', 'Price', 'Type', 'ImageUrl'])
    
    try:
        with conn.cursor() as cursor:
            # Base query
            sql = "SELECT * FROM equipment_inventory WHERE 1=1"  # 1=1 allows for flexible WHERE clause building
            params = []
            
            # Add search term condition if provided
            if search_term:
                sql += " AND (UPPER(Category_Description) LIKE UPPER(%s) OR UPPER(Make) LIKE UPPER(%s))"
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
            
            # Rename columns to match the expected format
            if not df.empty:
                # Use appropriate column mappings for the equipment_inventory table
                df = df.rename(columns={
                    'Item_Code': 'Code',
                    'Category_Description': 'Description',
                    'Category': 'Type'
                })
                           
            return df#[['Code', 'Description', 'Price', 'Type', 'ImageUrl']]
    except Exception as e:
        print(f"Query error: {e}")
        return pd.DataFrame(columns=['Code', 'Description', 'Price', 'Type', 'ImageUrl'])
    finally:
        conn.close()

#######################################################
##### ADMIN SEARCH AND EDIT PAGES
#######################################################

def get_all_products():
    """
    Get all products from the database.
    Returns a pandas DataFrame with all products.
    """
    conn = connect_to_db()
    if not conn:
        print("Failed to connect to database")
        return pd.DataFrame(columns=['Code', 'Description', 'Price', 'Type'])
    
    try:
        with conn.cursor() as cursor:
            # Get all active products
            sql = "SELECT * FROM equipment_inventory"
            cursor.execute(sql)
            result = cursor.fetchall()
            
            # Convert to DataFrame
            df = pd.DataFrame(result)
            # If the query returns column names, assign them as DataFrame columns
            if cursor.description:
                df.columns = [desc[0] for desc in cursor.description]            
            # Rename columns to match the expected format in the app
            if not df.empty:
                df = df.rename(columns={
                    'Item_Code': 'Code',
                    'Category_Description': 'Description',
                    'Category': 'Type'
                })
            
            return df[['Code', 'Description', 'Price', 'Type']]
    except Exception as e:
        print(f"Query error: {e}")
        return pd.DataFrame(columns=['Code', 'Description', 'Price', 'Type'])
    finally:
        conn.close()


def get_item_by_code(item_code):
    """Fetch a specific item by its code"""
    conn = connect_to_db()
    if not conn:
        print("Failed to connect to database")
        return pd.DataFrame()
        
    try:
        # Use %s placeholder instead of ? for MySQL
        query = "SELECT * FROM equipment_inventory WHERE Item_Code = %s"
        with conn.cursor() as cursor:
            cursor.execute(query, (item_code,))
            result = cursor.fetchall()
            df = pd.DataFrame(result)
            
        return df
    except Exception as e:
        print(f"Database error: {e}")
        return pd.DataFrame()
    finally:
        conn.close()

def add_or_update_item(item_data, is_update=False):
    """Add a new item or update an existing item in the database"""
    conn = connect_to_db()
    if not conn:
        print("Failed to connect to database")
        return False
        
    try:
        with conn.cursor() as cursor:
            if is_update:
                # Update existing item - using %s placeholders for MySQL
                query = """
                UPDATE equipment_inventory
                SET Category = %s, Sub_Category = %s, Category_Description = %s,
                    Make = %s, Model = %s, Certification = %s, Specification = %s,
                    Location = %s, Price = %s
                WHERE Item_Code = %s
                """
                cursor.execute(query, (
                    item_data['Category'],
                    item_data['Sub_Category'],
                    item_data['Category_Description'],
                    item_data['Make'],
                    item_data['Model'],
                    item_data['Certification'],
                    item_data['Specification'],
                    item_data['Location'],
                    item_data['Price'],
                    item_data['Item_Code']
                ))
            else:
                # Add new item - first get the next available Item_Code if not provided
                if not item_data['Item_Code']:
                    cursor.execute("SELECT MAX(Item_Code) as max_id FROM equipment_inventory")
                    result = cursor.fetchone()
                    next_id = 1 if not result or result['max_id'] is None else result['max_id'] + 1
                    item_data['Item_Code'] = next_id
                
                # Insert the new item - using %s placeholders for MySQL
                query = """
                INSERT INTO equipment_inventory (
                    Item_Code, Category, Sub_Category, Category_Description,
                    Make, Model, Certification, Specification, Location, Price
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(query, (
                    item_data['Item_Code'],
                    item_data['Category'],
                    item_data['Sub_Category'],
                    item_data['Category_Description'],
                    item_data['Make'],
                    item_data['Model'],
                    item_data['Certification'],
                    item_data['Specification'],
                    item_data['Location'],
                    item_data['Price']
                ))
            
            conn.commit()
            return True
        
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Database error: {e}")
        return False
    
    finally:
        if conn:
            conn.close()

# Example usage (will run when the script is executed directly)
if __name__ == "__main__":
    test_connection()
