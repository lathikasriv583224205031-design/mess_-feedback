from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

# ---------------- DATABASE ----------------
def get_db():
    return sqlite3.connect("database.db")

def create_table():
    conn = get_db()
    cursor = conn.cursor()

    # Feedback table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        food TEXT,
        rating INTEGER,
        comment TEXT
    )
    """)

    # Orders table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        items TEXT
    )
    """)

    conn.commit()
    conn.close()

create_table()

# ---------------- FOOD PRICES ----------------
food_prices = {
    "idli": 10,
    "dosa": 20,
    "rice": 30,
    "meals": 50,
    "chapati": 15,
    "parotta": 25
}

# ---------------- ROUTES ----------------

# Login Page
@app.route('/')
def login():
    return render_template("login.html")

# Menu Page
@app.route('/menu')
def menu():
    return render_template("menu.html")

# ---------------- ORDER ----------------
@app.route('/order', methods=['GET', 'POST'])
def order():
    if request.method == 'POST':
        name = request.form['name']

        food_list = ["idli", "dosa", "rice", "meals", "chapati", "parotta"]
        items = []
        total = 0

        for food in food_list:
            qty = request.form.get(food)

            if qty and qty != "":
                qty = int(qty)
                if qty > 0:
                    price = food_prices[food]
                    cost = qty * price
                    total += cost

                    items.append(f"{food}({qty}) = ₹{cost}")

        items_str = ", ".join(items)

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO orders (name, items) VALUES (?, ?)",
            (name, items_str + f" | Total = ₹{total}")
        )
        conn.commit()
        conn.close()

        return redirect('/menu')

    return render_template("order.html")

# ---------------- FEEDBACK ----------------
@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if request.method == 'POST':
        name = request.form['name']
        food = request.form['food']
        rating = request.form['rating']
        comment = request.form['comment']

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO feedback (name, food, rating, comment) VALUES (?, ?, ?, ?)",
            (name, food, rating, comment)
        )
        conn.commit()
        conn.close()

        return redirect('/menu')

    return render_template("feedback.html")

# ---------------- ADMIN ----------------
@app.route('/admin')
def admin():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM feedback")
    feedback_data = cursor.fetchall()

    cursor.execute("SELECT * FROM orders")
    order_data = cursor.fetchall()

    conn.close()

    return render_template("admin.html", feedback=feedback_data, orders=order_data)

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)