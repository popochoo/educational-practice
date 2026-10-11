import os
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
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

# ВАЖНО!!! ПОМЕНЯЙТЕ ПАРАМЕТРЫ ПЕРЕМЕННЫХ ОКРУЖЕНИЯ НА СВОИ 
def get_db_connection():
    db_config = {
        "dbname": os.getenv("DB_NAME", "practice_db"),
        "user": os.getenv("DB_USER", "postgres"),
        "password": os.getenv("DB_PASSWORD", ""),
        "host": os.getenv("DB_HOST", "localhost"),
        "port": os.getenv("DB_PORT", "5432"),
    }
    return psycopg2.connect(**db_config)


def load_partners_from_db() -> list:
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        query = """
            SELECT 
                p.id AS partner_id, 
                p.name AS partner_name, 
                p.phone,
                p.email,
                p.inn,
                COALESCE(SUM(s.quantity), 0) AS total_quantity
            FROM partners p
            LEFT JOIN sales_history s 
                ON p.id = s.partner_id
            GROUP BY p.id, p.name, p.phone, p.email, p.inn
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
        print(f"Ошибка загрузки данных из БД: {e}")
        return []


class PartnerHistoryWindow(tk.Toplevel):
    def __init__(self, parent, partner_id, partner_name):
        super().__init__(parent)
        
        self.partner_id = partner_id
        self.title(f"CRM: История реализации продукции — [{partner_name}]")
        self.geometry("700x450")
        self.configure(bg="#F2F2F2")

        self.transient(parent)
        self.grab_set()

        try:
            self.iconbitmap("resources/icon.ico")
        except Exception:
            pass

        header = tk.Frame(self, bg="#FFFFFF", height=55)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)

        lbl_logo = tk.Label(header, text="[ ЛОГОТИП ]", font=("Arial", 10, "italic"), bg="#EAEAEA", width=12)
        lbl_logo.pack(side="left", padx=15, pady=10)

        lbl_title = tk.Label(header, text="История отгрузок продукции", font=("Arial", 12, "bold"), bg="#FFFFFF")
        lbl_title.pack(side="left", padx=5)

        table_frame = tk.Frame(self, bg="#F2F2F2")
        table_frame.pack(fill="both", expand=True, padx=20, pady=15)

        style = ttk.Style()
        style.theme_use("clam")
        
        self.tree = ttk.Treeview(table_frame, columns=("product", "date", "quantity"), show="headings")
        
        self.tree.heading("product", text="Наименование продукции")
        self.tree.heading("date", text="Дата продажи")
        self.tree.heading("quantity", text="Количество (шт.)")
        
        self.tree.column("product", width=350, anchor="w")
        self.tree.column("date", width=150, anchor="center")
        self.tree.column("quantity", width=130, anchor="center")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        btn_close = tk.Button(self, text="Назад", width=15, command=self.destroy)
        btn_close.pack(side="bottom", anchor="e", padx=20, pady=15)

        self.load_history_data()

    def load_history_data(self):
        try:
            conn = get_db_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            query = """
                SELECT 
                    pr.name AS product_name,
                    TO_CHAR(s.sale_date, 'YYYY-MM-DD') AS formatted_date,
                    s.quantity
                FROM sales_history s
                JOIN products pr 
                    ON s.product_id = pr.id
                WHERE s.partner_id = %s
                ORDER BY s.sale_date DESC;
            """
            
            cursor.execute(query, (self.partner_id,))
            records = cursor.fetchall()

            cursor.close()
            conn.close()

            for r in records:
                self.tree.insert("", tk.END, values=(r["product_name"], r["formatted_date"], r["quantity"]))

        except Exception as e:
            messagebox.showerror("Ошибка СУБД", f"Не удалось получить историю: {e}")


class PartnerEditWindow(tk.Toplevel):
    def __init__(self, parent, partner_id=None):
        super().__init__(parent)
        
        self.parent = parent
        self.partner_id = partner_id
        
        if self.partner_id:
            self.title("CRM: Карточка партнера [Редактирование]")
        else:
            self.title("CRM: Карточка партнера [Добавление]")
            
        self.geometry("550x650")
        self.configure(bg="#F2F2F2")

        self.transient(parent)
        self.grab_set()

        try:
            self.iconbitmap("resources/icon.ico")
        except Exception:
            pass

        header = tk.Frame(self, bg="#FFFFFF", height=50)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)

        lbl_title_text = "Редактирование партнера" if partner_id else "Добавление нового партнера"
        lbl_title = tk.Label(header, text=lbl_title_text, font=("Arial", 12, "bold"), bg="#FFFFFF")
        lbl_title.pack(side="left", padx=15)

        form_frame = tk.Frame(self, bg="#F2F2F2")
        form_frame.pack(fill="both", expand=True, padx=20, pady=15)

        lbl_type = tk.Label(form_frame, text="Тип партнера:", bg="#F2F2F2")
        lbl_type.pack(anchor="w", pady=(5, 2))
        self.cb_type = ttk.Combobox(form_frame, values=["ЗАО", "ООО", "ИП", "ПАО"], state="readonly")
        self.cb_type.pack(fill="x", pady=2)
        self.cb_type.current(1)

        lbl_name = tk.Label(form_frame, text="Наименование организации:", bg="#F2F2F2")
        lbl_name.pack(anchor="w", pady=(10, 2))
        self.ent_name = tk.Entry(form_frame, width=50)
        self.ent_name.pack(fill="x", pady=2)

        lbl_inn = tk.Label(form_frame, text="ИНН организации:", bg="#F2F2F2")
        lbl_inn.pack(anchor="w", pady=(10, 2))
        self.ent_inn = tk.Entry(form_frame, width=50)
        self.ent_inn.pack(fill="x", pady=2)

        lbl_rating = tk.Label(form_frame, text="Рейтинг партнера:", bg="#F2F2F2")
        lbl_rating.pack(anchor="w", pady=(10, 2))
        self.ent_rating = tk.Entry(form_frame, width=50)
        self.ent_rating.pack(fill="x", pady=2)
        self.ent_rating.insert(0, "0")

        lbl_address = tk.Label(form_frame, text="Юридический адрес:", bg="#F2F2F2")
        lbl_address.pack(anchor="w", pady=(10, 2))
        self.ent_address = tk.Entry(form_frame, width=50)
        self.ent_address.pack(fill="x", pady=2)

        lbl_phone = tk.Label(form_frame, text="Телефон компании:", bg="#F2F2F2")
        lbl_phone.pack(anchor="w", pady=(10, 2))
        self.ent_phone = tk.Entry(form_frame, width=50)
        self.ent_phone.pack(fill="x", pady=2)

        lbl_email = tk.Label(form_frame, text="Email компании:", bg="#F2F2F2")
        lbl_email.pack(anchor="w", pady=(10, 2))
        self.ent_email = tk.Entry(form_frame, width=50)
        self.ent_email.pack(fill="x", pady=2)

        self.placeholder_phone = "+7 (999) 000-00-00"
        self.placeholder_email = "example@domain.com"
        self.setup_placeholder(self.ent_phone, self.placeholder_phone)
        self.setup_placeholder(self.ent_email, self.placeholder_email)

        if self.partner_id:
            self.load_partner_data_to_form()

        btn_frame = tk.Frame(self, bg="#F2F2F2")
        btn_frame.pack(fill="x", side="bottom", padx=20, pady=20)

        btn_back = tk.Button(btn_frame, text="Назад", command=self.destroy, width=15)
        btn_back.pack(side="left")

        btn_save = tk.Button(btn_frame, text="Сохранить", bg="#EAEAEA", width=15, command=self.save_partner)
        btn_save.pack(side="right")

    def setup_placeholder(self, entry, placeholder_text):
        entry.insert(0, placeholder_text)
        entry.config(fg="gray")
        entry.bind("<FocusIn>", lambda event: self.clear_placeholder(entry, placeholder_text))
        entry.bind("<FocusOut>", lambda event: self.restore_placeholder(entry, placeholder_text))

    def clear_placeholder(self, entry, placeholder_text):
        if entry.get() == placeholder_text:
            entry.delete(0, tk.END)
            entry.config(fg="black")

    def restore_placeholder(self, entry, placeholder_text):
        if not entry.get():
            entry.insert(0, placeholder_text)
            entry.config(fg="gray")

    def load_partner_data_to_form(self):
        try:
            conn = get_db_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("SELECT name, inn, email, phone FROM partners WHERE id = %s;", (self.partner_id,))
            partner = cursor.fetchone()
            cursor.close()
            conn.close()

            if partner:
                full_name = partner["name"]
                detected_type = "ООО"
                clean_name = full_name
                for p_type in ["ЗАО", "ООО", "ИП", "ПАО"]:
                    if full_name.startswith(p_type):
                        detected_type = p_type
                        clean_name = full_name.replace(p_type, "").strip()
                        break
                self.cb_type.set(detected_type)
                self.ent_name.insert(0, clean_name)
                self.ent_inn.insert(0, partner["inn"] if partner["inn"] else "")
                if partner["phone"]:
                    self.ent_phone.delete(0, tk.END)
                    self.ent_phone.insert(0, partner["phone"])
                    self.ent_phone.config(fg="black")
                if partner["email"]:
                    self.ent_email.delete(0, tk.END)
                    self.ent_email.insert(0, partner["email"])
                    self.ent_email.config(fg="black")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить данные: {e}")

    def save_partner(self):
        p_type = self.cb_type.get()
        p_name = self.ent_name.get().strip()
        p_inn = self.ent_inn.get().strip()
        p_rating_raw = self.ent_rating.get().strip()
        p_phone = self.ent_phone.get().strip()
        if p_phone == self.placeholder_phone:
            p_phone = ""
        p_email = self.ent_email.get().strip()
        if p_email == self.placeholder_email:
            p_email = ""

        if not p_name or not p_inn:
            messagebox.showwarning("Внимание", "Поля 'Наименование' и 'ИНН' обязательны!")
            return

        try:
            p_rating = int(p_rating_raw)
            if p_rating < 0:
                raise ValueError()
        except ValueError:
            messagebox.showerror("Ошибка", "Рейтинг должен быть целым неотрицательным числом!")
            return

        full_company_name = f"{p_type} {p_name}"

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            if self.partner_id:
                query = "UPDATE partners SET name = %s, inn = %s, phone = %s, email = %s WHERE id = %s;"
                cursor.execute(query, (full_company_name, p_inn, p_phone, p_email, self.partner_id))
            else:
                cursor.execute("SELECT COALESCE(MAX(id), 0) + 1 FROM partners;")
                next_id = cursor.fetchone()[0]
                query = "INSERT INTO partners (id, name, inn, phone, email) VALUES (%s, %s, %s, %s, %s);"
                cursor.execute(query, (next_id, full_company_name, p_inn, p_phone, p_email))
            
            conn.commit()
            cursor.close()
            conn.close()

            messagebox.showinfo("Успех", "Данные успешно сохранены!")
            self.parent.refresh_data()
            self.destroy()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка СУБД: {e}")


class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("CRM: Реестр партнеров")
        self.geometry("850x600")
        self.configure(bg="#F2F2F2")

        try:
            self.iconbitmap("resources/icon.ico")
        except Exception:
            pass

        self.selected_partner_id = None
        self.selected_partner_name = None
        self.selected_card_widget = None

        header_frame = tk.Frame(self, bg="#FFFFFF", height=65)
        header_frame.pack(fill="x", side="top")
        header_frame.pack_propagate(False)

        lbl_logo = tk.Label(header_frame, text="[ ЛОГОТИП ]", font=("Arial", 10, "italic"), bg="#EAEAEA", width=12)
        lbl_logo.pack(side="left", padx=15, pady=12)

        lbl_page_title = tk.Label(header_frame, text="Реестр партнеров и скидок", font=("Arial", 14, "bold"), bg="#FFFFFF")
        lbl_page_title.pack(side="left", padx=10)

        btn_add = tk.Button(header_frame, text="Добавить партнера", font=("Arial", 10), command=self.open_add_window)
        btn_add.pack(side="right", padx=15, pady=15)

        self.btn_history = tk.Button(header_frame, text="История продаж", font=("Arial", 10), state="disabled", command=self.open_history_window)
        self.btn_history.pack(side="right", padx=5, pady=15)

        self.canvas = tk.Canvas(self, bg="#F2F2F2", highlightthickness=0)
        scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg="#F2F2F2")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw", width=820)
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scrollbar.pack(side="right", fill="y")

        self.refresh_data()

    def select_partner(self, widget, partner_id, name):
        if self.selected_card_widget and self.selected_card_widget.winfo_exists():
            self.selected_card_widget.config(bg="white")
            for child in self.selected_card_widget.winfo_children():
                child.config(bg="white")

        self.selected_partner_id = partner_id
        self.selected_partner_name = name
        self.selected_card_widget = widget
        
        self.selected_card_widget.config(bg="#E0EEEE")
        for child in self.selected_card_widget.winfo_children():
            child.config(bg="#E0EEEE")
            
        self.btn_history.config(state="normal")

    def create_partner_card(self, partner_id, name, phone, email, discount):
        card = tk.Frame(self.scrollable_frame, bd=1, relief="solid", bg="white", cursor="hand2")
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

        card.bind("<Button-1>", lambda event: self.select_partner(card, partner_id, name))
        info_frame.bind("<Button-1>", lambda event: self.select_partner(card, partner_id, name))
        lbl_title.bind("<Button-1>", lambda event: self.select_partner(card, partner_id, name))
        lbl_phone.bind("<Button-1>", lambda event: self.select_partner(card, partner_id, name))
        lbl_email.bind("<Button-1>", lambda event: self.select_partner(card, partner_id, name))
        discount_frame.bind("<Button-1>", lambda event: self.select_partner(card, partner_id, name))
        lbl_discount.bind("<Button-1>", lambda event: self.select_partner(card, partner_id, name))

        card.bind("<Double-1>", lambda event: self.open_edit_window(partner_id))
        info_frame.bind("<Double-1>", lambda event: self.open_edit_window(partner_id))
        lbl_title.bind("<Double-1>", lambda event: self.open_edit_window(partner_id))

    def refresh_data(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        self.selected_partner_id = None
        self.selected_partner_name = None
        self.selected_card_widget = None
        self.btn_history.config(state="disabled")

        partners = load_partners_from_db()

        if not partners:
            lbl_empty = tk.Label(self.scrollable_frame, text="Данные не найдены или нет связи с СУБД.", font=("Arial", 11), bg="#F2F2F2")
            lbl_empty.pack(pady=20)
        else:
            for p in partners:
                self.create_partner_card(
                    partner_id=p["partner_id"],
                    name=p["partner_name"],
                    phone=p["phone"],
                    email=p["email"],
                    discount=p["discount_percentage"]
                )

    def open_add_window(self):
        PartnerEditWindow(self, partner_id=None)

    def open_edit_window(self, partner_id):
        PartnerEditWindow(self, partner_id=partner_id)

    def open_history_window(self):
        if self.selected_partner_id:
            PartnerHistoryWindow(self, self.selected_partner_id, self.selected_partner_name)


if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()