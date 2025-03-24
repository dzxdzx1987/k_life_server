import os

from flask import render_template, request, url_for, redirect, flash
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename

from server import app

import cv2
from pyzbar.pyzbar import decode

image_path = os.path.join(os.path.dirname(app.root_path), 'sample/02.jpg')
# Define the upload folder and allowed extensions
UPLOAD_FOLDER = os.path.join(app.root_path, 'static/uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part.')
            return redirect(request.url)

        file = request.files['file']

        # If the user does not select a file
        if file.filename == '':
            flash('No selected file.')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            flash('File successfully uploaded.')
            return redirect(url_for('index'))

    return render_template('upload.html')

@app.route('/api/readBarCode', methods=['GET', 'POST'])
def read_barcode():
    # 加载图像
    image = cv2.imread(image_path)

    # 使用pyzbar检测和解码条形码
    barcodes = decode(image)
    
    results = []
    result = ''
    for barcode in barcodes:
        barcode_data = barcode.data.decode('utf-8')
        barcode_type = barcode.type
        results.append((barcode_data, barcode_type))
        if barcode_type == 'CODE128':
            result = barcode_data
            break

    if result:
        print("识别成功:", results)
        return result
    else:
        print("未检测到条形码")
        return None
