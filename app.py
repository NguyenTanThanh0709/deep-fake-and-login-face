from flask import Flask, render_template, request, redirect, url_for, jsonify
from werkzeug.utils import secure_filename
from datetime import datetime
from flask_cors import CORS
import cv2
import numpy as np
from io import BytesIO
from PIL import Image
import mimetypes
import pickle
import os
import base64
import face_recognition
import beepy
from datetime import datetime

# Tải mô hình đã lưu
def load_model(model_file='model.pkl'):
    with open(model_file, 'rb') as f:
        model_data = pickle.load(f)
    return model_data['encoded_faces'], model_data['class_names']

# Lấy mô hình
encoded_face_train, classNames = load_model()

# Hàm đánh dấu điểm danh
def markAttendance(name, class_):
    current_time = datetime.now().strftime('%H:%M:%S')
    current_date = datetime.now().strftime('%Y-%m-%d')
    print(f"Marking attendance for: {name}, {class_}, {current_time}, {current_date}")
    # Bạn có thể thay đổi cách điểm danh theo ý muốn (ví dụ lưu vào cơ sở dữ liệu)
    with open('Attendance.csv', mode='a') as file:
        file.write(f'{name},{class_},{current_time},{current_date}\n')
    beepy.beep(sound=2)

# Flask App
app = Flask(__name__)
CORS(app)  # Allow cross-origin requests, if you're calling the API from a different domain

# Set the upload folder
UPLOAD_FOLDER = './PE'  # Change this path based on your project structure
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # Limit file size to 50MB

@app.route('/')
def index():
    return render_template('index.html')  # Tạo một trang web đơn giản để tải ảnh lên

@app.route('/login')
def login():
    return render_template('login.html')  # Tạo một trang web đơn giản để tải ảnh lên

@app.route('/listnv')
def listnv():
    return render_template('listnv.html')  # Tạo một trang web đơn giản để tải ảnh lên

@app.route('/formnv')
def formnv():
    return render_template('formnhanvien.html')  # Tạo một trang web đơn giản để tải ảnh lên

@app.route('/listlogattendace')
def listlogattendace():
    return render_template('listlogattendace.html')  # Tạo một trang web đơn giản để tải ảnh lên

@app.route('/listlogdeepfake')
def listlogdeepfake():
    return render_template('listlogdeepfake.html')  # Tạo một trang web đơn giản để tải ảnh lên

@app.route('/profile') 
def profile():
    return render_template('profile.html')  # Tạo một trang web đơn giản để tải ảnh lên 

@app.route('/start')  
def start():
    return render_template('start.html')  # Tạo một trang web đơn giản để tải ảnh lên  

@app.route('/end')  
def end():
    return render_template('end.html')  # Tạo một trang web đơn giản để tải ảnh lên  

@app.route('/save-media-start', methods=['POST'])
def save_media():
    try:
        file = request.files.get('file')
        file_type = request.form.get('fileType')

        # Generate a unique filename based on the timestamp
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
        file_name = f"ABC_{timestamp}"

        if file_type == 'image' and file:
            # For image
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{file_name}.jpg")
            file.save(image_path)
            return jsonify({"message": "Image saved successfully", "file_path": image_path}), 200
        
        
        elif file_type == 'video' and file:
            video_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{file_name}.mp4")
            file.save(video_path)
            return jsonify({"message": "Video saved successfully", "file_path": video_path}), 200

        return jsonify({"error": "Invalid file type"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/save-media-end', methods=['POST'])
def save_media_end():
    try:
        file = request.files.get('file')
        file_type = request.form.get('fileType')

        # Generate a unique filename based on the timestamp
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
        file_name = f"ABC_{timestamp}"

        if file_type == 'image' and file:
            # For image
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{file_name}.jpg")
            file.save(image_path)
            return jsonify({"message": "Image saved successfully", "file_path": image_path}), 200
        
        
        elif file_type == 'video' and file:
            video_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{file_name}.mp4")
            file.save(video_path)
            return jsonify({"message": "Video saved successfully", "file_path": video_path}), 200

        return jsonify({"error": "Invalid file type"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route('/attendance', methods=['POST'])
def attendance():
    if 'image' not in request.files:
        return redirect(request.url)
    file = request.files['image']
    if file.filename == '':
        return redirect(request.url)
    
    # Đọc ảnh từ người dùng
    img = np.array(bytearray(file.read()), dtype=np.uint8)
    img = cv2.imdecode(img, cv2.IMREAD_COLOR)
    
    # Chuyển ảnh sang định dạng RGB
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    # Phát hiện khuôn mặt trong ảnh
    face_locations = face_recognition.face_locations(imgRGB)
    face_encodings = face_recognition.face_encodings(imgRGB, face_locations)
    
    for encoded_face in face_encodings:
        matches = face_recognition.compare_faces(encoded_face_train, encoded_face)
        face_distances = face_recognition.face_distance(encoded_face_train, encoded_face)
        match_index = np.argmin(face_distances)
        
        if 0 <= match_index < len(classNames):
            name_class = classNames[match_index]
            if "_" in name_class:
                class_ = name_class.split('_')[1]
                name = name_class.split('_')[0]
            else:
                class_ = "Unknown"  
                name = name_class
            
            markAttendance(name, class_)
    
    return redirect(url_for('index'))  # Redirect về trang chính sau khi điểm danh

if __name__ == '__main__':
    app.run(debug=True)
