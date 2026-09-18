import os
import psycopg2
from psycopg2.extras import RealDictCursor

if os.path.exists(".env"):
    with open(".env", "r", encoding="utf-8") as f:
        for line in f:
            clean_line = line.strip()
            if clean_line and not clean_line.startswith("#"):
                key, value = clean_line.split("=", 1)
                os.environ[key.strip()] = value.strip()


def calculate_partner_discount(total_quantity: int) -> int:
    if total_quantity < 10000:
        return 0
    if total_quantity < 50000:
        return 5
    if total_quantity < 300000:
        return 10
    return 15


def get_partner_with_discount(partner_id: int) -> dict:

    # ВАЖНО!!!!! В СОСЕДНЕМ ФАЙЛЕ .env НАХОДЯТЬСЯ ПАРАМЕТРЫ ПОДКЛЮЧЕНИЯ К БАЗЕ ДАННЫХ!!! ЗАМЕНИТЕ ИХ НА СВОИ ДАННЫЕ POSTGRESQL ДЛЯ ПОДКЛЮЧЕНИЯ!!!

    db_config = {
        "dbname": os.getenv("DB_NAME"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
        "host": os.getenv("DB_HOST"),
        "port": os.getenv("DB_PORT"),
    }

    conn = psycopg2.connect(**db_config)
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    query = """
        SELECT 
            p.id AS partner_id, 
            p.name, 
            p.inn,
            p.email,
            COALESCE(SUM(si.quantity), 0) AS total_quantity
        FROM partners p
        LEFT JOIN shipments s 
            ON p.id = s.partner_id
        LEFT JOIN shipment_items si 
            ON s.id = si.shipment_id
        WHERE p.id = %s
        GROUP BY p.id, p.name, p.inn, p.email;
    """

    cursor.execute(query, (partner_id,))
    partner_data = cursor.fetchone()

    if not partner_data:
        cursor.close()
        conn.close()
        return {}

    total_volume = int(partner_data["total_quantity"])
    discount = calculate_partner_discount(total_volume)
    partner_data["discount_percentage"] = discount
    result = dict(partner_data)

    cursor.close()
    conn.close()

    return result


if __name__ == "__main__":
    test_partner_id = 999 # ID партнера
    partner_info = get_partner_with_discount(test_partner_id)
    print(partner_info)
