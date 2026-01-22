import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from db import create_database

# ---------- DATABASE ----------
def connect_db():
    return sqlite3.connect("supermarket.db")


create_database()

# ---------- FUNCTIONS ----------
def add_product():
    name = entry_name.get()
    category = entry_category.get()
    price = entry_price.get()
    quantity = entry_quantity.get()

    if name == "" or price == "" or quantity == "":
        messagebox.showerror("შეცდომა", "შეავსე ყველა აუცილებელი ველი")
        return

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO products (name, category, price, quantity) VALUES (?, ?, ?, ?)",
        (name, category, float(price), int(quantity))
    )
    conn.commit()
    conn.close()

    messagebox.showinfo("წარმატება", "პროდუქტი დაემატა")

    entry_name.delete(0, tk.END)
    entry_category.delete(0, tk.END)
    entry_price.delete(0, tk.END)
    entry_quantity.delete(0, tk.END)

def get_product_by_id():
    product_id = entry_search_id.get()

    if product_id == "":
        messagebox.showerror("შეცდომა", "შეიყვანე ID")
        return

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
    result = cursor.fetchone()
    conn.close()

    text_result.delete("1.0", tk.END)

    if result:
        text_result.insert(
            tk.END,
            f"ID: {result[0]}\n"
            f"დასახელება: {result[1]}\n"
            f"კატეგორია: {result[2]}\n"
            f"ფასი: {result[3]} ₾\n"
            f"რაოდენობა: {result[4]}"
        )
    else:
        text_result.insert(tk.END, "პროდუქტი ვერ მოიძებნა")

def show_all_products():
    listbox.delete(0, tk.END)

    # სათაურები
    header = (
        f"{' ID | ':<5}"
        f"{' დასახელება |':<20}"
        f"{' კატეგორია |':<15}"
        f"{' ფასი |':<10}"
        f"{' რაოდენობა |':<10}"
    )

    listbox.insert(tk.END, header)
    listbox.insert(tk.END, "-" * 60)

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")

    for row in cursor.fetchall():
        line = (
            f"{str(row[0]):<5}"
            f"{row[1]:<20}"
            f"{row[2]:<15}"
            f"{row[3]:<10}"
            f"{row[4]:<10}"
        )
        listbox.insert(tk.END, line)

    conn.close()



# def show_all_products():
#     listbox.delete(0, tk.END)

#     conn = connect_db()
#     cursor = conn.cursor()
#     cursor.execute("SELECT * FROM products")

#     for row in cursor.fetchall():
#         listbox.insert(
#             tk.END,
#             f"ID:{row[0]} | {row[1]} | {row[2]} | {row[3]} ₾ | რაოდენობა: {row[4]}"
#         )

#     conn.close()

# ---------- GUI ----------
root = tk.Tk()
root.title("სუპერმარკეტის მართვის სისტემა")
root.geometry("650x500")

notebook = ttk.Notebook(root)
notebook.pack(expand=True, fill="both")



# ---------- TAB 1: ALL PRODUCTS ----------
tab_all = ttk.Frame(notebook)
notebook.add(tab_all, text="ყველა პროდუქტი")

# ttk.Button(tab_all, text="განახლება", command=show_all_products).pack(pady=5)

listbox = tk.Listbox(tab_all, width=90)
listbox.pack(pady=10)
show_all_products()


# ---------- TAB 2: ADD PRODUCT ----------
tab_add = ttk.Frame(notebook)
notebook.add(tab_add, text="პროდუქტის დამატება")

ttk.Label(tab_add, text="დასახელება").pack(pady=2)
entry_name = ttk.Entry(tab_add)
entry_name.pack()

ttk.Label(tab_add, text="კატეგორია").pack(pady=2)
entry_category = ttk.Entry(tab_add)
entry_category.pack()

ttk.Label(tab_add, text="ფასი").pack(pady=2)
entry_price = ttk.Entry(tab_add)
entry_price.pack()

ttk.Label(tab_add, text="რაოდენობა").pack(pady=2)
entry_quantity = ttk.Entry(tab_add)
entry_quantity.pack()

ttk.Button(tab_add, text="დამატება", command=add_product).pack(pady=10)

# ---------- TAB 3: SEARCH BY ID ----------
tab_search = ttk.Frame(notebook)
notebook.add(tab_search, text="პროდუქტის ნახვა ID-ით")

ttk.Label(tab_search, text="პროდუქტის ID").pack(pady=5)
entry_search_id = ttk.Entry(tab_search)
entry_search_id.pack()

ttk.Button(tab_search, text="ძებნა", command=get_product_by_id).pack(pady=5)

text_result = tk.Text(tab_search, height=8, width=50)
text_result.pack(pady=10)



root.mainloop()
