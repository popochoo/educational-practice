import math

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

        # Если переданные ID типов не существуют в БД
        if not prod_row or not mat_row:
            return -1

        coef = float(prod_row[0])
        scrap = float(mat_row[0])

        # Бизнес-логика расчета по ТЗ
        base_waste = param_1 * param_2 * coef
        total_clean_waste = base_waste * quantity
        total_with_scrap = total_clean_waste * (1 + scrap / 100)

        return math.ceil(total_with_scrap)

    except Exception:
        return -1