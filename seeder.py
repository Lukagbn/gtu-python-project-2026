import sqlite3
from datetime import datetime, timedelta
import random

def seed_products():
    """პროდუქტების ბაზაში დამატება"""
    
    conn = sqlite3.connect("supermarket.db")
    cur = conn.cursor()
    
    products = [
        ("რძე", 3.50, 100),
        ("პური", 1.20, 150),
        ("ყველი", 8.00, 50),
        ("კვერცხი (10 ცალი)", 5.50, 80),
        ("წყალი 1.5ლ", 1.00, 200),
        ("ლუდი", 4.50, 120),
        ("ღვინო", 15.00, 60),
        ("ხორცი 1კგ", 25.00, 40),
        ("თევზი 1კგ", 18.00, 30),
        ("ბრინჯი 1კგ", 6.00, 70),
        ("შაქარი 1კგ", 3.00, 90),
        ("ზეთი 1ლ", 12.00, 50),
        ("კარტოფილი 1კგ", 2.50, 100),
        ("პომიდორი 1კგ", 4.00, 80),
        ("კიტრი 1კგ", 3.50, 75),
        ("ვაშლი 1კგ", 5.00, 60),
        ("ბანანი 1კგ", 4.50, 85),
        ("ყავა", 15.00, 45),
        ("ჩაი", 8.00, 55),
        ("შოკოლადი", 6.00, 100),
        ("ჩიფსი", 3.00, 120),
        ("წვნიანი", 2.50, 90),
        ("კეტჩუპი", 4.00, 70),
        ("მაიონეზი", 4.50, 65),
        ("სპაგეტი", 3.50, 80),
        ("მწვანილი", 2.00, 100),
        ("სუნელი", 3.00, 85),
        ("საპონი", 2.50, 110),
        ("შამპუნი", 8.00, 70),
        ("ლობიო 1კგ", 5.00, 60),
        ("იოგურტი", 2.50, 100),
        ("კარაქი", 6.00, 45),
        ("წიწაკა 1კგ", 7.00, 40),
        ("ხახვი 1კგ", 6.50, 50),
        ("ფორთოხალი 1კგ", 5.50, 70),
        ("ლიმონი 1კგ", 4.00, 65),
    ]
    
    try:
        cur.execute("SELECT COUNT(*) FROM products")
        count = cur.fetchone()[0]
        
        if count > 0:
            print(f"⚠️  ბაზაში უკვე არსებობს {count} პროდუქტი.")
            response = input("გსურს ყველას წაშლა და თავიდან დამატება? (y/n): ")
            
            if response.lower() == 'y':
                cur.execute("DELETE FROM products")
                print("🗑️  ძველი პროდუქტები წაიშალა")
            else:
                print("❌ ოპერაცია გაუქმდა")
                conn.close()
                return False
        
        cur.executemany(
            "INSERT INTO products (name, price, quantity) VALUES (?, ?, ?)",
            products
        )
        
        conn.commit()
        print(f"✅ წარმატებით დაემატა {len(products)} პროდუქტი!")
        
        print("\n📦 დამატებული პროდუქტები:")
        print("-" * 50)
        cur.execute("SELECT id, name, price, quantity FROM products")
        for row in cur.fetchall():
            print(f"ID: {row[0]:2d} | {row[1]:25s} | {row[2]:6.2f} ₾ | რაოდ: {row[3]}")
        
        return True
        
    except Exception as e:
        conn.rollback()
        print(f"❌ შეცდომა: {e}")
        return False
    finally:
        conn.close()

def seed_sales():
    """გაყიდვების ბაზაში დამატება"""
    
    conn = sqlite3.connect("supermarket.db")
    cur = conn.cursor()
    
    try:
        cur.execute("SELECT COUNT(*) FROM products")
        product_count = cur.fetchone()[0]
        
        if product_count == 0:
            print("⚠️  ბაზაში არ არის პროდუქტები. ჯერ დაამატე პროდუქტები!")
            conn.close()
            return
        
        cur.execute("SELECT id, name, price FROM products")
        products = cur.fetchall()
        
        cur.execute("SELECT COUNT(*) FROM sales")
        count = cur.fetchone()[0]
        
        if count > 0:
            print(f"⚠️  ბაზაში უკვე არსებობს {count} მონაცემი.")
            response = input("გსურს ყველას წაშლა და თავიდან დამატება? (y/n): ")
            
            if response.lower() == 'y':
                cur.execute("DELETE FROM sales")
                print("🗑️  ძველი მონაცემები წაიშალა")
            else:
                print("❌ ოპერაცია გაუქმდა")
                conn.close()
                return
        
        sales = []
        num_sales = 100  
        
        print(f"\n💰 {num_sales} გაყიდვის გენერირება...")
        
        for _ in range(num_sales):
            product = random.choice(products)
            product_id = product[0]
            price = product[2]
            
            quantity = random.randint(1, 10)
            
            total = price * quantity
            
            days_ago = random.randint(0, 30)
            hours = random.randint(8, 20)  
            minutes = random.randint(0, 59)
            
            sale_date = datetime.now() - timedelta(days=days_ago)
            sale_date = sale_date.replace(hour=hours, minute=minutes, second=0)
            date_str = sale_date.strftime("%Y-%m-%d %H:%M")
            
            sales.append((product_id, quantity, total, date_str))
        
        cur.executemany(
            "INSERT INTO sales (product_id, quantity, total, date) VALUES (?, ?, ?, ?)",
            sales
        )
        
        conn.commit()
        print(f"✅ წარმატებით დაემატა {len(sales)} მონაცემი!")

    except Exception as e:
        conn.rollback()
        print(f"❌ შეცდომა: {e}")
    finally:
        conn.close()

if __name__ == "__main__":

    
    print("\nპროდუქტების დამატება...")
    print("-" * 60)
    success = seed_products()
    
    if success or success is None:
        print("\n" + "=" * 60)
        
        print("\n2️⃣  გაყიდვების დამატება...")
        print("-" * 60)
        seed_sales()
    
    print("\n" + "=" * 60)
    print("✓ დასრულდა!")