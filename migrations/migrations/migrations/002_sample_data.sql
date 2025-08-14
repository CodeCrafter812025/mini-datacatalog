-- درج داده‌های نمونه

-- داده‌های schemas
INSERT INTO catalog_test.schemas (name) VALUES 
('sales_schema'),
('inventory_schema'),
('customer_schema'),
('hr_schema'),
('finance_schema');

-- داده‌های etl_processes
INSERT INTO catalog_test.etl_processes (name, description) VALUES 
('etl1', 'Daily sales data processing'),
('etl2', 'Inventory update process'),
('etl3', 'Customer data synchronization'),
('etl4', 'HR records update'),
('etl5', 'Financial reporting');

-- داده‌های tables_name
INSERT INTO catalog_test.tables_name (name, schema_name, etl_name, schema_id) VALUES 
('orders', 'sales_schema', 'etl1', 1),
('order_items', 'sales_schema', 'etl1', 1),
('products', 'inventory_schema', 'etl2', 2),
('stock_levels', 'inventory_schema', 'etl2', 2),
('customers', 'customer_schema', 'etl3', 3),
('employees', 'hr_schema', 'etl4', 4),
('transactions', 'finance_schema', 'etl5', 5);

-- داده‌های etl_table_relations
INSERT INTO catalog_test.etl_table_relations (etl_id, table_id, usage_type) VALUES
(1, 1, 'both'),
(1, 2, 'both'),
(2, 3, 'both'),
(2, 4, 'both'),
(3, 5, 'both'),
(4, 6, 'both'),
(5, 7, 'both');
