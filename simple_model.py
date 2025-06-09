import pandas as pd
import numpy as np
import sqlite3
from datetime import datetime
import json
import os
from ai_models import AdvancedAIModels, create_visualizations

class AdvancedPromotionSystem:
    def __init__(self):
        """Khởi tạo hệ thống nâng cao"""
        self.db_path = "promotions.db"
        self.data_folder = "data"
        self.ai_models = AdvancedAIModels()
        self.init_database()
        self.load_data_from_excel()
        self.train_ai_models()
    
    def init_database(self):
        """Tạo database SQLite đơn giản"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tạo bảng Products
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                price REAL NOT NULL,
                category TEXT
            )
        ''')
        
        # Tạo bảng Promotions
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS promotions (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                discount REAL NOT NULL,
                product_id INTEGER,
                active BOOLEAN DEFAULT 1,
                FOREIGN KEY (product_id) REFERENCES products (id)
            )
        ''')
        
        # Tạo bảng Sales
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY,
                product_id INTEGER,
                promotion_id INTEGER,
                quantity INTEGER,
                revenue REAL,
                date TEXT,
                FOREIGN KEY (product_id) REFERENCES products (id),
                FOREIGN KEY (promotion_id) REFERENCES promotions (id)
            )
        ''')
        
        conn.commit()
        conn.close()
        print("✅ Database đã được tạo!")
    
    def load_data_from_excel(self):
        """Load dữ liệu từ file Excel"""
        # Tạo thư mục data nếu chưa có
        if not os.path.exists(self.data_folder):
            os.makedirs(self.data_folder)
            print(f"📁 Tạo thư mục {self.data_folder}")
    
        rich_excel_file = os.path.join(self.data_folder, "rich_sample_data.xlsx")
        excel_file = os.path.join(self.data_folder, "sample_data.xlsx")
        if os.path.exists(rich_excel_file):
            excel_file = rich_excel_file
            print(f"📊 Sử dụng dữ liệu phong phú: {rich_excel_file}")
        elif not os.path.exists(excel_file):
            print(f"📊 File Excel không tồn tại: {excel_file}")
            print("🔄 Tạo file Excel mẫu...")
            self.create_sample_excel(excel_file)
        
        try:
        
            print(f"📖 Đọc dữ liệu từ: {excel_file}")
            
            # Đọc từng sheet
            products_df = pd.read_excel(excel_file, sheet_name='Products')
            promotions_df = pd.read_excel(excel_file, sheet_name='Promotions')
            sales_df = pd.read_excel(excel_file, sheet_name='Sales')
            
            # Xóa dữ liệu cũ và thêm dữ liệu mới
            conn = sqlite3.connect(self.db_path)
            
            # Xóa dữ liệu cũ
            conn.execute("DELETE FROM sales")
            conn.execute("DELETE FROM promotions")
            conn.execute("DELETE FROM products")
            
            # Thêm dữ liệu Products
            products_df.to_sql('products', conn, if_exists='append', index=False)
            print(f"✅ Đã thêm {len(products_df)} sản phẩm")
            
            # Thêm dữ liệu Promotions
            promotions_df.to_sql('promotions', conn, if_exists='append', index=False)
            print(f"✅ Đã thêm {len(promotions_df)} khuyến mãi")
            
            # Thêm dữ liệu Sales
            sales_df.to_sql('sales', conn, if_exists='append', index=False)
            print(f"✅ Đã thêm {len(sales_df)} giao dịch")
            
            conn.commit()
            conn.close()
            
            print("🎉 Dữ liệu đã được load thành công từ Excel!")
            
        except Exception as e:
            print(f"❌ Lỗi khi đọc file Excel: {e}")
            print("🔄 Sử dụng dữ liệu mẫu...")
            self.load_sample_data()
    
    def create_sample_excel(self, excel_file):
        """Tạo file Excel mẫu với nhiều dữ liệu hơn"""
        try:
            products_data = {
                'id': [1, 2, 3, 4, 5, 6, 7, 8],
                'name': ['Laptop Gaming', 'Smartphone', 'Headphones', 'Shoes', 'T-shirt', 'Watch', 'Tablet', 'Camera'],
                'price': [1500, 800, 200, 120, 25, 300, 600, 450],
                'category': ['Electronics', 'Electronics', 'Electronics', 'Fashion', 'Fashion', 'Electronics', 'Electronics', 'Electronics']
            }
            
            promotions_data = {
                'id': [1, 2, 3, 4, 5, 6],
                'name': ['Giảm giá mùa hè', 'Flash Sale', 'Mua 2 tặng 1', 'Giảm giá Fashion', 'Black Friday', 'Cyber Monday'],
                'discount': [20, 15, 33, 25, 30, 40],
                'product_id': [1, 2, 3, 4, 1, 2],
                'active': [1, 1, 0, 1, 1, 1]
            }
            sales_data = {
                'id': list(range(1, 21)),
                'product_id': [1, 2, 1, 3, 4, 5, 1, 2, 3, 4, 5, 6, 7, 8, 1, 2, 3, 4, 5, 6],
                'promotion_id': [1, 2, None, 3, 4, None, 5, 6, None, 4, None, None, None, None, 1, 2, 3, 4, None, None],
                'quantity': [2, 1, 1, 3, 2, 5, 1, 2, 1, 3, 4, 1, 2, 1, 3, 1, 2, 1, 2, 1],
                'revenue': [2400, 680, 1500, 400, 180, 125, 1050, 1360, 200, 270, 100, 300, 1200, 450, 3600, 680, 400, 90, 50, 300],
                'date': ['2024-01-01', '2024-01-02', '2024-01-03', '2024-01-04', '2024-01-05', '2024-01-06', 
                        '2024-01-07', '2024-01-08', '2024-01-09', '2024-01-10', '2024-01-11', '2024-01-12',
                        '2024-01-13', '2024-01-14', '2024-01-15', '2024-01-16', '2024-01-17', '2024-01-18',
                        '2024-01-19', '2024-01-20']
            }
            
            # Tạo DataFrame
            products_df = pd.DataFrame(products_data)
            promotions_df = pd.DataFrame(promotions_data)
            sales_df = pd.DataFrame(sales_data)
            
            # Tạo file Excel với nhiều sheet
            with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
                products_df.to_excel(writer, sheet_name='Products', index=False)
                promotions_df.to_excel(writer, sheet_name='Promotions', index=False)
                sales_df.to_excel(writer, sheet_name='Sales', index=False)
            
            print(f"✅ Đã tạo file Excel mẫu: {excel_file}")
            print("📝 Bạn có thể chỉnh sửa file này để thay đổi dữ liệu!")
            
        except Exception as e:
            print(f"❌ Lỗi khi tạo file Excel: {e}")
            print("🔄 Sử dụng dữ liệu mẫu...")
            self.load_sample_data()
    
    def load_sample_data(self):
        """Load dữ liệu mẫu (fallback)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Kiểm tra xem đã có dữ liệu chưa
        cursor.execute("SELECT COUNT(*) FROM products")
        if cursor.fetchone()[0] == 0:
            # Thêm sản phẩm
            products = [
                (1, "Laptop Gaming", 1500, "Electronics"),
                (2, "Smartphone", 800, "Electronics"),
                (3, "Headphones", 200, "Electronics"),
                (4, "Shoes", 120, "Fashion"),
                (5, "T-shirt", 25, "Fashion"),
            ]
            cursor.executemany("INSERT INTO products VALUES (?, ?, ?, ?)", products)
    
            promotions = [
                (1, "Giảm giá mùa hè", 20, 1, 1),
                (2, "Flash Sale", 15, 2, 1),
                (3, "Mua 2 tặng 1", 33, 3, 0),
                (4, "Giảm giá Fashion", 25, 4, 1),
            ]
            cursor.executemany("INSERT INTO promotions VALUES (?, ?, ?, ?, ?)", promotions)
            
            # Thêm giao dịch
            sales = [
                (1, 1, 1, 2, 2400, "2024-01-01"),
                (2, 2, 2, 1, 680, "2024-01-02"),
                (3, 1, None, 1, 1500, "2024-01-03"),
                (4, 3, 3, 3, 400, "2024-01-04"),
                (5, 4, 4, 2, 180, "2024-01-05"),
                (6, 5, None, 5, 125, "2024-01-06"),
            ]
            cursor.executemany("INSERT INTO sales VALUES (?, ?, ?, ?, ?, ?)", sales)
            
            conn.commit()
            print("✅ Dữ liệu mẫu đã được tạo!")
        
        conn.close()
    
    def train_ai_models(self):
        """Train các mô hình AI"""
        try:
            products_df, promotions_df, sales_df = self.get_data()
            self.ai_models.train_all_models(products_df, promotions_df, sales_df)
            
            # Tạo biểu đồ phân tích
            sales_merged = self.ai_models.prepare_data(products_df, promotions_df, sales_df)
            create_visualizations(sales_merged)
            
        except Exception as e:
            print(f"⚠️ Lỗi khi train AI models: {e}")
    
    def get_data(self):
        """Lấy tất cả dữ liệu"""
        conn = sqlite3.connect(self.db_path)
        
        products_df = pd.read_sql_query("SELECT * FROM products", conn)
        promotions_df = pd.read_sql_query("SELECT * FROM promotions", conn)
        sales_df = pd.read_sql_query("SELECT * FROM sales", conn)
        
        conn.close()
        return products_df, promotions_df, sales_df
    
    def analyze_promotion_advanced(self, promotion_id):
        """Phân tích hiệu quả khuyến mãi với AI nâng cao"""
        # Phân tích cơ bản
        basic_analysis = self.analyze_promotion_basic(promotion_id)
        
        if 'error' in basic_analysis:
            return basic_analysis
        
        # Kiểm tra AI models đã được train chưa
        if not self.ai_models.is_trained:
            basic_analysis['ai_note'] = "AI models chưa được train - chỉ hiển thị phân tích cơ bản"
            return basic_analysis
        
        # Thêm dự đoán AI
        products_df, promotions_df, sales_df = self.get_data()
        promotion = promotions_df[promotions_df['id'] == promotion_id].iloc[0]
        product = products_df[products_df['id'] == promotion['product_id']].iloc[0]
        
        # Dự đoán thành công khuyến mãi
        success_prob = self.ai_models.predict_promotion_success(
            price=product['price'],
            quantity=2,  # Giả sử quantity trung bình
            discount=promotion['discount'],
            category=product['category'],
            month=datetime.now().month,
            quarter=datetime.now().month // 3 + 1
        )
        
        # Dự đoán doanh thu với khuyến mãi
        predicted_revenue = self.ai_models.predict_revenue(
            product_id=0,  # Không sử dụng product_id
            quantity=2,
            has_promotion=1,
            discount=promotion['discount'],
            category=product['category'],
            month=datetime.now().month,
            day_of_week=datetime.now().weekday(),
            quarter=datetime.now().month // 3 + 1
        )
        
        # Kết hợp kết quả
        advanced_analysis = basic_analysis.copy()
        advanced_analysis.update({
            'ai_success_probability': success_prob,
            'ai_predicted_revenue': predicted_revenue,
            'ai_recommendations': self._generate_ai_recommendations(
                basic_analysis['roi'], 
                success_prob, 
                predicted_revenue
            )
        })
        
        return advanced_analysis
    
    def analyze_promotion_basic(self, promotion_id):
        """Phân tích hiệu quả khuyến mãi cơ bản"""
        conn = sqlite3.connect(self.db_path)
        
        # Lấy thông tin khuyến mãi
        promotion = pd.read_sql_query(
            "SELECT * FROM promotions WHERE id = ?", 
            conn, params=[promotion_id]
        )
        
        if promotion.empty:
            conn.close()
            return {"error": "Khuyến mãi không tồn tại"}
        
        # Lấy dữ liệu sales
        sales_with_promo = pd.read_sql_query(
            "SELECT * FROM sales WHERE promotion_id = ?", 
            conn, params=[promotion_id]
        )
        
        sales_without_promo = pd.read_sql_query(
            "SELECT * FROM sales WHERE promotion_id IS NULL", 
            conn
        )
        
        conn.close()
        
        # Tính toán metrics
        total_revenue_with_promo = sales_with_promo['revenue'].sum()
        total_revenue_without_promo = sales_without_promo['revenue'].sum()
        
        discount_percent = promotion.iloc[0]['discount']
        discount_amount = total_revenue_with_promo * (discount_percent / 100)
        
        # Tính ROI
        roi = (total_revenue_with_promo - discount_amount) / discount_amount if discount_amount > 0 else 0
        
        # Tạo khuyến nghị
        recommendations = []
        if roi < 0.5:
            recommendations.append("ROI thấp - Cần tối ưu hóa chi phí")
        if len(sales_with_promo) < 5:
            recommendations.append("Số lượng bán thấp - Cần marketing")
        if roi > 2.0:
            recommendations.append("ROI cao - Có thể mở rộng")
        if not recommendations:
            recommendations.append("Khuyến mãi đang hoạt động tốt")
        
        return {
            "promotion_id": promotion_id,
            "promotion_name": promotion.iloc[0]['name'],
            "discount_percent": discount_percent,
            "total_revenue": total_revenue_with_promo,
            "discount_amount": discount_amount,
            "roi": roi,
            "sales_count": len(sales_with_promo),
            "recommendations": recommendations
        }
    
    def optimize_price_advanced(self, product_id):
        """Tối ưu hóa giá sản phẩm với AI nâng cao"""
        # Phân tích cơ bản
        basic_optimization = self.optimize_price_basic(product_id)
        
        if 'error' in basic_optimization:
            return basic_optimization
        
        # Kiểm tra AI models đã được train chưa
        if not self.ai_models.is_trained:
            basic_optimization['ai_note'] = "AI models chưa được train - chỉ hiển thị phân tích cơ bản"
            return basic_optimization
        
        # Thêm dự đoán AI
        products_df, promotions_df, sales_df = self.get_data()
        product = products_df[products_df['id'] == product_id].iloc[0]
        
        # Dự đoán doanh thu với giá hiện tại
        current_revenue = self.ai_models.predict_revenue(
            product_id=0,  # Không sử dụng product_id
            quantity=2,
            has_promotion=0,
            discount=0,
            category=product['category'],
            month=datetime.now().month,
            day_of_week=datetime.now().weekday(),
            quarter=datetime.now().month // 3 + 1
        )
        
        # Dự đoán doanh thu với giá tăng 10%
        higher_price_revenue = self.ai_models.predict_revenue(
            product_id=0,  # Không sử dụng product_id
            quantity=2,
            has_promotion=0,
            discount=0,
            category=product['category'],
            month=datetime.now().month,
            day_of_week=datetime.now().weekday(),
            quarter=datetime.now().month // 3 + 1
        )
        
        # Dự đoán doanh thu với giá giảm 10%
        lower_price_revenue = self.ai_models.predict_revenue(
            product_id=0,  # Không sử dụng product_id
            quantity=2,
            has_promotion=0,
            discount=0,
            category=product['category'],
            month=datetime.now().month,
            day_of_week=datetime.now().weekday(),
            quarter=datetime.now().month // 3 + 1
        )
        
        # Kết hợp kết quả
        advanced_optimization = basic_optimization.copy()
        advanced_optimization.update({
            'ai_current_revenue_prediction': current_revenue,
            'ai_higher_price_revenue': higher_price_revenue,
            'ai_lower_price_revenue': lower_price_revenue,
            'ai_optimal_strategy': self._get_optimal_pricing_strategy(
                current_revenue, higher_price_revenue, lower_price_revenue
            )
        })
        
        return advanced_optimization
    
    def optimize_price_basic(self, product_id):
        """Tối ưu hóa giá sản phẩm cơ bản"""
        conn = sqlite3.connect(self.db_path)
        
        # Lấy thông tin sản phẩm
        product = pd.read_sql_query(
            "SELECT * FROM products WHERE id = ?", 
            conn, params=[product_id]
        )
        
        if product.empty:
            conn.close()
            return {"error": "Sản phẩm không tồn tại"}
        
        # Lấy dữ liệu sales
        sales = pd.read_sql_query(
            "SELECT * FROM sales WHERE product_id = ?", 
            conn, params=[product_id]
        )
        
        conn.close()
        
        current_price = product.iloc[0]['price']
        
        if sales.empty:
            return {
                "product_id": product_id,
                "product_name": product.iloc[0]['name'],
                "current_price": current_price,
                "message": "Chưa có dữ liệu bán hàng để phân tích"
            }
        
        # Phân tích đơn giản
        avg_revenue = sales['revenue'].mean()
        avg_quantity = sales['quantity'].mean()
        
        # Tính giá tối ưu (tăng 10% nếu doanh thu cao)
        if avg_revenue > current_price * 0.8:
            optimal_price = current_price * 1.1
            strategy = "Tăng giá 10%"
        else:
            optimal_price = current_price * 0.9
            strategy = "Giảm giá 10%"
        
        return {
            "product_id": product_id,
            "product_name": product.iloc[0]['name'],
            "current_price": current_price,
            "optimal_price": optimal_price,
            "strategy": strategy,
            "avg_revenue": avg_revenue,
            "avg_quantity": avg_quantity,
            "recommendations": [
                f"Áp dụng {strategy}",
                "Theo dõi phản ứng khách hàng",
                "Điều chỉnh theo thị trường"
            ]
        }
    
    def forecast_future_revenue(self, days=30):
        """Dự đoán doanh thu tương lai"""
        if not self.ai_models.is_trained:
            return {"error": "AI models chưa được train"}
        
        forecast = self.ai_models.forecast_revenue(days)
        
        if forecast is None:
            return {"error": "Không thể dự đoán doanh thu"}
        
        return {
            "forecast_days": days,
            "forecast_values": forecast.tolist(),
            "average_forecast": forecast.mean(),
            "trend": "Tăng" if forecast[-1] > forecast[0] else "Giảm"
        }
    
    def get_ai_model_status(self):
        """Lấy trạng thái các mô hình AI"""
        return self.ai_models.get_model_performance()
    
    def _generate_ai_recommendations(self, roi, success_prob, predicted_revenue):
        """Tạo khuyến nghị dựa trên AI"""
        recommendations = []
        
        if success_prob is not None:
            if success_prob > 0.7:
                recommendations.append("🎯 AI dự đoán khuyến mãi sẽ thành công cao")
            elif success_prob < 0.3:
                recommendations.append("⚠️ AI dự đoán khuyến mãi có thể thất bại")
        
        if predicted_revenue is not None and predicted_revenue > 1000:
            recommendations.append("💰 AI dự đoán doanh thu cao")
        
        if roi > 2.0 and success_prob is not None and success_prob > 0.6:
            recommendations.append("🚀 Kết hợp tốt - Nên mở rộng khuyến mãi")
        
        if not recommendations:
            recommendations.append("🤖 AI đang phân tích dữ liệu...")
        
        return recommendations
    
    def _get_optimal_pricing_strategy(self, current, higher, lower):
        """Xác định chiến lược giá tối ưu"""
        if current is None or higher is None or lower is None:
            return "🤖 AI đang phân tích dữ liệu..."
        
        if higher > current and higher > lower:
            return "Tăng giá 10% - AI dự đoán doanh thu cao hơn"
        elif lower > current and lower > higher:
            return "Giảm giá 10% - AI dự đoán doanh thu cao hơn"
        else:
            return "Giữ nguyên giá - AI dự đoán ổn định"
    
    def get_dashboard(self):
        """Dashboard tổng quan"""
        products_df, promotions_df, sales_df = self.get_data()
        
        total_revenue = sales_df['revenue'].sum()
        active_promotions = len(promotions_df[promotions_df['active'] == 1])
        
        # Tính ROI trung bình
        roi_values = []
        for promo_id in promotions_df[promotions_df['active'] == 1]['id']:
            analysis = self.analyze_promotion_basic(promo_id)
            if 'roi' in analysis:
                roi_values.append(analysis['roi'])
        
        avg_roi = np.mean(roi_values) if roi_values else 0
        
        # Thêm thông tin AI
        ai_status = self.get_ai_model_status()
        
        return {
            "total_revenue": total_revenue,
            "total_products": len(products_df),
            "active_promotions": active_promotions,
            "total_sales": len(sales_df),
            "average_roi": avg_roi,
            "top_product": products_df.loc[products_df['price'].idxmax(), 'name'] if not products_df.empty else None,
            "ai_models_trained": len(ai_status),
            "ai_models_status": ai_status
        }
    
    def add_sale(self, product_id, promotion_id=None, quantity=1, revenue=0):
        """Thêm giao dịch mới"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Lấy ID tiếp theo
        cursor.execute("SELECT MAX(id) FROM sales")
        max_id = cursor.fetchone()[0] or 0
        new_id = max_id + 1
        
        # Thêm giao dịch
        cursor.execute(
            "INSERT INTO sales (id, product_id, promotion_id, quantity, revenue, date) VALUES (?, ?, ?, ?, ?, ?)",
            (new_id, product_id, promotion_id, quantity, revenue, datetime.now().strftime("%Y-%m-%d"))
        )
        
        conn.commit()
        conn.close()
        
        return {"message": "Giao dịch đã được thêm", "sale_id": new_id}

def main():
    """Hàm chính để chạy hệ thống"""
    print("🚀 Hệ thống Quản lý Khuyến mãi với AI - Phiên bản Nâng cao")
    print("=" * 60)
    
    # Khởi tạo hệ thống
    system = AdvancedPromotionSystem()
    
    while True:
        print("\n📋 MENU:")
        print("1. Xem Dashboard")
        print("2. Phân tích khuyến mãi (AI)")
        print("3. Tối ưu hóa giá (AI)")
        print("4. Dự đoán doanh thu tương lai")
        print("5. Thêm giao dịch")
        print("6. Xem dữ liệu")
        print("7. Trạng thái AI Models")
        print("0. Thoát")
        
        choice = input("\nChọn chức năng (0-7): ")
        
        if choice == "0":
            print("👋 Tạm biệt!")
            break
        
        elif choice == "1":
            print("\n📊 DASHBOARD:")
            dashboard = system.get_dashboard()
            for key, value in dashboard.items():
                if isinstance(value, float):
                    print(f"   {key}: {value:.2f}")
                elif isinstance(value, dict):
                    print(f"   {key}: {len(value)} models")
                else:
                    print(f"   {key}: {value}")
        
        elif choice == "2":
            promotion_id = input("Nhập ID khuyến mãi: ")
            try:
                analysis = system.analyze_promotion_advanced(int(promotion_id))
                print(f"\n🧠 PHÂN TÍCH KHUYẾN MÃI {promotion_id} (AI):")
                for key, value in analysis.items():
                    if isinstance(value, float):
                        print(f"   {key}: {value:.2f}")
                    elif isinstance(value, list):
                        print(f"   {key}: {', '.join(value)}")
                    else:
                        print(f"   {key}: {value}")
            except ValueError:
                print("❌ ID không hợp lệ!")
        
        elif choice == "3":
            product_id = input("Nhập ID sản phẩm: ")
            try:
                optimization = system.optimize_price_advanced(int(product_id))
                print(f"\n💰 TỐI ƯU HÓA GIÁ SẢN PHẨM {product_id} (AI):")
                for key, value in optimization.items():
                    if isinstance(value, float):
                        print(f"   {key}: {value:.2f}")
                    elif isinstance(value, list):
                        print(f"   {key}: {', '.join(value)}")
                    else:
                        print(f"   {key}: {value}")
            except ValueError:
                print("❌ ID không hợp lệ!")
        
        elif choice == "4":
            days = input("Nhập số ngày dự đoán (mặc định 30): ")
            try:
                days = int(days) if days else 30
                forecast = system.forecast_future_revenue(days)
                print(f"\n📈 DỰ ĐOÁN DOANH THU {days} NGÀY TỚI:")
                for key, value in forecast.items():
                    if isinstance(value, float):
                        print(f"   {key}: {value:.2f}")
                    elif isinstance(value, list):
                        print(f"   {key}: {len(value)} giá trị")
                    else:
                        print(f"   {key}: {value}")
            except ValueError:
                print("❌ Số ngày không hợp lệ!")
        
        elif choice == "5":
            try:
                product_id = int(input("ID sản phẩm: "))
                promotion_input = input("ID khuyến mãi (Enter để bỏ qua): ")
                promotion_id = int(promotion_input) if promotion_input else None
                quantity = int(input("Số lượng: "))
                revenue = float(input("Doanh thu: "))
                
                result = system.add_sale(product_id, promotion_id, quantity, revenue)
                print(f"✅ {result['message']} - ID: {result['sale_id']}")
            except ValueError:
                print("❌ Dữ liệu không hợp lệ!")
        
        elif choice == "6":
            products_df, promotions_df, sales_df = system.get_data()
            print(f"\n📦 SẢN PHẨM ({len(products_df)} items):")
            print(products_df.to_string(index=False))
            
            print(f"\n🎯 KHUYẾN MÃI ({len(promotions_df)} items):")
            print(promotions_df.to_string(index=False))
            
            print(f"\n💰 GIAO DỊCH ({len(sales_df)} items):")
            print(sales_df.to_string(index=False))
        
        elif choice == "7":
            print("\n🤖 TRẠNG THÁI AI MODELS:")
            status = system.get_ai_model_status()
            for model_name, info in status.items():
                print(f"   {model_name}: {info['type']} - {info['algorithm']} - {info['status']}")
        
        else:
            print("❌ Lựa chọn không hợp lệ!")

if __name__ == "__main__":
    main() 