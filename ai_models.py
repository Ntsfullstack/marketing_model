
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import mean_squared_error, accuracy_score, classification_report
import matplotlib.pyplot as plt
import seaborn as sns
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.seasonal import seasonal_decompose
import warnings
warnings.filterwarnings('ignore')

class AdvancedAIModels:
    def __init__(self):
        """Khởi tạo các mô hình AI"""
        self.models = {}
        self.scalers = {}
        self.label_encoders = {}
        self.is_trained = False
        
    def prepare_data(self, products_df, promotions_df, sales_df):
        """Chuẩn bị dữ liệu cho training"""
        # Merge dữ liệu - sửa tên cột
        sales_merged = sales_df.merge(products_df, left_on='product_id', right_on='id', how='left')
        sales_merged = sales_merged.merge(promotions_df, left_on='promotion_id', right_on='id', how='left')
        
        # Tạo features
        sales_merged['has_promotion'] = sales_merged['promotion_id'].notna().astype(int)
        sales_merged['discount_amount'] = sales_merged['revenue'] * (sales_merged['discount'] / 100)
        sales_merged['net_revenue'] = sales_merged['revenue'] - sales_merged['discount_amount'].fillna(0)
        sales_merged['revenue_per_unit'] = sales_merged['revenue'] / sales_merged['quantity']
        
        # Encode categorical variables
        le_category = LabelEncoder()
        sales_merged['category_encoded'] = le_category.fit_transform(sales_merged['category'])
        
        # Time features
        sales_merged['date'] = pd.to_datetime(sales_merged['date'])
        sales_merged['month'] = sales_merged['date'].dt.month
        sales_merged['day_of_week'] = sales_merged['date'].dt.dayofweek
        sales_merged['quarter'] = sales_merged['date'].dt.quarter
        
        # Fill NaN values
        sales_merged['discount'] = sales_merged['discount'].fillna(0)
        
        self.label_encoders['category'] = le_category
        return sales_merged
    
    def train_revenue_prediction_model(self, sales_merged):
        """Train mô hình dự đoán doanh thu"""
        # Features cho revenue prediction (không bao gồm product_id)
        features = ['price', 'quantity', 'has_promotion', 'discount', 
                   'category_encoded', 'month', 'day_of_week', 'quarter']
        
        X = sales_merged[features].fillna(0)
        y = sales_merged['revenue']
        
        # Kiểm tra dữ liệu
        if len(X) < 5:
            print("⚠️ Không đủ dữ liệu để train revenue prediction model")
            return None, None
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train multiple models
        models = {
            'linear_regression': LinearRegression(),
            'random_forest': RandomForestRegressor(n_estimators=100, random_state=42)
        }
        
        best_model = None
        best_score = -np.inf
        
        for name, model in models.items():
            try:
                # Cross validation
                scores = cross_val_score(model, X_train_scaled, y_train, cv=min(5, len(X_train)), scoring='neg_mean_squared_error')
                avg_score = -scores.mean()
                
                # Train on full training set
                model.fit(X_train_scaled, y_train)
                
                # Test score
                y_pred = model.predict(X_test_scaled)
                test_score = -mean_squared_error(y_test, y_pred)
                
                print(f"📊 {name}: CV Score = {avg_score:.2f}, Test Score = {test_score:.2f}")
                
                if test_score > best_score:
                    best_score = test_score
                    best_model = model
            except Exception as e:
                print(f"⚠️ Lỗi train {name}: {e}")
        
        if best_model is not None:
            self.models['revenue_prediction'] = best_model
            self.scalers['revenue_prediction'] = scaler
            print("✅ Revenue prediction model đã được train thành công!")
        else:
            print("❌ Không thể train revenue prediction model")
        
        return best_model, scaler
    
    def train_promotion_success_model(self, sales_merged):
        """Train mô hình dự đoán thành công khuyến mãi"""
        # Tạo target: khuyến mãi thành công nếu ROI > 1
        promotion_sales = sales_merged[sales_merged['has_promotion'] == 1].copy()
        
        if len(promotion_sales) < 10:
            print("⚠️ Không đủ dữ liệu để train promotion success model")
            return None, None
        
        # Tính ROI cho mỗi khuyến mãi
        promotion_sales['roi'] = (promotion_sales['net_revenue'] - promotion_sales['discount_amount']) / promotion_sales['discount_amount']
        promotion_sales['is_successful'] = (promotion_sales['roi'] > 1).astype(int)
        
        # Features
        features = ['price', 'quantity', 'discount', 'category_encoded', 'month', 'quarter']
        X = promotion_sales[features].fillna(0)
        y = promotion_sales['is_successful']
        
        if len(y.unique()) < 2:
            print("⚠️ Không đủ dữ liệu đa dạng cho classification")
            return None, None
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train models
        models = {
            'logistic_regression': LogisticRegression(random_state=42),
            'random_forest_classifier': RandomForestClassifier(n_estimators=100, random_state=42)
        }
        
        best_model = None
        best_score = 0
        
        for name, model in models.items():
            # Cross validation
            scores = cross_val_score(model, X_train_scaled, y_train, cv=5, scoring='accuracy')
            avg_score = scores.mean()
            
            # Train on full training set
            model.fit(X_train_scaled, y_train)
            
            # Test score
            y_pred = model.predict(X_test_scaled)
            test_score = accuracy_score(y_test, y_pred)
            
            print(f"🎯 {name}: CV Score = {avg_score:.3f}, Test Score = {test_score:.3f}")
            
            if test_score > best_score:
                best_score = test_score
                best_model = model
        
        self.models['promotion_success'] = best_model
        self.scalers['promotion_success'] = scaler
        
        return best_model, scaler
    
    def train_time_series_model(self, sales_df):
        """Train mô hình time series cho dự đoán xu hướng"""
        try:
            # Aggregate sales by date
            daily_sales = sales_df.groupby('date')['revenue'].sum().reset_index()
            daily_sales['date'] = pd.to_datetime(daily_sales['date'])
            daily_sales = daily_sales.set_index('date').sort_index()
            
            if len(daily_sales) < 10:
                print("⚠️ Không đủ dữ liệu time series")
                return None
            
            # Fill missing dates
            date_range = pd.date_range(start=daily_sales.index.min(), 
                                     end=daily_sales.index.max(), freq='D')
            daily_sales = daily_sales.reindex(date_range, fill_value=0)
            
            # Simple moving average for trend
            daily_sales['ma_7'] = daily_sales['revenue'].rolling(window=7).mean()
            
            # ARIMA model
            model = ARIMA(daily_sales['revenue'], order=(1, 1, 1))
            model_fit = model.fit()
            
            self.models['time_series'] = model_fit
            
            return model_fit
            
        except Exception as e:
            print(f"⚠️ Lỗi time series model: {e}")
            return None
    
    def train_all_models(self, products_df, promotions_df, sales_df):
        """Train tất cả các mô hình"""
        print("🚀 Training AI Models...")
        print("=" * 50)
        
        try:
            # Prepare data
            print("📊 Chuẩn bị dữ liệu...")
            sales_merged = self.prepare_data(products_df, promotions_df, sales_df)
            print(f"✅ Dữ liệu đã được chuẩn bị: {len(sales_merged)} records")
            print(f"📋 Columns: {list(sales_merged.columns)}")
            
            # Train revenue prediction model
            print("\n📊 Training Revenue Prediction Model...")
            self.train_revenue_prediction_model(sales_merged)
            
            # Train promotion success model
            print("\n🎯 Training Promotion Success Model...")
            self.train_promotion_success_model(sales_merged)
            
            # Train time series model
            print("\n📈 Training Time Series Model...")
            self.train_time_series_model(sales_df)
            
            self.is_trained = True
            print("\n✅ Tất cả models đã được train!")
            
        except Exception as e:
            print(f"⚠️ Lỗi khi train AI models: {e}")
            import traceback
            traceback.print_exc()
    
    def predict_revenue(self, product_id, quantity, has_promotion, discount, category, month, day_of_week, quarter):
        """Dự đoán doanh thu"""
        if not self.is_trained or 'revenue_prediction' not in self.models:
            return None
        
        try:
            # Prepare features (không bao gồm product_id)
            category_encoded = self.label_encoders['category'].transform([category])[0]
            features = np.array([[0, quantity, has_promotion, discount, 
                                 category_encoded, month, day_of_week, quarter]])  # Thay product_id bằng 0
            
            # Scale features
            features_scaled = self.scalers['revenue_prediction'].transform(features)
            
            # Predict
            prediction = self.models['revenue_prediction'].predict(features_scaled)[0]
            
            return max(0, prediction)  # Revenue không thể âm
        except Exception as e:
            print(f"⚠️ Lỗi dự đoán doanh thu: {e}")
            return None
    
    def predict_promotion_success(self, price, quantity, discount, category, month, quarter):
        """Dự đoán khuyến mãi có thành công không"""
        if not self.is_trained or 'promotion_success' not in self.models:
            return None
        
        # Prepare features
        category_encoded = self.label_encoders['category'].transform([category])[0]
        features = np.array([[price, quantity, discount, category_encoded, month, quarter]])
        
        # Scale features
        features_scaled = self.scalers['promotion_success'].transform(features)
        
        # Predict
        success_prob = self.models['promotion_success'].predict_proba(features_scaled)[0][1]
        
        return success_prob
    
    def forecast_revenue(self, days=30):
        """Dự đoán doanh thu trong tương lai"""
        if not self.is_trained or 'time_series' not in self.models:
            return None
        
        try:
            forecast = self.models['time_series'].forecast(steps=days)
            return forecast
        except:
            return None
    
    def get_model_performance(self):
        """Lấy thông tin hiệu suất của các models"""
        performance = {}
        
        if 'revenue_prediction' in self.models:
            performance['revenue_prediction'] = {
                'type': 'Regression',
                'algorithm': type(self.models['revenue_prediction']).__name__,
                'status': 'Trained'
            }
        
        if 'promotion_success' in self.models:
            performance['promotion_success'] = {
                'type': 'Classification',
                'algorithm': type(self.models['promotion_success']).__name__,
                'status': 'Trained'
            }
        
        if 'time_series' in self.models:
            performance['time_series'] = {
                'type': 'Time Series',
                'algorithm': 'ARIMA',
                'status': 'Trained'
            }
        
        return performance

def create_visualizations(sales_merged):
    """Tạo biểu đồ phân tích"""
    plt.style.use('seaborn-v0_8')
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    
    # 1. Revenue by category
    category_revenue = sales_merged.groupby('category')['revenue'].sum()
    axes[0,0].pie(category_revenue.values, labels=category_revenue.index, autopct='%1.1f%%')
    axes[0,0].set_title('Doanh thu theo danh mục')
    
    # 2. Revenue trend over time
    daily_revenue = sales_merged.groupby('date')['revenue'].sum()
    axes[0,1].plot(daily_revenue.index, daily_revenue.values, marker='o')
    axes[0,1].set_title('Xu hướng doanh thu theo thời gian')
    axes[0,1].tick_params(axis='x', rotation=45)
    
    # 3. Promotion effectiveness
    promo_revenue = sales_merged.groupby('has_promotion')['revenue'].mean()
    axes[1,0].bar(['Không KM', 'Có KM'], promo_revenue.values)
    axes[1,0].set_title('Hiệu quả khuyến mãi')
    axes[1,0].set_ylabel('Doanh thu trung bình')
    
    # 4. Price vs Revenue scatter
    axes[1,1].scatter(sales_merged['price'], sales_merged['revenue'], alpha=0.6)
    axes[1,1].set_xlabel('Giá sản phẩm')
    axes[1,1].set_ylabel('Doanh thu')
    axes[1,1].set_title('Mối quan hệ Giá - Doanh thu')
    
    plt.tight_layout()
    plt.savefig('data/analysis_charts.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("📊 Đã tạo biểu đồ phân tích: data/analysis_charts.png") 