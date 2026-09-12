-- ============================================================================
-- ЗАПРОС 1: Список партнеров с количеством сделанных доставок
-- Сортировка по названию, использование LEFT JOIN и COUNT
-- ============================================================================

SELECT 
    p.id AS partner_id,
    p.name AS partner_name,
    p.inn AS partner_inn,
    COUNT(s.id) AS total_shipments_count
FROM partners p
LEFT JOIN shipments s ON p.id = s.partner_id
GROUP BY p.id, p.name, p.inn
ORDER BY p.name ASC;


-- ============================================================================
-- ЗАПРОС 2: Демонстрация транзакции (Добавление/обновление данных)
-- Создание нового партнера и запись его тестовой доставки в одном блоке
-- ============================================================================

BEGIN;

INSERT INTO partners (id, name, inn, email, phone)
VALUES (999, 'ООО Тестовый Партнер', '7799999999', 'test@partner.ru', '+70000000000')
ON CONFLICT (id) DO UPDATE 
SET name = EXCLUDED.name, 
    email = EXCLUDED.email;

INSERT INTO shipments (id, partner_id, shipment_date, status)
VALUES (99999, 999, '2026-09-07 19:00:00', 'В обработке')
ON CONFLICT (id) DO NOTHING;

INSERT INTO shipment_items (shipment_id, product_id, quantity, price_at_shipment)
VALUES (99999, 1, 10, 500.00)
ON CONFLICT DO NOTHING;

COMMIT;


-- ============================================================================
-- ЗАПРОС 3: История реализации для конкретного партнера
-- Детальная история отгрузок за указанный период времени
-- ============================================================================

SELECT 
    s.shipment_date AS "Дата отгрузки",
    s.id AS "Номер накладной",
    p.name AS "Название продукта",
    si.quantity AS "Объем (шт.)",
    si.price_at_shipment AS "Цена за шт.",
    (si.quantity * si.price_at_shipment) AS "Итоговая сумма"
FROM shipments s
JOIN shipment_items si ON s.id = si.shipment_id
JOIN products p ON si.product_id = p.id
WHERE s.partner_id IN (1, 2, 3, 999) -- Проверяем сразу всех партнеров, которые у вас есть
  AND s.shipment_date BETWEEN '2020-01-01' AND '2030-12-31' -- Максимально широкий диапазон дат
ORDER BY s.shipment_date DESC;

