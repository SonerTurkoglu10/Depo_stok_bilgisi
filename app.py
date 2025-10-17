from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3

app = Flask(__name__)
app.secret_key = 'dev-secret-key-change-me'

# Anasayfa
@app.route('/', methods=['GET', 'POST'])
def anasayfa():
    # Veritabanına bağlan
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Tablo oluştur (yoksa)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS urunler (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            urun_adi TEXT NOT NULL,
            stok INTEGER NOT NULL,
            birim_fiyat REAL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS satislar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            urun_id INTEGER,
            tarih TEXT,
            adet INTEGER,
            FOREIGN KEY(urun_id) REFERENCES urunler(id)
        )
    ''')

    conn.commit()

    # Ürünleri getir (id, urun_adi, stok, birim_fiyat)
    cursor.execute("SELECT id, urun_adi, stok, birim_fiyat FROM urunler")
    urunler = cursor.fetchall()

    stok_bilgisi = None

    if request.method == 'POST':
        urun_id = request.form.get('urun')
        cursor.execute("SELECT urun_adi, stok FROM urunler WHERE id=?", (urun_id,))
        stok_bilgisi = cursor.fetchone()

    conn.close()
    return render_template('index.html', urunler=urunler, stok_bilgisi=stok_bilgisi)

@app.route('/ekle', methods=['POST'])

def ekle():
    urun_adi = request.form.get('urun_adi')
    stok = request.form.get('stok')
    birim_fiyat = request.form.get('birim_fiyat')

    if not urun_adi or stok is None:
        flash('Ürün adı ve stok zorunludur.')
        return redirect(url_for('anasayfa'))

    try:
        stok = int(stok)
        birim_fiyat = float(birim_fiyat) if birim_fiyat not in (None, '') else None
    except ValueError:
        flash('Stok veya birim fiyat hatalı formatta.')
        return redirect(url_for('anasayfa'))

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    # Aynı isimde ürün var mı?
    cursor.execute("SELECT id, stok FROM urunler WHERE urun_adi=?", (urun_adi,))
    mevcut = cursor.fetchone()
    if mevcut:
        # Stok artır
        yeni_stok = mevcut[1] + stok
        cursor.execute("UPDATE urunler SET stok=?, birim_fiyat=? WHERE id=?", (yeni_stok, birim_fiyat, mevcut[0]))
        conn.commit()
        conn.close()
        flash(f"'{urun_adi}' ürünü zaten var. Stok artırıldı: {mevcut[1]} → {yeni_stok}")
        return redirect(url_for('anasayfa'))
    else:
        # Yeni ürün ekle
        cursor.execute("INSERT INTO urunler (urun_adi, stok, birim_fiyat) VALUES (?, ?, ?)", (urun_adi, stok, birim_fiyat))
        conn.commit()
        conn.close()
        flash(f"'{urun_adi}' ürünü eklendi.")
        return redirect(url_for('anasayfa'))


# Ürünü tükendi olarak işaretle
@app.route('/tukendi/<int:urun_id>', methods=['POST'])
def tukendi(urun_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE urunler SET stok=0 WHERE id=?", (urun_id,))
    conn.commit()
    conn.close()
    flash(f"ID {urun_id} ürün tükendi olarak işaretlendi.")
    return redirect(url_for('anasayfa'))

if __name__ == '__main__':
    app.run(debug=True)
