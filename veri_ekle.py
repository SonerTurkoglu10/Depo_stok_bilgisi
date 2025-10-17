import sqlite3

veriler = [
    ("Laptop", 25, 20000),
    ("Mouse", 100, 300),
    ("Klavye", 50, 500),
]

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

cursor.executemany("INSERT INTO urunler (urun_adi, stok, birim_fiyat) VALUES (?, ?, ?)", veriler)

conn.commit()
conn.close()

print("Örnek ürünler eklendi ✅")
