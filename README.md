# 🎯 Hệ thống Quản lý Khuyến mãi với AI - SQL Server

Hệ thống quản lý khuyến mãi thông minh với AI models để phân tích hiệu quả khuyến mãi và dự đoán doanh thu. Sử dụng **SQL Server** làm database.

## 📁 Cấu trúc Project

```
training_model/
├── simple_model_sqlserver.py  # File chính sử dụng SQL Server
├── ai_models.py              # Các AI models nâng cao
├── sqlserver_config.py       # Cấu hình SQL Server
├── setup_sqlserver.py        # Script setup database
├── data/
│   └── rich_sample_data.xlsx # Dữ liệu mẫu phong phú (173 giao dịch)
├── requirements.txt          # Dependencies
└── README.md                # Hướng dẫn này
```

## 🚀 Cài đặt & Chạy

### 1. Yêu cầu hệ thống
- **SQL Server** (Express, Developer, hoặc Enterprise)
- **ODBC Driver** cho SQL Server
- **Python 3.8+**

### 2. Cài đặt ODBC Driver
- **Windows**: Tải từ Microsoft
- **macOS**: `brew install microsoft/mssql-release/msodbcsql18`
- **Linux**: Theo hướng dẫn Microsoft

### 3. Tạo môi trường ảo
```bash
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
# hoặc
.venv\Scripts\activate     # Windows
```

### 4. Cài đặt dependencies
```bash
pip install -r requirements.txt
```

### 5. Cấu hình SQL Server
Chỉnh sửa `sqlserver_config.py`:
```python
SQLSERVER_CONFIG = {
    'driver': 'ODBC Driver 17 for SQL Server',  # hoặc 18
    'server': 'localhost',
    'port': 1433,
    'database': 'promotions_db',
    'trusted_connection': 'yes',  # Windows Authentication
    # Hoặc SQL Authentication:
    # 'uid': 'sa',
    # 'pwd': 'your_password',
}
```

### 6. Setup Database
```bash
python setup_sqlserver.py
```

### 7. Chạy hệ thống
```bash
python simple_model_sqlserver.py
```

## 🎯 Tính năng chính

### 📊 Quản lý dữ liệu
- **Products**: Quản lý sản phẩm (15 items)
- **Promotions**: Quản lý khuyến mãi (10 items) 
- **Sales**: Theo dõi giao dịch (173 records)
- **Import/Export Excel**: Đọc/ghi dữ liệu từ Excel
- **SQL Server Database**: Lưu trữ dữ liệu an toàn, scalable

### 🤖 AI Models
- **Revenue Prediction**: Dự đoán doanh thu dựa trên sản phẩm, khuyến mãi
- **Promotion Success**: Phân tích hiệu quả khuyến mãi
- **Time Series**: Dự đoán xu hướng doanh thu theo thời gian
- **Price Optimization**: Tối ưu giá sản phẩm

### 📈 Analytics
- Thống kê doanh thu theo sản phẩm, khuyến mãi
- Phân tích hiệu quả khuyến mãi
- Dự đoán doanh thu tương lai
- Tối ưu giá sản phẩm

## 🧠 Cách hoạt động của AI Models

### 1. **Revenue Prediction Model** 📊
**Mục đích**: Dự đoán doanh thu dựa trên sản phẩm, khuyến mãi, số lượng

**Cách hoạt động**:
- **Input**: product_id, promotion_id, quantity, price, discount
- **Features**: price, discount_amount, quantity, category_encoded, has_promotion
- **Algorithm**: Linear Regression, Random Forest, Gradient Boosting
- **Output**: Dự đoán doanh thu (revenue)
- **Yêu cầu dữ liệu**: Ít nhất 5-10 records

**Ví dụ**:
```
Input: Laptop Gaming, 20% discount, quantity=2
→ Predicted Revenue: $2,400
```

### 2. **Promotion Success Model** 🎯
**Mục đích**: Phân tích hiệu quả khuyến mãi và dự đoán thành công

**Cách hoạt động**:
- **Input**: promotion_id, product_id, discount, category
- **Features**: discount_amount, price, category_encoded, quantity
- **Algorithm**: Logistic Regression, Random Forest Classifier
- **Output**: Xác suất thành công (0-1) và khuyến nghị
- **Yêu cầu dữ liệu**: Ít nhất 10 records có khuyến mãi

**Ví dụ**:
```
Input: Black Friday 30% discount cho Electronics
→ Success Probability: 0.85 (85%)
→ Recommendation: "Khuyến mãi hiệu quả, nên tiếp tục"
```

### 3. **Time Series Model** 📈
**Mục đích**: Dự đoán xu hướng doanh thu theo thời gian

**Cách hoạt động**:
- **Input**: Dữ liệu doanh thu theo ngày
- **Features**: date, revenue, month, day_of_week, quarter
- **Algorithm**: ARIMA, Exponential Smoothing
- **Output**: Dự đoán doanh thu cho các ngày tương lai
- **Yêu cầu dữ liệu**: Ít nhất 10-15 ngày liên tiếp

**Ví dụ**:
```
Input: Doanh thu 30 ngày qua
→ Predicted Revenue (next 7 days): [5000, 5200, 4800, 5500, 5300, 5100, 5400]
→ Trend: Tăng 5% so với tuần trước
```

### 4. **Price Optimization Model** 💰
**Mục đích**: Tối ưu giá sản phẩm để tối đa hóa doanh thu

**Cách hoạt động**:
- **Input**: product_id, current_price, category, historical_sales
- **Features**: price, quantity, revenue, discount_amount
- **Algorithm**: Linear Regression, Elasticity Analysis
- **Output**: Giá tối ưu và dự đoán doanh thu
- **Yêu cầu dữ liệu**: Ít nhất 5-10 records cho sản phẩm

**Ví dụ**:
```
Input: Laptop Gaming hiện tại $1500
→ Optimal Price: $1400 (-6.7%)
→ Predicted Revenue Increase: +15%
→ Recommendation: "Giảm giá để tăng doanh thu"
```

## 📊 Quy trình xử lý dữ liệu

### 1. **Data Preparation** 🔄
```
Raw Data → Clean → Feature Engineering → Train/Test Split
```

**Feature Engineering**:
- `has_promotion`: 0/1 (có khuyến mãi hay không)
- `discount_amount`: Số tiền giảm giá
- `net_revenue`: Doanh thu sau khuyến mãi
- `revenue_per_unit`: Doanh thu trên đơn vị
- `category_encoded`: Mã hóa danh mục sản phẩm
- `month`, `day_of_week`, `quarter`: Thông tin thời gian

### 2. **Model Training** 🎯
```
For each model:
1. Prepare features
2. Split data (80% train, 20% test)
3. Train multiple algorithms
4. Cross-validation
5. Select best model
6. Save model
```

### 3. **Model Evaluation** 📊
- **Revenue Prediction**: R² Score, Mean Absolute Error
- **Promotion Success**: Accuracy, Precision, Recall
- **Time Series**: Mean Absolute Percentage Error
- **Price Optimization**: Revenue improvement prediction

## 📊 Dữ liệu mẫu

Hệ thống sử dụng dữ liệu phong phú với:
- **15 sản phẩm** đa dạng (Electronics, Fashion)
- **10 khuyến mãi** khác nhau (20-50% discount)
- **173 giao dịch** trong 30 ngày
- **59.5%** tỷ lệ khuyến mãi
- **$170,365** tổng doanh thu

## 🎮 Menu chính

1. **Xem dữ liệu** - Hiển thị tất cả dữ liệu
2. **Thêm dữ liệu** - Thêm sản phẩm/khuyến mãi/giao dịch
3. **Phân tích cơ bản** - Thống kê doanh thu
4. **AI Analysis** - Phân tích nâng cao với AI
5. **Export Excel** - Xuất dữ liệu ra Excel
6. **Thoát**

## 🤖 AI Analysis Menu

1. **Revenue Prediction** - Dự đoán doanh thu
2. **Promotion Success Analysis** - Phân tích hiệu quả khuyến mãi
3. **Time Series Forecasting** - Dự đoán xu hướng
4. **Price Optimization** - Tối ưu giá
5. **Back to Main Menu**

## 🔧 Troubleshooting

### Lỗi kết nối SQL Server:
1. Kiểm tra SQL Server đang chạy
2. Kiểm tra connection string trong `sqlserver_config.py`
3. Đảm bảo đã cài ODBC Driver
4. Kiểm tra quyền truy cập database

### Lỗi ODBC Driver:
- Windows: Tải từ Microsoft
- macOS: `brew install microsoft/mssql-release/msodbcsql18`
- Linux: Theo hướng dẫn Microsoft

## 💡 Lưu ý

- SQL Server database được tạo tự động qua `setup_sqlserver.py`
- Dữ liệu được load từ `data/rich_sample_data.xlsx`
- AI models cần ít nhất 10 records để train
- Time series cần ít nhất 10 ngày dữ liệu
- Models được train lại mỗi lần chạy để cập nhật với dữ liệu mới
- Hỗ trợ cả Windows Authentication và SQL Authentication
