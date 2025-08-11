#!/usr/bin/env python3
"""
Complete Database Recovery Script for Hussain Construction Point
This script will fix the corrupted database and ensure the application works properly.
"""

import sqlite3
import os
import shutil
import hashlib
from datetime import datetime
import sys

class DatabaseRecoveryTool:
    def __init__(self, db_name="orders.db"):
        self.db_name = db_name
        self.backup_folder = "database_backups"
        
    def create_backup_folder(self):
        """Create backup folder if it doesn't exist"""
        if not os.path.exists(self.backup_folder):
            os.makedirs(self.backup_folder)
            print(f"✅ Created backup folder: {self.backup_folder}")
    
    def backup_corrupted_database(self):
        """Backup the corrupted database before deletion"""
        try:
            if os.path.exists(self.db_name):
                self.create_backup_folder()
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_name = f"{self.backup_folder}/corrupted_db_backup_{timestamp}.db"
                shutil.copy2(self.db_name, backup_name)
                print(f"🔄 Corrupted database backed up to: {backup_name}")
                return True
        except Exception as e:
            print(f"⚠️ Could not backup corrupted database: {e}")
            return False
    
    def remove_corrupted_files(self):
        """Remove all database-related files"""
        db_files = [
            self.db_name,
            f"{self.db_name}-wal",
            f"{self.db_name}-shm",
            f"{self.db_name}-journal"
        ]
        
        removed_count = 0
        for file_path in db_files:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    print(f"🗑️ Removed: {file_path}")
                    removed_count += 1
            except Exception as e:
                print(f"⚠️ Could not remove {file_path}: {e}")
        
        print(f"✅ Removed {removed_count} database files")
        return removed_count > 0
    
    def create_fresh_database(self):
        """Create a completely new database with proper structure"""
        try:
            print("🔨 Creating fresh database...")
            
            # Ensure no existing connection
            if os.path.exists(self.db_name):
                os.remove(self.db_name)
            
            # Create new database
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            # Enable foreign key constraints
            cursor.execute("PRAGMA foreign_keys = ON")
            
            # Create users table
            cursor.execute('''
                CREATE TABLE users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    email TEXT,
                    full_name TEXT,
                    role TEXT DEFAULT 'admin',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create orders table with improved structure
            cursor.execute('''
                CREATE TABLE orders (
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
                    status TEXT DEFAULT 'Active' CHECK(status IN ('Active', 'Completed', 'Cancelled', 'Deleted')),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create indexes for better performance
            cursor.execute('CREATE INDEX idx_orders_client_name ON orders(client_name)')
            cursor.execute('CREATE INDEX idx_orders_order_date ON orders(order_date)')
            cursor.execute('CREATE INDEX idx_orders_status ON orders(status)')
            cursor.execute('CREATE INDEX idx_orders_created_at ON orders(created_at)')
            
            # Create default admin user
            self._create_default_admin(cursor)
            
            # Create some sample data for testing
            self._create_sample_data(cursor)
            
            conn.commit()
            conn.close()
            
            print("✅ Fresh database created successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Error creating fresh database: {e}")
            return False
    
    def _create_default_admin(self, cursor):
        """Create the default admin user"""
        try:
            # Password: 'Haider786'
            password_hash = hashlib.sha256('Haider786'.encode()).hexdigest()
            cursor.execute('''
                INSERT INTO users (username, password_hash, email, full_name, role)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                'admin', 
                password_hash, 
                'haiderhussain536@gmail.com', 
                'Haider Hussain', 
                'Owner'
            ))
            print("👤 Default admin user created (username: admin, password: Haider786)")
        except Exception as e:
            print(f"⚠️ Error creating default admin: {e}")
    
    def _create_sample_data(self, cursor):
        """Create some sample orders for testing"""
        try:
            sample_orders = [
                (
                    "Ahmed Construction Co.", "03001234567", "Cement Bags", "50 bags", 
                    "Premium", "Grey", "Rs. 25000", "Cherat Cement", 
                    "2024-01-15", "10:30:00", "Urgent delivery required", "Completed"
                ),
                (
                    "Khan Builders", "03217654321", "Steel Rods", "100 pieces", 
                    "Standard", "Natural", "Rs. 45000", "Agha Steel", 
                    "2024-01-20", "14:15:00", "Grade 60 steel required", "Active"
                ),
                (
                    "Modern Homes", "03009876543", "Bricks", "10000 pieces", 
                    "Premium", "Red", "Rs. 35000", "Pak Brick Company", 
                    "2024-01-25", "09:00:00", "First class bricks only", "Active"
                )
            ]
            
            cursor.executemany('''
                INSERT INTO orders (
                    client_name, contact_no, item_type, quantity, quality,
                    color, prize, provider, order_date, order_time, notes, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', sample_orders)
            
            print("📋 Sample orders created for testing")
        except Exception as e:
            print(f"⚠️ Error creating sample data: {e}")
    
    def verify_database(self):
        """Verify the database is working correctly"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            # Test basic operations
            cursor.execute("SELECT COUNT(*) FROM users")
            user_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM orders")
            order_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            conn.close()
            
            print(f"✅ Database verification successful!")
            print(f"   - Tables: {', '.join(tables)}")
            print(f"   - Users: {user_count}")
            print(f"   - Orders: {order_count}")
            
            return True
        except Exception as e:
            print(f"❌ Database verification failed: {e}")
            return False
    
    def run_recovery(self):
        """Run the complete database recovery process"""
        print("🚀 Starting database recovery process...")
        print("=" * 50)
        
        # Step 1: Backup corrupted database
        print("Step 1: Backing up corrupted database...")
        self.backup_corrupted_database()
        
        # Step 2: Remove corrupted files
        print("\nStep 2: Removing corrupted files...")
        if not self.remove_corrupted_files():
            print("⚠️ No corrupted files found to remove")
        
        # Step 3: Create fresh database
        print("\nStep 3: Creating fresh database...")
        if not self.create_fresh_database():
            print("❌ Failed to create fresh database!")
            return False
        
        # Step 4: Verify database
        print("\nStep 4: Verifying database...")
        if not self.verify_database():
            print("❌ Database verification failed!")
            return False
        
        print("\n" + "=" * 50)
        print("🎉 Database recovery completed successfully!")
        print("🔑 Default login credentials:")
        print("   Username: admin")
        print("   Password: Haider786")
        print("\n💡 You can now run your Streamlit application!")
        
        return True

def main():
    """Main function to run the recovery tool"""
    print("🏗️ Hussain Construction Point - Database Recovery Tool")
    print("=" * 60)
    
    # Check if we're in the right directory
    required_files = ['app.py', 'database.py', 'config.py']
    missing_files = [f for f in required_files if not os.path.exists(f)]
    
    if missing_files:
        print(f"❌ Missing required files: {', '.join(missing_files)}")
        print("Please run this script from the application directory.")
        return False
    
    # Initialize recovery tool
    recovery_tool = DatabaseRecoveryTool()
    
    # Run recovery process
    success = recovery_tool.run_recovery()
    
    if success:
        print("\n🚀 Next steps:")
        print("1. Run: streamlit run app.py")
        print("2. Login with username 'admin' and password 'Haider786'")
        print("3. Start creating new orders!")
    else:
        print("\n❌ Recovery failed. Please check the error messages above.")
        print("If the problem persists, please contact technical support.")
    
    return success

if __name__ == "__main__":
    main()