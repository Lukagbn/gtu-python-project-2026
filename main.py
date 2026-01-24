import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime

# ---------------- DATABASE ----------------
def connect_db():
    return sqlite3.connect("supermarket.db")

def create_tables():
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        price REAL,
        quantity INTEGER
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS sales (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER,
        quantity INTEGER,
        total REAL,
        date TEXT
    )
    """)

    conn.commit()
    conn.close()

create_tables()

# ---------------- CART ----------------
cart = []

def add_to_cart():
    pid = entry_sell_id.get()
    qty = entry_sell_qty.get()

    if not pid or not qty:
        messagebox.showerror("შეცდომა", "შეავსე ყველა ველი")
        return

    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT name, price, quantity FROM products WHERE id=?", (pid,))
    p = cur.fetchone()
    conn.close()

    if not p:
        messagebox.showerror("შეცდომა", "პროდუქტი ვერ მოიძებნა")
        return

    name, price, stock = p
    qty = int(qty)

    if qty > stock:
        messagebox.showerror("შეცდომა", "მარაგი არასაკმარისია")
        return

    cart.append((int(pid), name, price, qty))
    
    entry_sell_id.delete(0, tk.END)
    entry_sell_qty.delete(0, tk.END)
    
    update_cart_display()

def update_cart_display():
    cart_tree.delete(*cart_tree.get_children())
    total = 0
    
    for i, (pid, name, price, qty) in enumerate(cart):
        subtotal = price * qty
        total += subtotal
        cart_tree.insert("", tk.END, values=(i+1, name, qty, f"{price:.2f} ₾", f"{subtotal:.2f} ₾"))
    
    lbl_cart_total.config(text=f"სულ: {total:.2f} ₾")

def remove_from_cart():
    selected = cart_tree.selection()
    if not selected:
        messagebox.showwarning("გაფრთხილება", "აირჩიე პროდუქტი")
        return
    
    item = cart_tree.item(selected[0])
    index = int(item['values'][0]) - 1
    
    cart.pop(index)
    update_cart_display()

def clear_cart():
    if not cart:
        messagebox.showinfo("ინფორმაცია", "კალათა უკვე ცარიელია")
        return
    
    confirm = messagebox.askyesno("დადასტურება", "დარწმუნებული ხარ რომ გსურს კალათის გასუფთავება?")
    if confirm:
        cart.clear()
        update_cart_display()

def complete_sale():
    if not cart:
        messagebox.showwarning("გაფრთხილება", "კალათა ცარიელია")
        return

    conn = connect_db()
    cur = conn.cursor()
    
    try:
        for pid, name, price, qty in cart:
            cur.execute("UPDATE products SET quantity = quantity - ? WHERE id = ?", (qty, pid))
            total = price * qty
            cur.execute(
                "INSERT INTO sales (product_id, quantity, total, date) VALUES (?, ?, ?, ?)",
                (pid, qty, total, datetime.now().strftime("%Y-%m-%d %H:%M"))
            )
        
        conn.commit()
        messagebox.showinfo("წარმატება", "✓ გაიყიდა წარმატებით!")
        
        cart.clear()
        update_cart_display()
        
    except Exception as e:
        conn.rollback()
        messagebox.showerror("შეცდომა", f"გაყიდვა ვერ მოხერხდა: {e}")
    finally:
        conn.close()

# ---------------- TREEVIEW ----------------
def clear_tree(columns):
    tree.delete(*tree.get_children())
    tree["columns"] = columns
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, anchor="center", width=150)

# ---------------- VIEW SWITCHERS ----------------
def switch_sales_view(view):
    sales_main.grid_remove()
    sales_search.grid_remove()
    view.grid()

def switch_manage_view(view):
    manage_products.grid_remove()
    manage_sales.grid_remove()
    manage_add.grid_remove()
    product_actions.grid_remove()
    view.grid(sticky="nsew")

# ---------------- FUNCTIONS ----------------
def search_product():
    pid = entry_search_id.get()
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT name, price, quantity FROM products WHERE id=?", (pid,))
    p = cur.fetchone()
    conn.close()

    if p:
        lbl_search_result.config(
            text=f"დასახელება: {p[0]}\nფასი: {p[1]} ₾\nმარაგი: {p[2]}"
        )
    else:
        lbl_search_result.config(text="პროდუქტი ვერ მოიძებნა")

def show_products():
    switch_manage_view(manage_products)
    clear_tree(("ID", "დასახელება", "ფასი", "მარაგი"))

    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT id, name, price, quantity FROM products")

    for r in cur.fetchall():
        tree.insert("", tk.END, values=r)

    conn.close()
    product_actions.grid()

def show_sales():
    switch_manage_view(manage_sales)
    clear_tree(("ID", "პროდუქტი", "რაოდენობა", "ჯამი ₾", "თარიღი"))

    conn = connect_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT sales.id, products.name, sales.quantity, sales.total, sales.date
        FROM sales JOIN products ON sales.product_id = products.id
        ORDER BY sales.date DESC
    """)

    for r in cur.fetchall():
        tree.insert("", tk.END, values=r)

    conn.close()
    product_actions.grid_remove()

def add_product():
    name = entry_name.get()
    price = entry_price.get()
    qty = entry_qty.get()

    if not name or not price or not qty:
        messagebox.showerror("შეცდომა", "შეავსე ყველა ველი")
        return

    conn = connect_db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO products (name, price, quantity) VALUES (?, ?, ?)",
        (name, float(price), int(qty))
    )
    conn.commit()
    conn.close()

    entry_name.delete(0, tk.END)
    entry_price.delete(0, tk.END)
    entry_qty.delete(0, tk.END)

    messagebox.showinfo("წარმატება", "პროდუქტი დაემატა")
    show_products()

def delete_product():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("გაფრთხილება", "აირჩიე პროდუქტი")
        return
    
    item = tree.item(selected[0])
    product_id = item['values'][0]
    product_name = item['values'][1]
    
    confirm = messagebox.askyesno("დადასტურება", 
                                   f"დარწმუნებული ხარ რომ გსურს '{product_name}'-ის წაშლა?")
    if confirm:
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("DELETE FROM products WHERE id=?", (product_id,))
        conn.commit()
        conn.close()
        
        messagebox.showinfo("წარმატება", "პროდუქტი წაიშალა")
        show_products()

def edit_product():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("გაფრთხილება", "აირჩიე პროდუქტი")
        return
    
    item = tree.item(selected[0])
    product_id = item['values'][0]
    current_name = item['values'][1]
    current_price = item['values'][2]
    current_qty = item['values'][3]
    
    edit_window = tk.Toplevel(root)
    edit_window.title("რედაქტირება")
    edit_window.geometry("450x300")
    edit_window.resizable(False, False)
    edit_window.configure(bg="#f0f0f0")
    
    # ცენტრში განთავსება
    frame = tk.Frame(edit_window, bg="#ffffff", relief="raised", borderwidth=2)
    frame.pack(expand=True, fill="both", padx=20, pady=20)
    
    header = tk.Label(frame, text=f"პროდუქტის რედაქტირება (ID: {product_id})", 
                     font=("Segoe UI", 14, "bold"), bg="#ffffff", fg="#2c3e50")
    header.pack(pady=15)
    
    form_frame = tk.Frame(frame, bg="#ffffff")
    form_frame.pack(pady=10)
    
    tk.Label(form_frame, text="დასახელება:", font=("Segoe UI", 10), 
             bg="#ffffff", fg="#34495e").grid(row=0, column=0, sticky="e", padx=10, pady=8)
    edit_name = tk.Entry(form_frame, width=25, font=("Segoe UI", 10), relief="solid", borderwidth=1)
    edit_name.insert(0, current_name)
    edit_name.grid(row=0, column=1, pady=8)
    
    tk.Label(form_frame, text="ფასი:", font=("Segoe UI", 10), 
             bg="#ffffff", fg="#34495e").grid(row=1, column=0, sticky="e", padx=10, pady=8)
    edit_price = tk.Entry(form_frame, width=25, font=("Segoe UI", 10), relief="solid", borderwidth=1)
    edit_price.insert(0, current_price)
    edit_price.grid(row=1, column=1, pady=8)
    
    tk.Label(form_frame, text="რაოდენობა:", font=("Segoe UI", 10), 
             bg="#ffffff", fg="#34495e").grid(row=2, column=0, sticky="e", padx=10, pady=8)
    edit_qty = tk.Entry(form_frame, width=25, font=("Segoe UI", 10), relief="solid", borderwidth=1)
    edit_qty.insert(0, current_qty)
    edit_qty.grid(row=2, column=1, pady=8)
    
    def save_changes():
        new_name = edit_name.get()
        new_price = edit_price.get()
        new_qty = edit_qty.get()
        
        if not new_name or not new_price or not new_qty:
            messagebox.showerror("შეცდომა", "შეავსე ყველა ველი")
            return
        
        try:
            conn = connect_db()
            cur = conn.cursor()
            cur.execute(
                "UPDATE products SET name=?, price=?, quantity=? WHERE id=?",
                (new_name, float(new_price), int(new_qty), product_id)
            )
            conn.commit()
            conn.close()
            
            messagebox.showinfo("წარმატება", "პროდუქტი განახლდა")
            edit_window.destroy()
            show_products()
        except ValueError:
            messagebox.showerror("შეცდომა", "არასწორი ფორმატი")
    
    btn_frame = tk.Frame(frame, bg="#ffffff")
    btn_frame.pack(pady=20)
    
    save_btn = tk.Button(btn_frame, text="შენახვა", command=save_changes, 
                         bg="#27ae60", fg="white", font=("Segoe UI", 10, "bold"),
                         width=12, height=1, relief="flat", cursor="hand2")
    save_btn.pack(side="left", padx=5)
    
    cancel_btn = tk.Button(btn_frame, text="გაუქმება", command=edit_window.destroy,
                           bg="#95a5a6", fg="white", font=("Segoe UI", 10, "bold"),
                           width=12, height=1, relief="flat", cursor="hand2")
    cancel_btn.pack(side="left", padx=5)

# ---------------- GUI ----------------
root = tk.Tk()
root.title("🛒 Supermarket System")
root.geometry("1100x700")
root.configure(bg="#ecf0f1")

# სტილები
style = ttk.Style()
style.theme_use('clam')

# Notebook სტილი
style.configure("TNotebook", background="#ecf0f1", borderwidth=0)
style.configure("TNotebook.Tab", 
                background="#bdc3c7", 
                foreground="#2c3e50",
                padding=[20, 10],
                font=("Segoe UI", 11, "bold"))
style.map("TNotebook.Tab",
          background=[("selected", "#3498db")],
          foreground=[("selected", "white")])

# Frame სტილები
style.configure("TFrame", background="#ecf0f1")
style.configure("TLabelframe", background="#ffffff", relief="raised")
style.configure("TLabelframe.Label", 
                background="#ffffff", 
                foreground="#2c3e50",
                font=("Segoe UI", 11, "bold"))

# Button სტილები
style.configure("TButton",
                background="#3498db",
                foreground="white",
                borderwidth=0,
                focuscolor="none",
                font=("Segoe UI", 10, "bold"),
                padding=[15, 8])
style.map("TButton",
          background=[("active", "#2980b9")])

# Accent Button
style.configure("Accent.TButton",
                background="#27ae60",
                foreground="white",
                font=("Segoe UI", 11, "bold"),
                padding=[20, 10])
style.map("Accent.TButton",
          background=[("active", "#229954")])

# Delete Button
style.configure("Delete.TButton",
                background="#e74c3c",
                foreground="white",
                font=("Segoe UI", 10, "bold"))
style.map("Delete.TButton",
          background=[("active", "#c0392b")])

# Edit Button
style.configure("Edit.TButton",
                background="#f39c12",
                foreground="white",
                font=("Segoe UI", 10, "bold"))
style.map("Edit.TButton",
          background=[("active", "#e67e22")])

# Label სტილები
style.configure("TLabel",
                background="#ffffff",
                foreground="#34495e",
                font=("Segoe UI", 10))

style.configure("Header.TLabel",
                font=("Segoe UI", 16, "bold"),
                foreground="#2c3e50")

# Entry სტილები
style.configure("TEntry",
                fieldbackground="white",
                borderwidth=1,
                relief="solid")

# Treeview სტილები
style.configure("Treeview",
                background="white",
                foreground="#2c3e50",
                rowheight=30,
                fieldbackground="white",
                font=("Segoe UI", 10))
style.configure("Treeview.Heading",
                background="#34495e",
                foreground="white",
                font=("Segoe UI", 11, "bold"),
                relief="flat")
style.map("Treeview",
          background=[("selected", "#3498db")])

notebook = ttk.Notebook(root)
notebook.pack(expand=True, fill="both", padx=10, pady=10)

# ================= SALES TAB =================
tab_sales = ttk.Frame(notebook)
notebook.add(tab_sales, text="📊 სარეალიზაციო")

sales_top = ttk.Frame(tab_sales)
sales_top.grid(row=0, column=0, padx=15, pady=10, sticky="w")

ttk.Button(sales_top, text="მთავარი",
           command=lambda: switch_sales_view(sales_main)).grid(row=0, column=0, padx=5)
ttk.Button(sales_top, text="პროდუქტის ძიება",
           command=lambda: switch_sales_view(sales_search)).grid(row=0, column=1, padx=5)

sales_main = ttk.Frame(tab_sales)
sales_main.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")

tab_sales.rowconfigure(1, weight=1)
tab_sales.columnconfigure(0, weight=1)

# ზედა ნაწილი - დამატება და ჯამი
top_container = ttk.Frame(sales_main)
top_container.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
top_container.columnconfigure(0, weight=1)
top_container.columnconfigure(1, weight=0)
top_container.rowconfigure(0, weight=1)

# პროდუქტის დამატება
add_frame = ttk.LabelFrame(top_container, text="🛍️ პროდუქტის დამატება", padding=15)
add_frame.grid(row=0, column=0, padx=(0, 10), sticky="nsew")

ttk.Label(add_frame, text="პროდუქტის ID:").grid(row=0, column=0, padx=5, pady=8, sticky="w")
entry_sell_id = ttk.Entry(add_frame, width=25, font=("Segoe UI", 10))
entry_sell_id.grid(row=0, column=1, padx=5, pady=8)

ttk.Label(add_frame, text="რაოდენობა:").grid(row=1, column=0, padx=5, pady=8, sticky="w")
entry_sell_qty = ttk.Entry(add_frame, width=25, font=("Segoe UI", 10))
entry_sell_qty.grid(row=1, column=1, padx=5, pady=8)

ttk.Button(add_frame, text="➕ კალათში დამატება", command=add_to_cart)\
    .grid(row=2, column=0, columnspan=2, pady=15)

# სულ ჯამი
total_frame = ttk.LabelFrame(top_container, text="💰 სულ ჯამი", padding=15)
total_frame.grid(row=0, column=1, sticky="nsew")

lbl_cart_total = ttk.Label(total_frame, text="0.00 ₾", 
                           font=("Segoe UI", 24, "bold"), 
                           foreground="#27ae60")
lbl_cart_total.pack(pady=(10, 15), padx=30)

ttk.Button(total_frame, text="✓ გაყიდვა", command=complete_sale, style="Accent.TButton")\
    .pack(pady=5, padx=20, fill="x")

ttk.Button(total_frame, text="🗑️ ამოღება კალათიდან", command=remove_from_cart, style="Delete.TButton")\
    .pack(pady=5, padx=20, fill="x")

ttk.Button(total_frame, text="🧹 კალათის გასუფთავება", command=clear_cart, style="Delete.TButton")\
    .pack(pady=5, padx=20, fill="x")

# კალათა
cart_frame = ttk.LabelFrame(sales_main, text="🛒 კალათა", padding=15)
cart_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

sales_main.rowconfigure(1, weight=1)
sales_main.columnconfigure(0, weight=1)

cart_tree = ttk.Treeview(cart_frame, columns=("N", "დასახელება", "რაოდ.", "ფასი", "ჯამი"), 
                         show="headings", height=12)
cart_tree.heading("N", text="N")
cart_tree.heading("დასახელება", text="დასახელება")
cart_tree.heading("რაოდ.", text="რაოდ.")
cart_tree.heading("ფასი", text="ფასი")
cart_tree.heading("ჯამი", text="ჯამი")

cart_tree.column("N", width=50, anchor="center")
cart_tree.column("დასახელება", width=250)
cart_tree.column("რაოდ.", width=100, anchor="center")
cart_tree.column("ფასი", width=120, anchor="e")
cart_tree.column("ჯამი", width=120, anchor="e")

cart_tree.pack(fill="both", expand=True, pady=(0, 10))

# პროდუქტის ძიება
sales_search = ttk.Frame(tab_sales)
sales_search_inner = ttk.LabelFrame(sales_search, text="🔍 პროდუქტის ძიება", padding=30)
sales_search_inner.pack(padx=50, pady=50)

ttk.Label(sales_search_inner, text="პროდუქტის ID:").grid(row=0, column=0, padx=10, pady=10)
entry_search_id = ttk.Entry(sales_search_inner, width=30, font=("Segoe UI", 10))
entry_search_id.grid(row=0, column=1, padx=10, pady=10)

ttk.Button(sales_search_inner, text="🔍 ძებნა", command=search_product)\
    .grid(row=1, column=0, columnspan=2, pady=15)

lbl_search_result = ttk.Label(sales_search_inner, font=("Segoe UI", 11))
lbl_search_result.grid(row=2, column=0, columnspan=2, pady=15)

# ================= MANAGEMENT TAB =================
tab_manage = ttk.Frame(notebook)
notebook.add(tab_manage, text="⚙️ მენეჯმენტი")

tab_manage.rowconfigure(1, weight=1)
tab_manage.columnconfigure(0, weight=1)

manage_top = ttk.Frame(tab_manage)
manage_top.grid(row=0, column=0, padx=15, pady=10, sticky="w")

ttk.Button(manage_top, text="📦 ყველა პროდუქტი", command=show_products).grid(row=0, column=0, padx=5)
ttk.Button(manage_top, text="💰 გაყიდვები", command=show_sales).grid(row=0, column=1, padx=5)
ttk.Button(manage_top, text="➕ ახალი პროდუქტი",
           command=lambda: switch_manage_view(manage_add)).grid(row=0, column=2, padx=5)

product_actions = ttk.Frame(manage_top)
product_actions.grid(row=0, column=3, padx=20)

ttk.Button(product_actions, text="✏️ რედაქტირება", command=edit_product, style="Edit.TButton").pack(side="left", padx=5)
ttk.Button(product_actions, text="🗑️ წაშლა", command=delete_product, style="Delete.TButton").pack(side="left", padx=5)
product_actions.grid_remove()

# PRODUCTS VIEW
manage_products = ttk.Frame(tab_manage)
manage_products.grid(row=1, column=0, sticky="nsew", padx=15, pady=10)

tree = ttk.Treeview(manage_products, show="headings")
tree.pack(expand=True, fill="both")

scroll = ttk.Scrollbar(manage_products, orient="vertical", command=tree.yview)
scroll.pack(side="right", fill="y")
tree.configure(yscrollcommand=scroll.set)

# SALES VIEW
manage_sales = manage_products

# ADD PRODUCT VIEW
manage_add = ttk.Frame(tab_manage)
manage_add.columnconfigure(0, weight=1)
manage_add.rowconfigure(0, weight=1)

add_box = ttk.LabelFrame(manage_add, text="➕ ახალი პროდუქტის დამატება", padding=30)
add_box.grid(row=0, column=0)

ttk.Label(add_box, text="დასახელება:", font=("Segoe UI", 10)).grid(row=0, column=0, pady=10, sticky="e", padx=10)
entry_name = ttk.Entry(add_box, width=35, font=("Segoe UI", 10))
entry_name.grid(row=0, column=1, pady=10)

ttk.Label(add_box, text="ფასი:", font=("Segoe UI", 10)).grid(row=1, column=0, pady=10, sticky="e", padx=10)
entry_price = ttk.Entry(add_box, width=35, font=("Segoe UI", 10))
entry_price.grid(row=1, column=1, pady=10)

ttk.Label(add_box, text="რაოდენობა:", font=("Segoe UI", 10)).grid(row=2, column=0, pady=10, sticky="e", padx=10)
entry_qty = ttk.Entry(add_box, width=35, font=("Segoe UI", 10))
entry_qty.grid(row=2, column=1, pady=10)

ttk.Button(add_box, text="✓ დამატება", command=add_product, style="Accent.TButton")\
    .grid(row=3, column=0, columnspan=2, pady=20)

show_products()

root.mainloop()