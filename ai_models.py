#!/usr/bin/env python3
"""
AI Models cho Hệ thống Quản lý Khuyến mãi - SQL Server Version
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier, GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, r2_score, accuracy_score, classification_report
from sklearn.preprocessing import LabelEncoder
import statsmodels.api as sm
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.holtwinters import ExponentialSmoothing
import warnings
warnings.filterwarnings('ignore')

class PromotionAnalyzer:
    def __init__(self):
        self.models = {}
        self.label_encoders = {}
        self.is_trained = False
        
    def prepare_data(self, products_df, promotions_df, sales_df):
        """Chuẩn bị dữ liệu cho AI models"""
        print("📊 Chuẩn bị dữ liệu...")
        
        # Merge dữ liệu
        data = sales_df.merge(products_df, left_on='product_id', right_on='id', how='left')
        data = data.merge(promotions_df, left_on='promotion_id', right_on='id', how='left', suffixes=('_product', '_promotion'))
        
        # Tạo features
        data['has_promotion'] = data['promotion_id'].notna().astype(int)
        data['discount_amount'] = data['price'] * data['discount'] / 100 * data['has_promotion']
        data['net_revenue'] = data['revenue']
        data['revenue_per_unit'] = data['revenue'] / data['quantity']
        
        # Encode categories
        if 'category' in data.columns:
            le = LabelEncoder()
            data['category_encoded'] = le.fit_transform(data['category'].fillna('Unknown'))
            self.label_encoders['category'] = le
        
        # Time features
        data['date'] = pd.to_datetime(data['date'])
        data['month'] = data['date'].dt.month
        data['day_of_week'] = data['date'].dt.dayofweek
        data['quarter'] = data['date'].dt.quarter
        
        print(f"✅ Dữ liệu đã được chuẩn bị: {len(data)} records")
        print(f"📋 Columns: {list(data.columns)}")
        
        return data
    
    def train_models(self, products_df, promotions_df, sales_df):
        """Train tất cả AI models"""
        data = self.prepare_data(products_df, promotions_df, sales_df)
        
        if len(data) < 5:
            print("⚠️ Không đủ dữ liệu để train models")
            return
        
        # 1. Revenue Prediction Model
        self.train_revenue_model(data)
        
        # 2. Promotion Success Model
        self.train_promotion_success_model(data)
        
        # 3. Time Series Model
        self.train_time_series_model(data)
        
        # 4. Price Optimization Model
        self.train_price_optimization_model(data)
        
        self.is_trained = True
        print("🎉 Tất cả AI models đã được train!")
    
    def train_revenue_model(self, data):
        """Train Revenue Prediction Model"""
        print("\n📊 Training Revenue Prediction Model...")
        
        # Features cho revenue prediction
        features = ['price', 'discount_amount', 'quantity', 'category_encoded', 'has_promotion']
        X = data[features].fillna(0)
        y = data['revenue']
        
        if len(X) < 5:
            print("⚠️ Không đủ dữ liệu để train revenue model")
            return
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Train multiple models
        models = {
            'linear_regression': LinearRegression(),
            'random_forest': RandomForestRegressor(n_estimators=100, random_state=42),
            'gradient_boosting': GradientBoostingRegressor(n_estimators=100, random_state=42)
        }
        
        best_score = -float('inf')
        best_model = None
        
        for name, model in models.items():
            # Cross validation
            cv_scores = cross_val_score(model, X_train, y_train, cv=3, scoring='r2')
            cv_score = cv_scores.mean()
            
            # Train và test
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            test_score = r2_score(y_test, y_pred)
            
            print(f"📊 {name}: CV Score = {cv_score:.2f}, Test Score = {test_score:.2f}")
            
            if test_score > best_score:
                best_score = test_score
                best_model = model
        
        self.models['revenue_prediction'] = best_model
        print(f"✅ Revenue model đã train với score: {best_score:.2f}")
    
    def train_promotion_success_model(self, data):
        """Train Promotion Success Model"""
        print("\n🎯 Training Promotion Success Model...")
        
        # Chỉ lấy dữ liệu có khuyến mãi
        promo_data = data[data['has_promotion'] == 1]
        
        if len(promo_data) < 10:
            print("⚠️ Không đủ dữ liệu để train promotion success model")
            return
        
        # Tạo target: success = 1 nếu revenue > median
        median_revenue = promo_data['revenue'].median()
        promo_data['success'] = (promo_data['revenue'] > median_revenue).astype(int)
        
        # Features
        features = ['discount_amount', 'price', 'category_encoded', 'quantity']
        X = promo_data[features].fillna(0)
        y = promo_data['success']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Train models
        models = {
            'logistic_regression': LogisticRegression(random_state=42),
            'random_forest': RandomForestClassifier(n_estimators=100, random_state=42)
        }
        
        best_score = 0
        best_model = None
        
        for name, model in models.items():
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            score = accuracy_score(y_test, y_pred)
            
            print(f"📊 {name}: Accuracy = {score:.2f}")
            
            if score > best_score:
                best_score = score
                best_model = model
        
        self.models['promotion_success'] = best_model
        print(f"✅ Promotion success model đã train với accuracy: {best_score:.2f}")
    
    def train_time_series_model(self, data):
        """Train Time Series Model"""
        print("\n📈 Training Time Series Model...")
        
        # Aggregate data by date
        daily_revenue = data.groupby('date')['revenue'].sum().reset_index()
        daily_revenue = daily_revenue.sort_values('date')
        
        if len(daily_revenue) < 10:
            print("⚠️ Không đủ dữ liệu time series")
            return
        
        # Set date as index
        daily_revenue.set_index('date', inplace=True)
        
        try:
            # Try ARIMA model
            model = ARIMA(daily_revenue['revenue'], order=(1, 1, 1))
            fitted_model = model.fit()
            self.models['time_series'] = fitted_model
            print("✅ Time series model (ARIMA) đã train")
        except:
            try:
                # Try Exponential Smoothing
                model = ExponentialSmoothing(daily_revenue['revenue'])
                fitted_model = model.fit()
                self.models['time_series'] = fitted_model
                print("✅ Time series model (Exponential Smoothing) đã train")
            except:
                print("⚠️ Không thể train time series model")
    
    def train_price_optimization_model(self, data):
        """Train Price Optimization Model"""
        print("\n💰 Training Price Optimization Model...")
        
        # Features cho price optimization
        features = ['price', 'quantity', 'revenue', 'discount_amount']
        X = data[features].fillna(0)
        y = data['revenue']
        
        if len(X) < 5:
            print("⚠️ Không đủ dữ liệu để train price optimization model")
            return
        
        # Train linear regression for price elasticity
        model = LinearRegression()
        model.fit(X, y)
        
        self.models['price_optimization'] = model
        print("✅ Price optimization model đã train")
    
    def revenue_prediction(self):
        """Dự đoán doanh thu"""
        if 'revenue_prediction' not in self.models:
            print("❌ Revenue prediction model chưa được train")
            return
        
        print("\n📊 REVENUE PREDICTION")
        print("Nhập thông tin để dự đoán doanh thu:")
        
        try:
            price = float(input("Giá sản phẩm: "))
            discount = float(input("Giảm giá (%): "))
            quantity = int(input("Số lượng: "))
            category = input("Danh mục (Electronics/Fashion): ")
            
            # Encode category
            if 'category' in self.label_encoders:
                category_encoded = self.label_encoders['category'].transform([category])[0]
            else:
                category_encoded = 0
            
            # Prepare features
            discount_amount = price * discount / 100
            has_promotion = 1 if discount > 0 else 0
            
            features = np.array([[price, discount_amount, quantity, category_encoded, has_promotion]])
            
            # Predict
            prediction = self.models['revenue_prediction'].predict(features)[0]
            
            print(f"\n🎯 DỰ ĐOÁN DOANH THU: ${prediction:,.2f}")
            
        except Exception as e:
            print(f"❌ Lỗi: {e}")
    
    def promotion_success_analysis(self):
        """Phân tích hiệu quả khuyến mãi"""
        if 'promotion_success' not in self.models:
            print("❌ Promotion success model chưa được train")
            return
        
        print("\n🎯 PROMOTION SUCCESS ANALYSIS")
        print("Nhập thông tin khuyến mãi:")
        
        try:
            discount = float(input("Giảm giá (%): "))
            price = float(input("Giá sản phẩm: "))
            category = input("Danh mục (Electronics/Fashion): ")
            quantity = int(input("Số lượng dự kiến: "))
            
            # Encode category
            if 'category' in self.label_encoders:
                category_encoded = self.label_encoders['category'].transform([category])[0]
            else:
                category_encoded = 0
            
            # Prepare features
            discount_amount = price * discount / 100
            features = np.array([[discount_amount, price, category_encoded, quantity]])
            
            # Predict success probability
            if hasattr(self.models['promotion_success'], 'predict_proba'):
                proba = self.models['promotion_success'].predict_proba(features)[0]
                success_prob = proba[1]  # Probability of success
            else:
                success_prob = 0.5  # Default if no predict_proba
            
            print(f"\n🎯 XÁC SUẤT THÀNH CÔNG: {success_prob:.1%}")
            
            if success_prob > 0.7:
                print("✅ Khuyến mãi có khả năng thành công cao!")
            elif success_prob > 0.5:
                print("⚠️ Khuyến mãi có khả năng thành công trung bình")
            else:
                print("❌ Khuyến mãi có khả năng thành công thấp")
                
        except Exception as e:
            print(f"❌ Lỗi: {e}")
    
    def time_series_forecasting(self):
        """Dự đoán xu hướng thời gian"""
        if 'time_series' not in self.models:
            print("❌ Time series model chưa được train")
            return
        
        print("\n📈 TIME SERIES FORECASTING")
        
        try:
            days = int(input("Số ngày muốn dự đoán (1-30): "))
            
            model = self.models['time_series']
            
            if hasattr(model, 'forecast'):
                # ARIMA model
                forecast = model.forecast(steps=days)
            elif hasattr(model, 'predict'):
                # Exponential Smoothing
                forecast = model.predict(start=len(model.fittedvalues), end=len(model.fittedvalues) + days - 1)
            else:
                print("❌ Model không hỗ trợ forecasting")
                return
            
            print(f"\n📊 DỰ ĐOÁN DOANH THU {days} NGÀY TỚI:")
            for i, value in enumerate(forecast, 1):
                print(f"   Ngày {i}: ${value:,.2f}")
            
            avg_forecast = np.mean(forecast)
            print(f"\n📈 Doanh thu trung bình dự kiến: ${avg_forecast:,.2f}")
            
        except Exception as e:
            print(f"❌ Lỗi: {e}")
    
    def price_optimization(self):
        """Tối ưu giá sản phẩm"""
        if 'price_optimization' not in self.models:
            print("❌ Price optimization model chưa được train")
            return
        
        print("\n💰 PRICE OPTIMIZATION")
        print("Nhập thông tin sản phẩm:")
        
        try:
            current_price = float(input("Giá hiện tại: "))
            current_quantity = int(input("Số lượng bán trung bình: "))
            current_revenue = float(input("Doanh thu trung bình: "))
            
            # Test different prices
            test_prices = [current_price * 0.9, current_price * 0.95, current_price, 
                          current_price * 1.05, current_price * 1.1]
            
            best_price = current_price
            best_revenue = current_revenue
            
            print(f"\n📊 PHÂN TÍCH GIÁ:")
            print(f"   Giá hiện tại: ${current_price:,.2f} → Doanh thu: ${current_revenue:,.2f}")
            
            for test_price in test_prices:
                if test_price != current_price:
                    # Estimate quantity change based on price elasticity
                    price_change = (test_price - current_price) / current_price
                    quantity_change = -0.5 * price_change  # Assume elasticity of -0.5
                    new_quantity = current_quantity * (1 + quantity_change)
                    
                    # Predict revenue
                    features = np.array([[test_price, new_quantity, current_revenue, 0]])
                    predicted_revenue = self.models['price_optimization'].predict(features)[0]
                    
                    print(f"   Giá ${test_price:,.2f} → Doanh thu dự kiến: ${predicted_revenue:,.2f}")
                    
                    if predicted_revenue > best_revenue:
                        best_revenue = predicted_revenue
                        best_price = test_price
            
            print(f"\n🎯 KHUYẾN NGHỊ:")
            if best_price < current_price:
                print(f"   Giảm giá xuống ${best_price:,.2f} (-{((current_price-best_price)/current_price)*100:.1f}%)")
                print(f"   Doanh thu dự kiến tăng: ${best_revenue - current_revenue:,.2f}")
            elif best_price > current_price:
                print(f"   Tăng giá lên ${best_price:,.2f} (+{((best_price-current_price)/current_price)*100:.1f}%)")
                print(f"   Doanh thu dự kiến tăng: ${best_revenue - current_revenue:,.2f}")
            else:
                print("   Giữ nguyên giá hiện tại")
                
        except Exception as e:
            print(f"❌ Lỗi: {e}") 