DROP TABLE IF EXISTS shipment_items CASCADE;

DROP TABLE IF EXISTS shipments CASCADE;

DROP TABLE IF EXISTS products CASCADE;

DROP TABLE IF EXISTS partners CASCADE;

CREATE TABLE partners (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    inn VARCHAR(12) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    phone VARCHAR(20),
    address TEXT,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    sku VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    price NUMERIC(12, 2) NOT NULL CHECK (price >= 0)
);

CREATE TABLE shipments (
    id SERIAL PRIMARY KEY,
    partner_id INT NOT NULL,
    shipment_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) NOT NULL,
    CONSTRAINT fk_shipment_partner FOREIGN KEY (partner_id) REFERENCES partners(id) ON DELETE RESTRICT
);

CREATE TABLE shipment_items (
    shipment_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL CHECK (quantity > 0),
    price_at_shipment NUMERIC(12, 2) NOT NULL CHECK (price_at_shipment >= 0),
    PRIMARY KEY (shipment_id, product_id),
    CONSTRAINT fk_item_shipment FOREIGN KEY (shipment_id) REFERENCES shipments(id) ON DELETE CASCADE,
    CONSTRAINT fk_item_product FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE RESTRICT
);

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
    total_amount NUMERIC(12, 2)
);

COPY staging_partners
FROM
    'import_data/import_partners.csv' WITH (
        FORMAT csv,
        HEADER true,
        DELIMITER ',',
        ENCODING 'UTF8'
    );

COPY staging_sales
FROM
    'import_data/import_sales.txt' WITH (
        FORMAT csv,
        HEADER true,
        DELIMITER E '\t',
        ENCODING 'UTF8'
    );

INSERT INTO
    partners (id, name, inn, email, phone)
SELECT
    partner_id,
    TRIM(company_name),
    TRIM(inn),
    TRIM(contact_email),
    NULLIF(TRIM(phone), '')
FROM
    staging_partners ON CONFLICT (id) DO NOTHING;

INSERT INTO
    products (sku, name, price)
SELECT
    'SKU-' || upper(
        substring(
            md5(product_name)
            from
                1 for 6
        )
    ),
    product_name,
    MIN(total_amount / quantity)
FROM
    staging_sales
GROUP BY
    product_name ON CONFLICT DO NOTHING;

INSERT INTO
    shipments (id, partner_id, shipment_date, status)
SELECT
    sale_id,
    partner_id,
    sale_date,
    'Выполнено'
FROM
    staging_sales;

INSERT INTO
    shipment_items (
        shipment_id,
        product_id,
        quantity,
        price_at_shipment
    )
SELECT
    s.sale_id,
    p.id,
    s.quantity,
    (s.total_amount / s.quantity)
FROM
    staging_sales s
    JOIN products p ON p.name = s.product_name;