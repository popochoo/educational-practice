CREATE TEMP TABLE staging_partners (
    partner_id INT,
    company_name VARCHAR(255),
    inn VARCHAR(12),
    contact_email VARCHAR(100),
    phone VARCHAR(20),
    rating VARCHAR(10)
);

CREATE TEMP TABLE staging_sales (
    sale_id INT,
    partner_id INT,
    product_name VARCHAR(255),
    sale_date DATE,
    quantity INT,
    total_amount NUMERIC(12,2)
);

-- Пути к файлам у всех разные, нужно четко указать где лежат файлы, в моем случае они лежат в отдельной папке tmp на диске C:
COPY staging_partners FROM 'C:/tmp/import_partners.csv' WITH (FORMAT csv, HEADER true, DELIMITER ',', ENCODING 'UTF8');
COPY staging_sales FROM 'C:/tmp/import_sales.txt' WITH (FORMAT csv, HEADER true, DELIMITER E'\t', ENCODING 'UTF8');


INSERT INTO partners (id, name, inn, email, phone)
SELECT 
    partner_id,
    TRIM(company_name),
    TRIM(inn),
    TRIM(contact_email),
    NULLIF(TRIM(phone), '')
FROM staging_partners
ON CONFLICT (id) DO NOTHING;

INSERT INTO products (sku, name, price)
SELECT 
    'SKU-' || upper(substring(md5(product_name) from 1 for 6)),
    product_name,
    MIN(total_amount / quantity)
FROM staging_sales
GROUP BY product_name
ON CONFLICT DO NOTHING;

INSERT INTO shipments (id, partner_id, shipment_date, status)
SELECT 
    sale_id,
    partner_id,
    sale_date,
    'Выполнено'
FROM staging_sales;

INSERT INTO shipment_items (shipment_id, product_id, quantity, price_at_shipment)
SELECT 
    s.sale_id,
    p.id,
    s.quantity,
    (s.total_amount / s.quantity)
FROM staging_sales s
JOIN products p ON p.name = s.product_name;
