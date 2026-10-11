DROP TABLE IF EXISTS sales_history CASCADE;

DROP TABLE IF EXISTS products CASCADE;

DROP TABLE IF EXISTS partners CASCADE;

DROP TABLE IF EXISTS staging_partners CASCADE;

DROP TABLE IF EXISTS staging_products CASCADE;

DROP TABLE IF EXISTS staging_sales_history CASCADE;

CREATE TABLE partners (
    id INT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    inn VARCHAR(12) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    phone VARCHAR(20)
);

CREATE TABLE products (
    id INT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    price DECIMAL(12, 2) NOT NULL CHECK (price >= 0)
);

CREATE TABLE sales_history (
    id INT PRIMARY KEY,
    partner_id INT NOT NULL,
    product_id INT NOT NULL,
    sale_date DATE NOT NULL,
    quantity INT NOT NULL CHECK (quantity > 0),
    amount DECIMAL(12, 2) NOT NULL CHECK (amount >= 0),
    CONSTRAINT fk_sales_partner FOREIGN KEY (partner_id) REFERENCES partners(id) ON DELETE RESTRICT,
    CONSTRAINT fk_sales_product FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE RESTRICT
);

CREATE TEMP TABLE staging_partners (
    partner_id INT,
    partner_name VARCHAR(255),
    inn VARCHAR(12),
    email VARCHAR(100),
    phone VARCHAR(20)
);

CREATE TEMP TABLE staging_products (
    product_id INT,
    product_name VARCHAR(255),
    price DECIMAL(12, 2)
);

CREATE TEMP TABLE staging_sales_history (
    sale_id INT,
    partner_id INT,
    product_id INT,
    sale_date VARCHAR(50),
    quantity INT,
    amount DECIMAL(12, 2)
);

INSERT INTO
    staging_partners (partner_id, partner_name, inn, email, phone)
VALUES
    (
        1,
        ' ООО "Вектор" ',
        '7701234567',
        'vector@mail.ru',
        '+7 495 111 22 33'
    ),
    (
        2,
        'ИП ...Петров  A.B.',
        '7802345678',
        'petrov@yandex.ru',
        '+7 812 222 33 44'
    ),
    (
        3,
        'АО "Технолоджис"',
        '5003456789',
        'info@techno.ru',
        '+7 499 333 44 55'
    ),
    (
        4,
        '  ООО "Альфа" ',
        '7704567890',
        'alpha@gmail.com',
        '+7 999 444 55 66'
    ),
    (
        5,
        'ИП Сидоров И.И.',
        '7805678901',
        'sidorov@llc.ru',
        '+7 911 555 66 77'
    );

INSERT INTO
    staging_products (product_id, product_name, price)
VALUES
    (101, ' Ноутбук Pro ', 75000.00),
    (102, ' Смартфон X ', 45000.50),
    (103, 'Монитор 27"', 18200.00);

INSERT INTO
    staging_sales_history (
        sale_id,
        partner_id,
        product_id,
        sale_date,
        quantity,
        amount
    )
VALUES
    (1001, 1, 101, '25.10.2023', 2, 150000.00),
    (1002, 2, 102, '2023/10/26', 1, 45000.50),
    (1003, 999, 101, '2023-10-27', 5, 375000.00),
    (1004, 4, 103, '28-10-2023', 10, 182000.00),
    (1005, 3, 102, '2023.10.29', 3, 135001.50),
    (1006, 5, 103, '2023-10-30', 1, 18200.00);

INSERT INTO
    partners (id, name, inn, email, phone)
SELECT
    partner_id,
    TRIM(partner_name),
    TRIM(inn),
    TRIM(email),
    TRIM(phone)
FROM
    staging_partners;

INSERT INTO
    products (id, name, price)
SELECT
    product_id,
    TRIM(product_name),
    price
FROM
    staging_products;

INSERT INTO
    sales_history (
        id,
        partner_id,
        product_id,
        sale_date,
        quantity,
        amount
    )
SELECT
    s.sale_id,
    s.partner_id,
    s.product_id,
    CASE
        WHEN s.sale_date LIKE '%.%.%'
        AND POSITION('.' IN s.sale_date) = 3 THEN TO_DATE(s.sale_date, 'DD.MM.YYYY')
        WHEN s.sale_date LIKE '%.%.%'
        AND POSITION('.' IN s.sale_date) = 5 THEN TO_DATE(s.sale_date, 'YYYY.MM.DD')
        WHEN s.sale_date LIKE '%-%-%'
        AND POSITION('-' IN s.sale_date) = 3 THEN TO_DATE(s.sale_date, 'DD-MM-YYYY')
        WHEN s.sale_date LIKE '%/%/%' THEN TO_DATE(s.sale_date, 'YYYY/MM/DD')
        ELSE TO_DATE(s.sale_date, 'YYYY-MM-DD')
    END,
    s.quantity,
    s.amount
FROM
    staging_sales_history s
    JOIN partners p ON s.partner_id = p.id;