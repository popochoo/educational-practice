-- Добавляем новую отгрузку
INSERT INTO
    shipments (id, partner_id, shipment_date, status)
VALUES
    (777, 999, NOW(), 'Завершен');

-- Добавляем в эту отгрузку 350 000 единиц любого товара (Для демонстрации работы функции calculate_partner_discount)
INSERT INTO
    shipment_items (
        shipment_id,
        product_id,
        quantity,
        price_at_shipment
    )
VALUES
    (777, 1, 350000, 100.00);