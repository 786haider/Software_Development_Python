import sqlite3
import pandas as pd
import hashlib
from datetime import datetime, date
import shutil
import os

class DatabaseManager:
    def __init__(self, db_name="orders.db"):
        self.db_name = db_name
        self.init_database()
    
    def init_database(self):
        """Initialize database with required tables"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                email TEXT,
                full_name TEXT,
                role TEXT DEFAULT 'admin',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create orders table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_name TEXT NOT NULL,
                contact_no TEXT NOT NULL,
                item_type TEXT NOT NULL,
                quantity TEXT NOT NULL,
                quality TEXT NOT NULL,
                color TEXT NOT NULL,
                prize TEXT NOT NULL,
                provider TEXT NOT NULL,
                order_date TEXT NOT NULL,
                order_time TEXT NOT NULL,
                notes TEXT,
                status TEXT DEFAULT 'Active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create default admin user if not exists
        self._create_default_admin(cursor)
        
        conn.commit()
        conn.close()
    
    def _create_default_admin(self, cursor):
        """Create default admin user"""
        cursor.execute("SELECT COUNT(*) FROM users WHERE username = 'admin'")
        if cursor.fetchone()[0] == 0:
            # Default password is 'Haider786' - change this in production!
            password_hash = hashlib.sha256('Haider786'.encode()).hexdigest()
            cursor.execute('''
                INSERT INTO users (username, password_hash, email, full_name, role)
                VALUES (?, ?, ?, ?, ?)
            ''', ('admin', password_hash, 'haiderhussain536@gmail.com', 'Haider Hussain', 'Owner'))
    
    def verify_user(self, username, password):
        """Verify user credentials"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        cursor.execute('''
            SELECT id, username, email, full_name, role
            FROM users 
            WHERE username = ? AND password_hash = ?
        ''', (username, password_hash))
        
        user = cursor.fetchone()
        conn.close()
        return user
    
    def save_order(self, order_data):
        """Save new order to database"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            # Debug: Print what we're trying to save
            print(f"Saving order data: {order_data}")
            
            cursor.execute('''
                INSERT INTO orders (
                    client_name, contact_no, item_type, quantity, quality,
                    color, prize, provider, order_date, order_time, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', order_data)
            
            order_id = cursor.lastrowid
            print(f"Order saved with ID: {order_id}")
            
            conn.commit()
            conn.close()
            return order_id
        except Exception as e:
            print(f"Error saving order: {e}")
            if conn:
                conn.close()
            return None
    
    def get_all_orders(self, status=None):
        """Get all orders from database"""
        try:
            conn = sqlite3.connect(self.db_name)
            
            if status:
                query = "SELECT * FROM orders WHERE status = ? ORDER BY created_at DESC"
                df = pd.read_sql_query(query, conn, params=(status,))
            else:
                query = "SELECT * FROM orders WHERE status != 'Deleted' ORDER BY created_at DESC"
                df = pd.read_sql_query(query, conn)
            
            conn.close()
            
            # Debug: Print number of orders found
            print(f"Found {len(df)} orders")
            
            return df
        except Exception as e:
            print(f"Error fetching orders: {e}")
            if conn:
                conn.close()
            return pd.DataFrame()
    
    def get_order_by_id(self, order_id):
        """Get specific order by ID"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM orders WHERE id = ?", (order_id,))
            order = cursor.fetchone()
            
            conn.close()
            return order
        except Exception as e:
            print(f"Error fetching order: {e}")
            if conn:
                conn.close()
            return None
    
    def update_order(self, order_id, order_data):
        """Update existing order"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE orders SET
                    client_name = ?, contact_no = ?, item_type = ?, quantity = ?,
                    quality = ?, color = ?, prize = ?, provider = ?, order_date = ?,
                    order_time = ?, notes = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', order_data + (order_id,))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error updating order: {e}")
            if conn:
                conn.close()
            return False
    
    def delete_order(self, order_id):
        """Soft delete order (mark as deleted)"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE orders SET status = 'Deleted', updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (order_id,))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error deleting order: {e}")
            if conn:
                conn.close()
            return False
    
    def search_orders(self, search_term):
        """Search orders by various fields"""
        try:
            conn = sqlite3.connect(self.db_name)
            
            query = '''
                SELECT * FROM orders 
                WHERE status != 'Deleted' AND (
                    client_name LIKE ? OR 
                    contact_no LIKE ? OR 
                    item_type LIKE ? OR
                    provider LIKE ?
                )
                ORDER BY created_at DESC
            '''
            search_pattern = f"%{search_term}%"
            df = pd.read_sql_query(query, conn, params=(search_pattern, search_pattern, search_pattern, search_pattern))
            
            conn.close()
            return df
        except Exception as e:
            print(f"Error searching orders: {e}")
            if conn:
                conn.close()
            return pd.DataFrame()
    
    def get_dashboard_stats(self):
        """Get statistics for dashboard"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            # Total orders
            cursor.execute("SELECT COUNT(*) FROM orders WHERE status != 'Deleted'")
            total_orders = cursor.fetchone()[0]
            
            # Today's orders
            today = date.today().strftime('%Y-%m-%d')
            cursor.execute("SELECT COUNT(*) FROM orders WHERE order_date = ? AND status != 'Deleted'", (today,))
            orders_today = cursor.fetchone()[0]
            
            # This month's orders
            this_month = date.today().strftime('%Y-%m')
            cursor.execute("SELECT COUNT(*) FROM orders WHERE order_date LIKE ? AND status != 'Deleted'", (f"{this_month}%",))
            orders_this_month = cursor.fetchone()[0]
            
            # Total unique clients
            cursor.execute("SELECT COUNT(DISTINCT client_name) FROM orders WHERE status != 'Deleted'")
            total_clients = cursor.fetchone()[0]
            
            conn.close()
            
            stats = {
                'total_orders': total_orders,
                'orders_today': orders_today,
                'orders_this_month': orders_this_month,
                'total_clients': total_clients
            }
            
            # Debug: Print stats
            print(f"Dashboard stats: {stats}")
            
            return stats
        except Exception as e:
            print(f"Error getting dashboard stats: {e}")
            if conn:
                conn.close()
            return {
                'total_orders': 0,
                'orders_today': 0,
                'orders_this_month': 0,
                'total_clients': 0
            }
    
    def backup_database(self, backup_path):
        """Create database backup"""
        try:
            shutil.copy2(self.db_name, backup_path)
            return True
        except Exception as e:
            print(f"Error creating backup: {e}")
            return False
    
    def debug_database(self):
        """Debug function to check database contents"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            # Check if tables exist
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            print(f"Tables in database: {tables}")
            
            # Check orders table structure
            cursor.execute("PRAGMA table_info(orders);")
            columns = cursor.fetchall()
            print(f"Orders table columns: {columns}")
            
            # Check all orders
            cursor.execute("SELECT * FROM orders;")
            orders = cursor.fetchall()
            print(f"All orders in database: {orders}")
            
            conn.close()
        except Exception as e:
            print(f"Debug error: {e}")
            if conn:
                conn.close()