from flask import Flask, render_template, request, redirect, url_for, flash, session
import mysql.connector
from datetime import date
from functools import wraps
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash

# INSERT INTO admin (username, password_hash) VALUES ('admin', '32768:8:1$8W0lkzE8dr3srHXz$de3d2bfe3d53c3af8f701fdd8f80abb2a59bf0d67c1c3af9f464593befa48255d689e8a1cc91c8203dcc05928bed9a876c349158b659d0a4b08d532bbdc9ae1a');



app = Flask(__name__)
app.secret_key = "rental_secret_2025"

# ---------------- MySQL Connection ----------------
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="admin123",
        database="rental_system"
    )
# print("hash password",generate_password_hash("admin123"))

# ---------------- AUTH DECORATOR ----------------
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin' not in session:
            flash("⚠️ Please log in first!", "warning")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# ---------------- LOGIN / LOGOUT ----------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM admin WHERE username = %s", (username,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user['password_hash'], password):
            session['admin'] = username
            flash(f"✅ Welcome {username}!", "success")
            return redirect(url_for('home'))
        else:
            flash("❌ Invalid username or password!", "danger")

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('admin', None)
    flash("👋 Logged out successfully!", "info")
    return redirect(url_for('login'))

# ---------------- HOME ----------------
@app.route('/')
@login_required
def home():
    return render_template('index.html')

# ---------------- TENANTS ----------------
@app.route('/tenants', methods=['GET', 'POST'])
@login_required
def tenants():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = "SELECT * FROM tenants"
    params = ()

    search_term = request.args.get('search')
    if search_term:
        query += " WHERE name LIKE %s OR address LIKE %s OR contact_number LIKE %s"
        wildcard = f"%{search_term}%"
        params = (wildcard, wildcard, wildcard)

    cursor.execute(query, params)
    tenants = cursor.fetchall()
    conn.close()

    return render_template('tenants.html', tenants=tenants, search_term=search_term or "")

@app.route('/add_tenant', methods=['POST'])
@login_required
def add_tenant():
    name = request.form['name']
    address = request.form['address']
    contact_number = request.form['contact_number']

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tenants (name, address, contact_number) VALUES (%s, %s, %s)",
                   (name, address, contact_number))
    conn.commit()
    conn.close()
    flash("✅ Tenant added successfully!", "success")
    return redirect(url_for('tenants'))

@app.route('/delete_tenant/<int:tenant_id>')
@login_required
def delete_tenant(tenant_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tenants WHERE id = %s", (tenant_id,))
    conn.commit()
    conn.close()
    flash("🗑️ Tenant deleted successfully!", "danger")
    return redirect(url_for('tenants'))

# ---------------- PAYMENTS ----------------
@app.route('/payments', methods=['GET', 'POST'])
@login_required
def payments():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = "SELECT * FROM payments"
    params = ()

    tenant_id = request.args.get('tenant_id')
    status = request.args.get('status')

    filters = []
    if tenant_id:
        filters.append("tenant_id = %s")
        params += (tenant_id,)
    if status:
        filters.append("status = %s")
        params += (status,)

    if filters:
        query += " WHERE " + " AND ".join(filters)

    cursor.execute(query, params)
    payments = cursor.fetchall()
    conn.close()

    return render_template('payments.html', payments=payments, tenant_id=tenant_id or "", status=status or "")

@app.route('/add_payment', methods=['POST'])
@login_required
def add_payment():
    tenant_id = int(request.form['tenant_id'])
    rent = float(request.form['rent'])
    amount_paid = float(request.form['amount_paid'])
    payment_date = date.today()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COALESCE(SUM(balance_change), 0) FROM payments WHERE tenant_id = %s", (tenant_id,))
    prev_balance = float(cursor.fetchone()[0] or 0.0)

    balance_change = round(amount_paid - rent, 2)
    new_balance = round(prev_balance + balance_change, 2)

    if new_balance < 0:
        pending_amount = abs(new_balance)
        advance_amount = 0.0
        status = "pending"
    elif new_balance == 0:
        pending_amount = 0.0
        advance_amount = 0.0
        status = "completed"
    else:
        pending_amount = 0.0
        advance_amount = new_balance
        status = "advance"

    sql = """
    INSERT INTO payments
    (tenant_id, rent, amount_paid, payment_date, status, balance_change, pending_amount, advance_amount)
    VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
    """
    cursor.execute(sql, (tenant_id, rent, amount_paid, payment_date, status, balance_change, pending_amount, advance_amount))
    conn.commit()
    conn.close()

    flash(f"💰 Payment recorded! Status: {status.title()} | Balance: ₹{new_balance}", "info")
    return redirect(url_for('payments'))

if __name__ == '__main__':
    app.run(debug=True)
