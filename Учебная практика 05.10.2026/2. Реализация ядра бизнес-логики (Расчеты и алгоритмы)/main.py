import math
import os
import psycopg2

def calculate_partner_discount(total_quantity: int) -> int:
    if total_quantity < 10000:
        return 0
    if total_quantity < 49999:
        return 5
    if total_quantity < 299999:
        return 10
    return 15

# ВАЖНО!!! ПОМЕНЯЙТЕ ПАРАМЕТРЫ ПЕРЕМЕННЫХ ОКРУЖЕНИЯ НА СВОИ 
def get_db_connection():
    db_config = {
        "dbname": os.getenv("DB_NAME"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
        "host": os.getenv("DB_HOST"),
        "port": os.getenv("DB_PORT"),
    }
    return psycopg2.connect(**db_config)


def calculate_material_required(product_type_id: int, material_type_id: int, quantity: int, param_1: float, param_2: float) -> int:
    if quantity <= 0 or param_1 < 0 or param_2 < 0:
        return -1

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT product_type_coefficient FROM product_types WHERE id = %s;", (product_type_id,))
        prod_row = cursor.fetchone()

        cursor.execute("SELECT scrap_percentage FROM material_types WHERE id = %s;", (material_type_id,))
        mat_row = cursor.fetchone()

        cursor.close()
        conn.close()

        if not prod_row or not mat_row:
            return -1

        coef = float(prod_row[0])
        scrap = float(mat_row[0])

        base_expense = quantity * param_1 * param_2 * coef
        total_with_scrap = base_expense * (1 + scrap / 100)
        result = math.ceil(total_with_scrap)

        return result

    except Exception:
        return -1