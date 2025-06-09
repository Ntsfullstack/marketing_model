#!/usr/bin/env python3
"""
Script setup SQL Server Database
Chạy: python setup_sqlserver.py
"""

import pyodbc
import pandas as pd
from sqlserver_config import SQLSERVER_CONFIG, CREATE_DATABASE_SQL, CREATE_TABLES_SQL
import os

def create_connection_string():
    """Tạo connection string cho SQL Server"""
    config = SQLSERVER_CONFIG.copy()
    
    # Tạo connection string
    conn_str = f"DRIVER={{{config['driver']}}};"
    conn_str += f"SERVER={config['server']};"
    conn_str += f"PORT={config['port']};"
    
    if 'trusted_connection' in config and config['trusted_connection'] == 'yes':
        conn_str += "Trusted_Connection=yes;"
    else:
        conn_str += f"UID={config.get('uid', 'sa')};"
        conn_str += f"PWD={config.get('pwd', '')};"
    
    return conn_str

def setup_database():
    """Setup database và tables"""
    try:
        print("🚀 Thiết lập SQL Server Database...")
        
        # Kết nối đến SQL Server (không chỉ định database)
        conn_str = create_connection_string()
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        
        # Tạo database
        print("📊 Tạo database 'promotions_db'...")
        cursor.execute(CREATE_DATABASE_SQL)
        conn.commit()
        print("✅ Database đã được tạo!")
        
        # Đóng connection cũ
        conn.close()
        
        # Kết nối đến database mới
        conn_str_with_db = conn_str + f"DATABASE={SQLSERVER_CONFIG['database']};"
        conn = pyodbc.connect(conn_str_with_db)
        cursor = conn.cursor()
        
        # Tạo tables
        print("📋 Tạo các bảng...")
        for statement in CREATE_TABLES_SQL.split(';'):
            if statement.strip():
                cursor.execute(statement)
        
        conn.commit()
        print("✅ Các bảng đã được tạo!")
        
        # Kiểm tra tables
        cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'")
        tables = cursor.fetchall()
        print(f"📊 Các bảng đã tạo: {[table[0] for table in tables]}")
        
        conn.close()
        print("🎉 Setup SQL Server Database hoàn tất!")
        
        return True
        
    except Exception as e:
        print(f"❌ Lỗi khi setup database: {e}")
        print("\n💡 Hướng dẫn khắc phục:")
        print("1. Đảm bảo SQL Server đang chạy")
        print("2. Kiểm tra connection string trong sqlserver_config.py")
        print("3. Đảm bảo đã cài ODBC Driver cho SQL Server")
        print("4. Kiểm tra quyền truy cập database")
        return False

def load_sample_data():
    """Load dữ liệu mẫu từ Excel vào SQL Server"""
    try:
        print("\n📊 Load dữ liệu mẫu từ Excel...")
        
        # Kết nối đến database
        conn_str = create_connection_string() + f"DATABASE={SQLSERVER_CONFIG['database']};"
        conn = pyodbc.connect(conn_str)
        
        # Đường dẫn file Excel
        excel_file = os.path.join("data", "rich_sample_data.xlsx")
        
        if not os.path.exists(excel_file):
            print(f"❌ File Excel không tồn tại: {excel_file}")
            return False
        
        # Đọc dữ liệu từ Excel
        products_df = pd.read_excel(excel_file, sheet_name='Products')
        promotions_df = pd.read_excel(excel_file, sheet_name='Promotions')
        sales_df = pd.read_excel(excel_file, sheet_name='Sales')
        
        # Xóa dữ liệu cũ
        cursor = conn.cursor()
        cursor.execute("DELETE FROM sales")
        cursor.execute("DELETE FROM promotions")
        cursor.execute("DELETE FROM products")
        cursor.execute("DBCC CHECKIDENT ('products', RESEED, 0)")
        cursor.execute("DBCC CHECKIDENT ('promotions', RESEED, 0)")
        cursor.execute("DBCC CHECKIDENT ('sales', RESEED, 0)")
        
        # Thêm dữ liệu Products
        for _, row in products_df.iterrows():
            cursor.execute("""
                INSERT INTO products (name, price, category) 
                VALUES (?, ?, ?)
            """, (row['name'], row['price'], row['category']))
        
        # Thêm dữ liệu Promotions
        for _, row in promotions_df.iterrows():
            cursor.execute("""
                INSERT INTO promotions (name, discount, product_id, active) 
                VALUES (?, ?, ?, ?)
            """, (row['name'], row['discount'], row['product_id'], row['active']))
        
        # Thêm dữ liệu Sales
        for _, row in sales_df.iterrows():
            cursor.execute("""
                INSERT INTO sales (product_id, promotion_id, quantity, revenue, date) 
                VALUES (?, ?, ?, ?, ?)
            """, (row['product_id'], row['promotion_id'], row['quantity'], row['revenue'], row['date']))
        
        conn.commit()
        conn.close()
        
        print(f"✅ Đã load {len(products_df)} sản phẩm")
        print(f"✅ Đã load {len(promotions_df)} khuyến mãi")
        print(f"✅ Đã load {len(sales_df)} giao dịch")
        
        return True
        
    except Exception as e:
        print(f"❌ Lỗi khi load dữ liệu: {e}")
        return False

if __name__ == "__main__":
    print("🎯 Setup SQL Server Database cho Hệ thống Quản lý Khuyến mãi")
    print("=" * 60)
    
    # Setup database
    if setup_database():
        # Load dữ liệu mẫu
        load_sample_data()
    
    print("\n📋 Hướng dẫn tiếp theo:")
    print("1. Cập nhật sqlserver_config.py nếu cần")
    print("2. Chạy: python simple_model.py")
    print("3. Hệ thống sẽ sử dụng SQL Server thay vì SQLite") 