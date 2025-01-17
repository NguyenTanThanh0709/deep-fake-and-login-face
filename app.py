from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from werkzeug.utils import secure_filename
from datetime import datetime
import pymysql
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
from models.Employee import Employee
from models.AttendanceLog import AttendanceLog
from models.Department import Department
from models.DeepfakeLog import DeepfakeLog

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
app.config['SECRET_KEY'] = 'your-unique-secret-key'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # Limit file size to 50MB


# Hàm kết nối đến cơ sở dữ liệu
def connect_db(user, password, db, host, port):
    return pymysql.connect(user=user,
                           password=password,
                           database=db,
                           host=host,
                           port=port,  # Thêm tham số port
                           cursorclass=pymysql.cursors.DictCursor)

conn1 = connect_db('root_t', 'pass', 'AttendanceSystem', 'localhost', 3306)

@app.route('/api/login', methods=['POST'])
def login_api():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "Email và mật khẩu là bắt buộc"}), 400

    try:
        with conn1.cursor() as cursor:
            # Kiểm tra email và mật khẩu trong bảng Employees
            sql = "SELECT * FROM Employees WHERE email = %s AND IsActive = 1"
            cursor.execute(sql, (email,))
            employee_data = cursor.fetchone()

            if employee_data and employee_data['password'] == password:
                # Chuyển đổi dữ liệu thành đối tượng Employee
                employee = Employee.from_dict(employee_data)

                # Trả về thông tin nhân viên
                return jsonify({
                    "message": "Đăng nhập thành công",
                    "employee": {
                        "maNhanVien": employee.maNhanVien,
                        "tenNhanVien": employee.tenNhanVien,
                        "sdt": employee.sdt,
                        "photo_reference":  employee.photo_reference,
                        "email": employee.email,
                        "vaiTro": employee.vaiTro,
                        "role": employee.role,
                        "department_id": employee.department_id,
                    }
                }), 200
            else:
                return jsonify({"error": "Email hoặc mật khẩu không chính xác"}), 401
    except Exception as e:
        return jsonify({"error": f"Lỗi server: {str(e)}"}), 500

@app.route('/')
def index():
    return render_template('login.html')  # Tạo một trang web đơn giản để tải ảnh lên

def get_attendance_by_id(conn, maNhanVien):
    with conn.cursor() as cursor:
        query = "SELECT * FROM AttendanceLogs WHERE maNhanVien = %s ORDER BY timeStart DESC"
        cursor.execute(query, (maNhanVien,))
        results = cursor.fetchall()  # Fetch all records, even if there's only one
        if results:
            return [AttendanceLog.from_dict(result) for result in results]  # Return as a list
        else:
            return []
        


@app.route('/main/<int:user_id>', methods=['GET'])
def login(user_id):
    attendance = get_attendance_by_id(conn1, user_id)
    return render_template('index.html', attendance=attendance)  # Tạo một trang web đơn giản để tải ảnh lên

# Lấy thông tin nhân viên từ cơ sở dữ liệu
def get_employee_by_id(conn, maNhanVien):
    with conn.cursor() as cursor:
        query = "SELECT * FROM Employees WHERE maNhanVien = %s"
        cursor.execute(query, (maNhanVien,))
        result = cursor.fetchone()
        if result:
            return Employee.from_dict(result)
        else:
            return None

def update_user_password(conn, user_id, hashed_password):
    with conn.cursor() as cursor:
        query = "UPDATE Employees SET password = %s WHERE maNhanVien = %s"
        cursor.execute(query, (hashed_password, user_id))
        conn.commit()

@app.route('/profile/<int:user_id>', methods=['GET', 'POST'])
def profile(user_id):
    user = get_employee_by_id(conn1, user_id)
    if user:
        if request.method == 'POST':
            current_password = request.form['currentPassword']
            new_password = request.form['newPassword']
            confirm_password = request.form['confirmPassword']
            if user.password != current_password:
                flash('Current password is incorrect', 'danger')
                return render_template('profile.html', user=user)
            if new_password != confirm_password:
                flash('New password and confirm password do not match', 'danger')
                return render_template('profile.html', user=user)
            
            update_user_password(conn1, user_id, new_password)
            flash('Password updated successfully', 'success')
            return redirect(url_for('profile', user_id=user_id))
        # Truyền dữ liệu người dùng tới template
        return render_template('profile.html', user=user)
    else:
        return "User not found", 404

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


def get_nv_by_id(conn):
    with conn.cursor() as cursor:
        query = "SELECT * FROM Employees"
        cursor.execute(query)
        results = cursor.fetchall()  # Fetch all records, even if there's only one
        if results:
            return [Employee.from_dict(result) for result in results]  # Return as a list
        else:
            return []

def get_department_by_id(conn):
    with conn.cursor() as cursor:
        query = "SELECT * from Departments"
        cursor.execute(query)
        results = cursor.fetchall()  # Fetch all records, even if there's only one
        if results:
            return [Department.from_dict(result) for result in results]  # Return as a list
        else:
            return []
           
@app.route('/listnv')
def listnv():
    employees = get_nv_by_id(conn1)
    return render_template('listnv.html', employees=employees)  # Tạo một trang web đơn giản để tải ảnh lên

@app.route('/formnv/<int:user_id>', methods=['GET', 'POST'])
def formnv(user_id):
    department = get_department_by_id(conn1)
    print(user_id)

    if request.method == 'GET' and user_id != 0:
        # Retrieve employee data based on user_id
        employee = get_employee_by_id(conn1, user_id)
        if employee:
            return render_template('formnhanvien.html', employee=employee, departments=department)
        else:
            return "Employee not found", 404
    
    if request.method == 'POST' and user_id != 0:
        tenNhanVien = request.form['tenNhanVien']
        email = request.form['email']
        sdt = request.form['sdt']
        password = request.form['password']
        vaiTro = request.form['vaiTro']
        role = request.form['role']
        isActive = 1 if request.form['isActive'] == '1' else 0
        department_id = request.form['department']
        print(request.form)
            # Handle photo upload (optional)
        photo_reference = None
        if 'photo_reference' in request.files:
            photo_file = request.files['photo_reference']
            if photo_file:
                tenfile =tenNhanVien + "_" + sdt + ".jpg"
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{tenfile}.jpg")
                photo_file.save(image_path)
        
        # Update employee data in the database
        cursor = conn1.cursor()
        sql = """
            UPDATE Employees
            SET tenNhanVien = %s, email = %s, sdt = %s, password = %s, vaiTro = %s, role = %s, IsActive = %s, department_id = %s, photo_reference = %s
            WHERE maNhanVien = %s
        """
        cursor.execute(sql, (tenNhanVien, email, sdt, password, vaiTro, role, isActive, department_id, photo_reference, user_id))
        conn1.commit()
        return redirect(url_for('listnv'))



    if request.method == 'POST' and user_id == 0:
        # Retrieve form data
        tenNhanVien = request.form['tenNhanVien']
        email = request.form['email']
        sdt = request.form['sdt']
        password = request.form['password']
        vaiTro = request.form['vaiTro']
        role = request.form['role']
        isActive = 1 if request.form['isActive'] == '1' else 0
        department_id = request.form['department']
        print(request.form)
        
        # Handle photo upload
        photo_reference = None
        if 'photo_reference' in request.files:
            photo_file = request.files['photo_reference']
            if photo_file:
                tenfile =tenNhanVien + "_" + sdt + ".jpg"
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{tenfile}.jpg")
                photo_file.save(image_path)
        
        # Insert into Employees table
        cursor = conn1.cursor()
        sql = """
            INSERT INTO Employees (tenNhanVien, email, sdt, password, vaiTro, role, IsActive, department_id, photo_reference)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(sql, (tenNhanVien, email, sdt, password, vaiTro, role, isActive, department_id, photo_reference))
        conn1.commit()
        return redirect(url_for('listnv'))
    
    
    
    return render_template('formnhanvien.html', departments =department)  # Tạo một trang web đơn giản để tải ảnh lên


@app.route('/listlogattendace/<int:user_id>', methods=['GET'])
def listlogattendace(user_id):
    attendances = get_attendance_by_id(conn1, user_id)
    return render_template('listlogattendace.html', attendances = attendances)  # Tạo một trang web đơn giản để tải ảnh lên

def get_log_deepfake_by_id(conn, maNhanVien):
    with conn.cursor() as cursor:
        query = "SELECT * from DeepfakeLogs WHERE log_id = %s ORDER BY detection_time DESC"
        cursor.execute(query, (maNhanVien,))
        results = cursor.fetchall()  # Fetch all records, even if there's only one
        if results:
            return [DeepfakeLog.from_dict(result) for result in results]  # Return as a list
        else:
            return []

@app.route('/listlogdeepfake/<int:attendance_id>', methods=['GET'])
def listlogdeepfake(attendance_id):
    log_deepfake = get_log_deepfake_by_id(conn1, attendance_id)
    print(log_deepfake)
    return render_template('listlogdeepfake.html', logDeepfake = log_deepfake)  # Tạo một trang web đơn giản để tải ảnh lên

@app.route('/api/changeStatus/<int:maNhanVien>', methods=['POST'])
def change_status(maNhanVien):
    try:
        with conn1.cursor() as cursor:
            # Cập nhật trạng thái IsActive
            update_query = """
                UPDATE Employees
                SET IsActive = NOT IsActive
                WHERE maNhanVien = %s
            """
            cursor.execute(update_query, (maNhanVien,))
            conn1.commit()

            return 1

    except Exception as e:
        print(f"Lỗi: {e}")
        return jsonify({'error': 'Đã xảy ra lỗi trong quá trình xử lý'}), 500

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
