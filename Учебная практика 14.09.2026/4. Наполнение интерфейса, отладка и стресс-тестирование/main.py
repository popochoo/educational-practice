import os
import tkinter as tk
from tkinter import messagebox
import psycopg2
from psycopg2.extras import RealDictCursor

# 1. ВСТРОЕННЫЙ ПАРСЕР ФАЙЛА .ENV (БЕЗ СТОРОННИХ БИБЛИОТЕК)
if os.path.exists(".env"):
    with open(".env", "r", encoding="utf-8") as f:
        for line in f:
            clean_line = line.strip()
            if clean_line and not clean_line.startswith("#"):
                key, value = clean_line.split("=", 1)
                os.environ[key.strip()] = value.strip()


# 2. ЯДРО БИЗНЕС-ЛОГИКИ (РАСЧЕТ СКИДКИ ИЗ ПОДЗАДАНИЯ 1)
def calculate_partner_discount(total_quantity: int) -> int:
    if total_quantity < 10000:
        return 0
    if total_quantity < 50000:
        return 5
    if total_quantity < 300000:
        return 10
    return 15


# 3. АГРЕГАЦИЯ ДАННЫХ ИЗ POSTGRESQL (ИЗ ПОДЗАДАНИЯ 2 И SCHEMA.SQL)
def load_partners_from_db() -> list:
    
    # ВАЖНО!!!!! В СОСЕДНЕМ ФАЙЛЕ .env НАХОДЯТЬСЯ ПАРАМЕТРЫ ПОДКЛЮЧЕНИЯ К БАЗЕ ДАННЫХ!!! ЗАМЕНИТЕ ИХ НА СВОИ ДАННЫЕ POSTGRESQL ДЛЯ ПОДКЛЮЧЕНИЯ!!!

    db_config = {
        "dbname": os.getenv("DB_NAME", "practice_db"),
        "user": os.getenv("DB_USER", "postgres"),
        "password": os.getenv("DB_PASSWORD", ""),
        "host": os.getenv("DB_HOST", "localhost"),
        "port": os.getenv("DB_PORT", "5432"),
    }

    try:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        query = """
            SELECT 
                p.id AS partner_id, 
                p.name AS partner_name, 
                p.phone,
                p.email,
                COALESCE(SUM(si.quantity), 0) AS total_quantity
            FROM partners p
            LEFT JOIN shipments s 
                ON p.id = s.partner_id
            LEFT JOIN shipment_items si 
                ON s.id = si.shipment_id
            GROUP BY p.id, p.name, p.phone, p.email
            ORDER BY p.name ASC;
        """

        cursor.execute(query)
        partners_list = cursor.fetchall()

        processed_partners = []
        for partner in partners_list:
            total_volume = int(partner["total_quantity"])
            discount = calculate_partner_discount(total_volume)

            partner_dict = dict(partner)
            partner_dict["discount_percentage"] = discount
            processed_partners.append(partner_dict)

        cursor.close()
        conn.close()
        return processed_partners

    except Exception as e:
        print(f"Ошибка подключения к БД: {e}")
        return []


# 4. РАЗРАБОТКА ИНТЕРФЕЙСА (UI ИЗ ПОДЗАДАНИЯ 3)
def create_partner_card(parent, name, phone, email, discount):
    card = tk.Frame(parent, bd=1, relief="solid", bg="white")
    card.pack(fill="x", padx=15, pady=6)

    info_frame = tk.Frame(card, bg="white")
    info_frame.pack(side="left", fill="both", expand=True, padx=15, pady=10)

    lbl_title = tk.Label(info_frame, text=name, font=("Arial", 11, "bold"), bg="white", anchor="w")
    lbl_title.pack(fill="x")

    phone_text = f"Телефон: {phone}" if phone else "Телефон: не указан"
    lbl_phone = tk.Label(info_frame, text=phone_text, font=("Arial", 10), bg="white", anchor="w")
    lbl_phone.pack(fill="x")

    email_text = f"Email: {email}" if email else "Email: не указан"
    lbl_email = tk.Label(info_frame, text=email_text, font=("Arial", 10), bg="white", anchor="w")
    lbl_email.pack(fill="x")

    discount_frame = tk.Frame(card, bg="white")
    discount_frame.pack(side="right", fill="y", padx=20, pady=10)

    discount_text = f"{discount}%"
    lbl_discount = tk.Label(discount_frame, text=discount_text, font=("Arial", 14, "bold"), bg="white", anchor="e")
    lbl_discount.pack(expand=True)

def main():
    try:
        root = tk.Tk()
        root.title("CRM: Список партнеров и скидок")
        root.geometry("750x600")
        root.configure(bg="#F2F2F2")
        print("Инициализация Tkinter прошла успешно")

        header_frame = tk.Frame(root, bg="#FFFFFF", height=65)
        header_frame.pack(fill="x", side="top")
        header_frame.pack_propagate(False)

        lbl_page_title = tk.Label(header_frame, text="Список партнеров и скидок", font=("Arial", 14, "bold"), bg="#FFFFFF")
        lbl_page_title.pack(side="left", padx=10)

        canvas = tk.Canvas(root, bg="#F2F2F2", highlightthickness=0)
        scrollbar = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#F2F2F2")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=730)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scrollbar.pack(side="right", fill="y")

        print("Начинаем загрузку данных из БД...")
        partners = load_partners_from_db()
        print(f"Загружено партнеров из БД: {len(partners)}")

        if not partners:
            lbl_empty = tk.Label(scrollable_frame, text="Данные партнеров не найдены или нет связи с СУБД.", font=("Arial", 11), bg="#F2F2F2")
            lbl_empty.pack(pady=20)
        else:
            for p in partners:
                create_partner_card(
                    scrollable_frame,
                    name=p["partner_name"],
                    phone=p["phone"],
                    email=p["email"],
                    discount=p["discount_percentage"]
                )

        print("Запуск главного цикла оконного интерфейса...")
        root.mainloop()

    except Exception as general_error:
        import messagebox
        messagebox.showerror("Критическая ошибка", f"Приложение упало при старте:\n{general_error}")

if __name__ == "__main__":
    print("Скрипт стартовал...")
    main()

