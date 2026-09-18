import tkinter as tk
from tkinter import ttk


def create_partner_card(parent, partner_type, name, director, phone, rating, discount):
    card = tk.Frame(parent, bd=1, relief="solid", bg="white")
    card.pack(fill="x", padx=10, pady=5)

    info_frame = tk.Frame(card, bg="white")
    info_frame.pack(side="left", fill="both", expand=True, padx=15, pady=10)

    title_text = f"{partner_type} | {name}"
    lbl_title = tk.Label(info_frame, text=title_text, font=("Arial", 12, "bold"), bg="white", anchor="w")
    lbl_title.pack(fill="x")

    lbl_director = tk.Label(info_frame, text=director, font=("Arial", 10), bg="white", anchor="w")
    lbl_director.pack(fill="x")

    lbl_phone = tk.Label(info_frame, text=phone, font=("Arial", 10), bg="white", anchor="w")
    lbl_phone.pack(fill="x")

    rating_text = f"Рейтинг: {rating}"
    lbl_rating = tk.Label(info_frame, text=rating_text, font=("Arial", 10), bg="white", anchor="w")
    lbl_rating.pack(fill="x")

    discount_frame = tk.Frame(card, bg="white")
    discount_frame.pack(side="right", fill="y", padx=15, pady=10)

    discount_text = f"{discount}%"
    lbl_discount = tk.Label(discount_frame, text=discount_text, font=("Arial", 14, "bold"), bg="white", anchor="e")
    lbl_discount.pack(expand=True)


def main():
    root = tk.Tk()
    root.title("CRM: Список партнеров и скидок")
    root.geometry("700x550")
    root.configure(bg="#F2F2F2")

    header_frame = tk.Frame(root, bg="#FFFFFF", height=60)
    header_frame.pack(fill="x", side="top")
    header_frame.pack_propagate(False)

    lbl_page_title = tk.Label(header_frame, text="Список партнеров", font=("Arial", 14, "bold"), bg="#FFFFFF")
    lbl_page_title.pack(side="left", padx=10)

    main_frame = tk.Frame(root, bg="#F2F2F2")
    main_frame.pack(fill="both", expand=True, padx=10, pady=10)

    create_partner_card(main_frame, "ЗАО", "База Строительной Комплектации", "Иванов Иван Иванович", "+7 223 322 22 32", "10", "10")
    create_partner_card(main_frame, "ООО", "Логистик Экспресс", "Петров Алексей Владимирович", "+7 999 123 45 67", "8", "5")
    create_partner_card(main_frame, "ИП", "Сидоров С.С.", "Сидоров Сергей Сергеевич", "+7 888 765 43 21", "10", "15")

    root.mainloop()


if __name__ == "__main__":
    main()
