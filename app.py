from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)
app.secret_key = "my_super_secret_key"

# دالة للاتصال بقاعدة البيانات
def get_db():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# إنشاء الجداول إذا لم تكن موجودة
def init_db():
    with get_db() as db:
        db.execute('''CREATE TABLE IF NOT EXISTS users 
                   (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password TEXT, role TEXT)''')
        # إضافة مدير افتراضي إذا كانت القاعدة فارغة (اسم: admin ، كلمة سر: admin123)
        admin_exists = db.execute("SELECT * FROM users WHERE username='HEMO'").fetchone()
        if not admin_exists:
            hashed_pw = generate_password_hash('i123123i')
            db.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", ('admin', hashed_pw, 'super_admin'))
        db.commit()

init_db()

# حماية الصفحات (يجب أن يكون مسجلاً للدخول)
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# حماية صفحات الإدارة
def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('role') not in ['admin', 'super_admin']:
            return "غير مسموح لك بالدخول", 403
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        user = db.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            return redirect(url_for('admin_panel'))
        flash("بيانات الدخول خاطئة")
    return render_template('login.html')

@app.route('/admin')
@login_required
@admin_only
def admin_panel():
    db = get_db()
    all_users = db.execute("SELECT * FROM users").fetchall()
    # لنفترض أن الصور في قائمة تجريبية (يمكنك ربطها بملفاتك)
    return render_template('admin_panel.html', users=all_users)

@app.route('/add_admin', methods=['POST'])
@login_required
@admin_only
def add_admin():
    username = request.form['username']
    password = generate_password_hash(request.form['password'])
    db = get_db()
    try:
        db.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, password, 'admin'))
        db.commit()
        flash("تم إضافة الأدمن بنجاح")
    except:
        flash("اسم المستخدم موجود مسبقاً")
    return redirect(url_for('admin_panel'))

@app.route('/delete_user/<int:id>')
@login_required
@admin_only
def delete_user(id):
    db = get_db()
    db.execute("DELETE FROM users WHERE id=?", (id,))
    db.commit()
    return redirect(url_for('admin_panel'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)