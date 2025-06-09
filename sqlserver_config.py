#!/usr/bin/env python3
"""
Cấu hình SQL Server Database
"""

# SQL Server Configuration
SQLSERVER_CONFIG = {
    'driver': 'ODBC Driver 17 for SQL Server',  # hoặc 'ODBC Driver 18 for SQL Server'
    'server': 'localhost',
    'port': 1433,
    'database': 'promotions_db',
    'trusted_connection': 'yes',  # Windows Authentication
    # Hoặc dùng SQL Authentication:
    # 'uid': 'sa',
    # 'pwd': 'your_password',
}

# SQL Commands để tạo database và tables
CREATE_DATABASE_SQL = """
IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = 'promotions_db')
BEGIN
    CREATE DATABASE promotions_db;
END
"""

CREATE_TABLES_SQL = """
USE promotions_db;

-- Tạo bảng Products
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='products' AND xtype='U')
CREATE TABLE products (
    id INT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(255) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    category NVARCHAR(100) NOT NULL,
    created_at DATETIME2 DEFAULT GETDATE()
);

-- Tạo bảng Promotions
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='promotions' AND xtype='U')
CREATE TABLE promotions (
    id INT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(255) NOT NULL,
    discount DECIMAL(5,2) NOT NULL,
    product_id INT,
    active BIT DEFAULT 1,
    created_at DATETIME2 DEFAULT GETDATE(),
    CONSTRAINT FK_Promotions_Products FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE SET NULL
);

-- Tạo bảng Sales
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='sales' AND xtype='U')
CREATE TABLE sales (
    id INT IDENTITY(1,1) PRIMARY KEY,
    product_id INT NOT NULL,
    promotion_id INT NULL,
    quantity INT NOT NULL,
    revenue DECIMAL(10,2) NOT NULL,
    date DATE NOT NULL,
    created_at DATETIME2 DEFAULT GETDATE(),
    CONSTRAINT FK_Sales_Products FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    CONSTRAINT FK_Sales_Promotions FOREIGN KEY (promotion_id) REFERENCES promotions(id) ON DELETE SET NULL
);

-- Tạo indexes để tối ưu performance
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_sales_date')
CREATE INDEX IX_sales_date ON sales(date);

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_sales_product')
CREATE INDEX IX_sales_product ON sales(product_id);

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_sales_promotion')
CREATE INDEX IX_sales_promotion ON sales(promotion_id);

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_promotions_product')
CREATE INDEX IX_promotions_product ON promotions(product_id);
""" 