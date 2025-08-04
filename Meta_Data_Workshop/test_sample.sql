-- Meta Data Workshop 测试样例 DDL 文件
-- 包含多个表的CREATE TABLE语句，用于演示工具功能

-- 用户表
CREATE TABLE IF NOT EXISTS user_management.users (
    user_id INT NOT NULL AUTO_INCREMENT COMMENT '用户ID',
    username VARCHAR(50) NOT NULL COMMENT '用户名',
    email VARCHAR(100) NOT NULL COMMENT '邮箱',
    password_hash VARCHAR(255) NOT NULL COMMENT '密码哈希',
    first_name VARCHAR(50) COMMENT '名',
    last_name VARCHAR(50) COMMENT '姓',
    phone VARCHAR(20) COMMENT '电话号码',
    status TINYINT DEFAULT 1 COMMENT '状态(1:活跃,0:禁用)',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (user_id),
    UNIQUE KEY uk_username (username),
    UNIQUE KEY uk_email (email)
) COMMENT='用户信息表';

-- 产品表
CREATE TABLE IF NOT EXISTS product_catalog.products (
    product_id BIGINT NOT NULL AUTO_INCREMENT COMMENT '产品ID',
    product_code VARCHAR(32) NOT NULL COMMENT '产品编码',
    product_name VARCHAR(200) NOT NULL COMMENT '产品名称',
    category_id INT COMMENT '分类ID',
    description TEXT COMMENT '产品描述',
    price DECIMAL(10,2) NOT NULL DEFAULT 0.00 COMMENT '价格',
    stock_quantity INT DEFAULT 0 COMMENT '库存数量',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否有效',
    weight DECIMAL(8,2) COMMENT '重量(kg)',
    dimensions VARCHAR(50) COMMENT '尺寸',
    manufacturer VARCHAR(100) COMMENT '制造商',
    created_date DATE DEFAULT CURRENT_DATE COMMENT '创建日期',
    last_modified DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后修改时间',
    PRIMARY KEY (product_id),
    UNIQUE KEY uk_product_code (product_code)
) COMMENT='产品信息表';

-- 订单表
CREATE TABLE IF NOT EXISTS order_management.orders (
    order_id BIGINT NOT NULL AUTO_INCREMENT COMMENT '订单ID',
    order_number VARCHAR(32) NOT NULL COMMENT '订单号',
    customer_id INT NOT NULL COMMENT '客户ID',
    order_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '订单日期',
    total_amount DECIMAL(12,2) NOT NULL DEFAULT 0.00 COMMENT '订单总金额',
    discount_amount DECIMAL(10,2) DEFAULT 0.00 COMMENT '折扣金额',
    tax_amount DECIMAL(10,2) DEFAULT 0.00 COMMENT '税费',
    shipping_address TEXT COMMENT '收货地址',
    billing_address TEXT COMMENT '账单地址',
    payment_method VARCHAR(20) COMMENT '支付方式',
    order_status ENUM('pending', 'confirmed', 'shipped', 'delivered', 'cancelled') DEFAULT 'pending' COMMENT '订单状态',
    tracking_number VARCHAR(50) COMMENT '快递单号',
    notes TEXT COMMENT '备注',
    created_by INT COMMENT '创建人',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (order_id),
    UNIQUE KEY uk_order_number (order_number),
    INDEX idx_customer_id (customer_id),
    INDEX idx_order_date (order_date),
    INDEX idx_order_status (order_status)
) COMMENT='订单主表';

-- 订单明细表
CREATE TABLE IF NOT EXISTS order_management.order_items (
    item_id BIGINT NOT NULL AUTO_INCREMENT COMMENT '明细ID',
    order_id BIGINT NOT NULL COMMENT '订单ID',
    product_id BIGINT NOT NULL COMMENT '产品ID',
    product_name VARCHAR(200) NOT NULL COMMENT '产品名称',
    product_code VARCHAR(32) COMMENT '产品编码',
    unit_price DECIMAL(10,2) NOT NULL COMMENT '单价',
    quantity INT NOT NULL DEFAULT 1 COMMENT '数量',
    discount_rate DECIMAL(5,2) DEFAULT 0.00 COMMENT '折扣率',
    line_total DECIMAL(12,2) NOT NULL COMMENT '行总计',
    PRIMARY KEY (item_id),
    INDEX idx_order_id (order_id),
    INDEX idx_product_id (product_id)
) COMMENT='订单明细表';

-- 库存记录表
CREATE TABLE IF NOT EXISTS inventory.stock_movements (
    movement_id BIGINT NOT NULL AUTO_INCREMENT COMMENT '流水ID',
    product_id BIGINT NOT NULL COMMENT '产品ID',
    movement_type ENUM('in', 'out', 'adjustment') NOT NULL COMMENT '移动类型',
    quantity_change INT NOT NULL COMMENT '数量变化',
    reference_type VARCHAR(20) COMMENT '关联类型',
    reference_id BIGINT COMMENT '关联ID',
    warehouse_code VARCHAR(20) COMMENT '仓库编码',
    location_code VARCHAR(30) COMMENT '库位编码',
    batch_number VARCHAR(50) COMMENT '批次号',
    expiry_date DATE COMMENT '过期日期',
    cost_per_unit DECIMAL(10,4) COMMENT '单位成本',
    reason VARCHAR(100) COMMENT '操作原因',
    operator_id INT COMMENT '操作员ID',
    operation_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '操作时间',
    PRIMARY KEY (movement_id),
    INDEX idx_product_id (product_id),
    INDEX idx_operation_time (operation_time),
    INDEX idx_warehouse_location (warehouse_code, location_code)
) COMMENT='库存流水表';