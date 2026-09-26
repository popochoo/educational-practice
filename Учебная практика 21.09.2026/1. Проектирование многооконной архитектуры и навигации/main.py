import os
import tkinter as tk
from tkinter import messagebox
import psycopg2
from psycopg2.extras import RealDictCursor

# 1. ВСТРОЕННЫЙ ПАРСЕР ФАЙЛА .ENV
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


def load_partners_from_db() -> list:
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


class PartnerEditWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        
        self.title("CRM: Карточка партнера [Редактирование]")
        self.geometry("500x400")
        self.configure(bg="#F2F2F2")

        self.transient(parent)
        self.grab_set()

        header = tk.Frame(self, bg="#FFFFFF", height=50)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)

        lbl_title = tk.Label(header, text="Редактирование партнера", font=("Arial", 12, "bold"), bg="#FFFFFF")
        lbl_title.pack(side="left", padx=15)

        form_frame = tk.Frame(self, bg="#F2F2F2")
        form_frame.pack(fill="both", expand=True, padx=20, pady=20)

        lbl_name = tk.Label(form_frame, text="Наименование партнера:", bg="#F2F2F2")
        lbl_name.pack(anchor="w", pady=(5, 2))
        self.ent_name = tk.Entry(form_frame, width=50)
        self.ent_name.pack(fill="x", pady=2)

        lbl_email = tk.Label(form_frame, text="Email партнера:", bg="#F2F2F2")
        lbl_email.pack(anchor="w", pady=(10, 2))
        self.ent_email = tk.Entry(form_frame, width=50)
        self.ent_email.pack(fill="x", pady=2)

        btn_frame = tk.Frame(self, bg="#F2F2F2")
        btn_frame.pack(fill="x", side="bottom", padx=20, pady=20)

        btn_back = tk.Button(btn_frame, text="Назад к списку", command=self.close_window, width=15)
        btn_back.pack(side="left")

        btn_save = tk.Button(btn_frame, text="Сохранить", bg="#EAEAEA", width=15)
        btn_save.pack(side="right")

    def close_window(self):
        self.destroy()

class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("CRM: Реестр партнеров")
        self.geometry("780x600")
        self.configure(bg="#F2F2F2")

        header_frame = tk.Frame(self, bg="#FFFFFF", height=65)
        header_frame.pack(fill="x", side="top")
        header_frame.pack_propagate(False)

        lbl_logo = tk.Label(header_frame, text="[ ЛОГОТИП ]", font=("Arial", 10, "italic"), bg="#EAEAEA", width=12)
        lbl_logo.pack(side="left", padx=15, pady=12)

        lbl_page_title = tk.Label(header_frame, text="Реестр партнеров и скидок", font=("Arial", 14, "bold"), bg="#FFFFFF")
        lbl_page_title.pack(side="left", padx=10)

        btn_add = tk.Button(header_frame, text="Добавить партнера", font=("Arial", 10), command=self.open_edit_window)
        btn_add.pack(side="right", padx=15, pady=15)

        self.canvas = tk.Canvas(self, bg="#F2F2F2", highlightthickness=0)
        scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg="#F2F2F2")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw", width=750)
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scrollbar.pack(side="right", fill="y")

        self.refresh_data()

    def create_partner_card(self, name, phone, email, discount):
        card = tk.Frame(self.scrollable_frame, bd=1, relief="solid", bg="white")
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

    def refresh_data(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        partners = load_partners_from_db()

        if not partners:
            lbl_empty = tk.Label(self.scrollable_frame, text="Данные не найдены или нет связи с СУБД.", font=("Arial", 11), bg="#F2F2F2")
            lbl_empty.pack(pady=20)
        else:
            for p in partners:
                self.create_partner_card(
                    name=p["partner_name"],
                    phone=p["phone"],
                    email=p["email"],
                    discount=p["discount_percentage"]
                )

    def open_edit_window(self):
        PartnerEditWindow(self)


if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()