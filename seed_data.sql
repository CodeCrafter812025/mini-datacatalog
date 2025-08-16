-- درج داده‌های اولیه برای ETLها
INSERT INTO etls (name) VALUES 
('etl1'), ('etl2'), ('etl3'), ('etl4'), ('etl5')
ON CONFLICT (name) DO NOTHING;

-- درج داده‌های اولیه برای جداول
INSERT INTO tables (name, etl_id) VALUES 
('table1', 1), ('table2', 1),
('table3', 2),
('table4', 3), ('table5', 3),
('table6', 4),
('table7', 5)
ON CONFLICT DO NOTHING;
