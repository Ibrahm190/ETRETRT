import os
from flask import Flask, render_template, request, redirect, url_for, send_from_directory

app = Flask(__name__)

# إعدادات المجلد
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# التأكد من وجود المجلدات المطلوبة
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/')
def index():
    # عرض الصور للزوار
    images = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template('index.html', images=images)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    # رفع الصور في حالة الـ POST
    if request.method == 'POST':
        if 'photo' in request.files:
            file = request.files['photo']
            if file.filename != '':
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
                return redirect(url_for('admin'))
    
    # عرض الصور مع أزرار الحذف للأدمن
    images = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template('admin.html', images=images)

@app.route('/delete/<filename>', methods=['POST'])
def delete_image(filename):
    # ميزة الحذف
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(file_path):
        os.remove(file_path)
    return redirect(url_for('admin'))

@app.route('/uploads/<filename>')
def display_image(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    # التشغيل على الشبكة المحلية
    app.run(host='0.0.0.0', port=5000, debug=True)