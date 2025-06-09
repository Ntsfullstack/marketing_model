#!/usr/bin/env python3
"""
Hệ thống Quản lý Khuyến mãi với AI - Phiên bản SQL Server
Sử dụng SQL Server thay vì SQLite
"""

import pandas as pd
import numpy as np
import os
import sys
from datetime import datetime, timedelta
import pyodbc
from sqlserver_config import SQLSERVER_CONFIG

# Import AI models
from ai_models import PromotionAnalyzer

class PromotionManager:
    def __init__(self):
        self.data_folder = "data"
        self.config = SQLSERVER_CONFIG
        self.ai_analyzer = PromotionAnalyzer()
        
        # Tạo thư mục data nếu chưa có
        if not os.path.exists(self.data_folder):
            os.makedirs(self.data_folder)
        
        # Setup database
        self.setup_database()
        
        # Load dữ liệu
        self.load_data_from_excel()
        
        # Train AI models
        self.train_ai_models()
    
    def create_connection_string(self):
        """Tạo connection string cho SQL Server"""
        config = self.config.copy()
        
        # Tạo connection string
        conn_str = f"DRIVER={{{config['driver']}}};"
        conn_str += f"SERVER={config['server']};"
        conn_str += f"PORT={config['port']};"
        
        if 'trusted_connection' in config and config['trusted_connection'] == 'yes':
            conn_str += "Trusted_Connection=yes;"
        else:
            conn_str += f"UID={config.get('uid', 'sa')};"
            conn_str += f"PWD={config.get('pwd', '')};"
        
        conn_str += f"DATABASE={config['database']};"
        return conn_str
    
    def setup_database(self):
        """Setup SQL Server database"""
        try:
            print("🔧 Thiết lập SQL Server Database...")
            
            # Kết nối đến SQL Server
            conn_str = self.create_connection_string()
            conn = pyodbc.connect(conn_str)
            cursor = conn.cursor()
            
            # Kiểm tra kết nối
            cursor.execute("SELECT @@VERSION")
            version = cursor.fetchone()
            print(f"✅ Kết nối SQL Server thành công!")
            print(f"📊 SQL Server Version: {version[0][:50]}...")
            
            conn.close()
            
        except Exception as e:
            print(f"❌ Lỗi kết nối SQL Server: {e}")
            print("💡 Hãy chạy: python setup_sqlserver.py để setup database")
            sys.exit(1)
    
    def load_data_from_excel(self):
        """Load dữ liệu từ file Excel vào SQL Server"""
        # Đường dẫn file Excel
        excel_file = os.path.join(self.data_folder, "rich_sample_data.xlsx")
        
        if not os.path.exists(excel_file):
            print(f"❌ File Excel không tồn tại: {excel_file}")
            print("💡 Hãy tạo file Excel mẫu trước")
            return
        
        try:
            print(f"📊 Load dữ liệu từ Excel: {excel_file}")
            
            # Kết nối đến database
            conn_str = self.create_connection_string()
            conn = pyodbc.connect(conn_str)
            cursor = conn.cursor()
            
            # Đọc dữ liệu từ Excel
            products_df = pd.read_excel(excel_file, sheet_name='Products')
            promotions_df = pd.read_excel(excel_file, sheet_name='Promotions')
            sales_df = pd.read_excel(excel_file, sheet_name='Sales')
            
            # Xóa dữ liệu cũ
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
            
        except Exception as e:
            print(f"❌ Lỗi khi load dữ liệu: {e}")
    
    def get_all_data(self):
        """Lấy tất cả dữ liệu từ SQL Server"""
        try:
            conn_str = self.create_connection_string()
            conn = pyodbc.connect(conn_str)
            
            # Lấy dữ liệu từ các bảng
            products_df = pd.read_sql("SELECT * FROM products", conn)
            promotions_df = pd.read_sql("SELECT * FROM promotions", conn)
            sales_df = pd.read_sql("SELECT * FROM sales", conn)
            
            conn.close()
            
            return products_df, promotions_df, sales_df
            
        except Exception as e:
            print(f"❌ Lỗi khi lấy dữ liệu: {e}")
            return None, None, None
    
    def train_ai_models(self):
        """Train AI models với dữ liệu từ SQL Server"""
        print("🚀 Training AI Models...")
        print("=" * 50)
        
        # Lấy dữ liệu
        products_df, promotions_df, sales_df = self.get_all_data()
        
        if products_df is None or promotions_df is None or sales_df is None:
            print("❌ Không thể lấy dữ liệu để train models")
            return
        
        # Train AI models
        self.ai_analyzer.train_models(products_df, promotions_df, sales_df)
    
    def show_data(self):
        """Hiển thị tất cả dữ liệu"""
        products_df, promotions_df, sales_df = self.get_all_data()
        
        if products_df is None:
            return
        
        print("\n📦 PRODUCTS:")
        print(products_df.to_string(index=False))
        
        print("\n🎯 PROMOTIONS:")
        print(promotions_df.to_string(index=False))
        
        print("\n💰 SALES:")
        print(sales_df.head(10).to_string(index=False))
        if len(sales_df) > 10:
            print(f"... và {len(sales_df) - 10} records khác")
    
    def add_data(self):
        """Thêm dữ liệu mới"""
        print("\n➕ THÊM DỮ LIỆU MỚI")
        print("1. Thêm sản phẩm")
        print("2. Thêm khuyến mãi")
        print("3. Thêm giao dịch")
        
        choice = input("Chọn loại dữ liệu (1-3): ")
        
        try:
            conn_str = self.create_connection_string()
            conn = pyodbc.connect(conn_str)
            cursor = conn.cursor()
            
            if choice == "1":
                name = input("Tên sản phẩm: ")
                price = float(input("Giá: "))
                category = input("Danh mục: ")
                
                cursor.execute("""
                    INSERT INTO products (name, price, category) 
                    VALUES (?, ?, ?)
                """, (name, price, category))
                
                print("✅ Đã thêm sản phẩm!")
                
            elif choice == "2":
                name = input("Tên khuyến mãi: ")
                discount = float(input("Giảm giá (%): "))
                product_id = int(input("ID sản phẩm: "))
                
                cursor.execute("""
                    INSERT INTO promotions (name, discount, product_id, active) 
                    VALUES (?, ?, ?, ?)
                """, (name, discount, product_id, True))
                
                print("✅ Đã thêm khuyến mãi!")
                
            elif choice == "3":
                product_id = int(input("ID sản phẩm: "))
                promotion_id = input("ID khuyến mãi (Enter để bỏ trống): ")
                quantity = int(input("Số lượng: "))
                revenue = float(input("Doanh thu: "))
                date = input("Ngày (YYYY-MM-DD): ")
                
                promotion_id = int(promotion_id) if promotion_id else None
                
                cursor.execute("""
                    INSERT INTO sales (product_id, promotion_id, quantity, revenue, date) 
                    VALUES (?, ?, ?, ?, ?)
                """, (product_id, promotion_id, quantity, revenue, date))
                
                print("✅ Đã thêm giao dịch!")
            
            conn.commit()
            conn.close()
            
            # Train lại AI models
            self.train_ai_models()
            
        except Exception as e:
            print(f"❌ Lỗi: {e}")
    
    def basic_analysis(self):
        """Phân tích cơ bản"""
        products_df, promotions_df, sales_df = self.get_all_data()
        
        if products_df is None:
            return
        
        print("\n📊 PHÂN TÍCH CƠ BẢN")
        print("=" * 30)
        
        # Thống kê tổng quan
        total_revenue = sales_df['revenue'].sum()
        total_sales = len(sales_df)
        avg_revenue = sales_df['revenue'].mean()
        
        print(f"💰 Tổng doanh thu: ${total_revenue:,.2f}")
        print(f"📈 Tổng giao dịch: {total_sales}")
        print(f"📊 Doanh thu trung bình: ${avg_revenue:,.2f}")
        
        # Doanh thu theo sản phẩm
        print("\n🏆 TOP SẢN PHẨM:")
        product_revenue = sales_df.groupby('product_id')['revenue'].sum().sort_values(ascending=False)
        for product_id, revenue in product_revenue.head(5).items():
            product_name = products_df[products_df['id'] == product_id]['name'].iloc[0]
            print(f"   {product_name}: ${revenue:,.2f}")
        
        # Doanh thu theo khuyến mãi
        print("\n🎯 HIỆU QUẢ KHUYẾN MÃI:")
        promo_sales = sales_df[sales_df['promotion_id'].notna()]
        if len(promo_sales) > 0:
            promo_revenue = promo_sales.groupby('promotion_id')['revenue'].sum().sort_values(ascending=False)
            for promo_id, revenue in promo_revenue.head(3).items():
                promo_name = promotions_df[promotions_df['id'] == promo_id]['name'].iloc[0]
                print(f"   {promo_name}: ${revenue:,.2f}")
    
    def ai_analysis(self):
        """Phân tích AI"""
        while True:
            print("\n🤖 AI ANALYSIS")
            print("1. Revenue Prediction")
            print("2. Promotion Success Analysis")
            print("3. Time Series Forecasting")
            print("4. Price Optimization")
            print("5. Back to Main Menu")
            
            choice = input("Chọn phân tích (1-5): ")
            
            if choice == "1":
                self.ai_analyzer.revenue_prediction()
            elif choice == "2":
                self.ai_analyzer.promotion_success_analysis()
            elif choice == "3":
                self.ai_analyzer.time_series_forecasting()
            elif choice == "4":
                self.ai_analyzer.price_optimization()
            elif choice == "5":
                break
            else:
                print("❌ Lựa chọn không hợp lệ")
    
    def export_to_excel(self):
        """Xuất dữ liệu ra Excel"""
        products_df, promotions_df, sales_df = self.get_all_data()
        
        if products_df is None:
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"exported_data_{timestamp}.xlsx"
        filepath = os.path.join(self.data_folder, filename)
        
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            products_df.to_excel(writer, sheet_name='Products', index=False)
            promotions_df.to_excel(writer, sheet_name='Promotions', index=False)
            sales_df.to_excel(writer, sheet_name='Sales', index=False)
        
        print(f"✅ Đã xuất dữ liệu ra: {filepath}")
    
    def run(self):
        """Chạy hệ thống"""
        print("🚀 Hệ thống Quản lý Khuyến mãi với AI - SQL Server")
        print("=" * 60)
        
        while True:
            print("\n🎮 MENU CHÍNH")
            print("1. Xem dữ liệu")
            print("2. Thêm dữ liệu")
            print("3. Phân tích cơ bản")
            print("4. AI Analysis")
            print("5. Export Excel")
            print("6. Thoát")
            
            choice = input("\nChọn chức năng (1-6): ")
            
            if choice == "1":
                self.show_data()
            elif choice == "2":
                self.add_data()
            elif choice == "3":
                self.basic_analysis()
            elif choice == "4":
                self.ai_analysis()
            elif choice == "5":
                self.export_to_excel()
            elif choice == "6":
                print("👋 Tạm biệt!")
                break
            else:
                print("❌ Lựa chọn không hợp lệ")

if __name__ == "__main__":
    manager = PromotionManager()
    manager.run() 