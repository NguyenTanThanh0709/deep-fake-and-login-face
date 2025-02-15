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
from models.Company import Company
from tensorflow.keras.models import load_model


# 📌 Tải mô hình Deepfake Detection (h5)
modeldeepfake = load_model('deepfake_detection_model.h5')

# 📌 Tải dữ liệu nhận diện khuôn mặt từ file pkl
def load_face_model(model_file='model.pkl'):
    try:
        with open(model_file, 'rb') as f:
            model_data = pickle.load(f)
        print("✅ Dữ liệu khuôn mặt đã tải thành công!")
        return model_data['encoded_faces'], model_data['class_names']
    except Exception as e:
        print(f"❌ Lỗi khi tải dữ liệu khuôn mặt: {e}")
        return None, None

# Lấy dữ liệu khuôn mặt
encoded_face_train, classNames = load_face_model()


# Hàm trích xuất khung hình từ video
def extract_frames(video_path):
    print(video_path)
    cap = cv2.VideoCapture(video_path)
    frames = []
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        # Thay đổi kích thước khung hình về kích thước mà mô hình yêu cầu (ví dụ: 299x299)
        frame = cv2.resize(frame, (299, 299))  # Thay đổi kích thước cho phù hợp với mô hình
        frames.append(frame)
    
    cap.release()
    return frames

# Hàm chuẩn hóa các khung hình (chuyển từ [0, 255] về [0, 1])
def preprocess_frames(frames):
    frames = np.array(frames, dtype='float32') / 255.0  # Chuẩn hóa
    return frames

# Hàm dự đoán xem video có chứa deepfake hay không
def predict_deepfake(video_path):
    video_path = video_path.lstrip('/')
    frames = extract_frames(video_path)
    
    if not frames:
        print("Không tìm thấy khung hình nào trong video!")
        return
    
    preprocessed_frames = preprocess_frames(frames)

    # Dự đoán cho các khung hình
    predictions = modeldeepfake.predict(preprocessed_frames)

    # Xử lý kết quả: dự đoán các khung hình có phải deepfake hay không (0 hoặc 1)
    predicted_classes = (predictions > 0.5).astype("int32")
    
    # Đếm số lượng khung hình deepfake
    deepfake_score = np.mean(predictions)  # Trung bình các giá trị xác suất
    deepfake_count = np.sum(predicted_classes)
    total_frames = len(predicted_classes)
    print(f"Deepfake Score: {deepfake_score:.2f}")  # Hiển thị điểm số với 2 chữ số thập phân


    print(f"Tổng số khung hình: {total_frames}")
    print(f"Số khung hình deepfake: {deepfake_count}")

    # Kết luận kết hợp
    if deepfake_score > 0.7 or deepfake_count > total_frames / 2:
        print("Video này có khả năng cao là deepfake.")
        return True, deepfake_score
    elif deepfake_score < 0.3 and deepfake_count < total_frames / 2:
        print("Video này có khả năng cao là thật.")
        return False, deepfake_score
    else:
        print("Không chắc chắn về độ thật/giả của video này.")
        return None, deepfake_score

# Flask App
app = Flask(__name__)
CORS(app)  # Allow cross-origin requests, if you're calling the API from a different domain

# Set the upload folder
UPLOAD_FOLDER = './static/images'  # Change this path based on your project structure
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['SECRET_KEY'] = 'your-unique-secret-key'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['UPLOAD_FOLDER_data'] = './static/images/data'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # Limit file size to 50MB


# Hàm kết nối đến cơ sở dữ liệu
def connect_db(user, password, db, host, port):
    return pymysql.connect(user=user,
                           password=password,
                           database=db,
                           host=host,
                           port=port,  # Thêm tham số port
                           cursorclass=pymysql.cursors.DictCursor)


@app.route('/api/login', methods=['POST'])
def login_api():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "Email và mật khẩu là bắt buộc"}), 400
    conn1 = connect_db('pass', 'pass', 'AttendanceSystem', 'localhost', 3306)
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
        query = "SELECT * FROM AttendanceLogs WHERE sdtNhanVien = %s ORDER BY timeStart DESC"
        cursor.execute(query, (maNhanVien,))
        results = cursor.fetchall()  # Fetch all records, even if there's only one
        if results:
            return [AttendanceLog.from_dict(result) for result in results]  # Return as a list
        else:
            return []
        


@app.route('/main/<string:user_id>', methods=['GET'])
def login(user_id):
    conn1 = connect_db('pass', 'pass', 'AttendanceSystem', 'localhost', 3306)
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
    conn1 = connect_db('pass', 'pass', 'AttendanceSystem', 'localhost', 3306)
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

@app.route('/starttest')  
def starttest():
    return render_template('starttest.html')  # Tạo một trang web đơn giản để tải ảnh lên  

# Lấy thông tin nhân viên từ cơ sở dữ liệu
def get_compay_by_sdt(conn, maNhanVien):
    with conn.cursor() as cursor:
        query = "SELECT * from company WHERE sdtAdmin = %s"
        cursor.execute(query, (maNhanVien,))
        result = cursor.fetchone()
        if result:
            return Company.from_dict(result)
        else:
            return None

@app.route('/companypage')  
def companypage():
    sdt = request.args.get('sdt')
    conn1 = connect_db('pass', 'pass', 'AttendanceSystem', 'localhost', 3306)
    department = get_compay_by_sdt(conn1,sdt)
    return render_template('company.html', company=department)



@app.route('/end')  
def end():
    return render_template('end.html')  # Tạo một trang web đơn giản để tải ảnh lên  

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
    conn1 = connect_db('pass', 'pass', 'AttendanceSystem', 'localhost', 3306)
    employees = get_nv_by_id(conn1)
    return render_template('listnv.html', employees=employees)  # Tạo một trang web đơn giản để tải ảnh lên

@app.route('/formnv/<int:user_id>', methods=['GET', 'POST'])
def formnv(user_id):
    conn1 = connect_db('pass', 'pass', 'AttendanceSystem', 'localhost', 3306)
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
                tenfile =email.split("@")[0] + "_" + sdt + ".jpg"
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{tenfile}.jpg")
                photo_reference = "/static/images/data" + '/' + tenfile
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
        
        # Handle photo upload
        photo_reference = None
        if 'photo_reference' in request.files:
            photo_file = request.files['photo_reference']
            if photo_file:
                tenfile =email.split("@")[0] + "_" + sdt + ".jpg"
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{tenfile}.jpg")
                photo_reference = "/static/images/data" + '/' + tenfile
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
    conn1 = connect_db('pass', 'pass', 'AttendanceSystem', 'localhost', 3306)
    attendances = get_attendance_by_id(conn1, user_id)
    return render_template('listlogattendace.html', attendances = attendances)  # Tạo một trang web đơn giản để tải ảnh lên

def get_log_deepfake_by_id(conn, maNhanVien):
    with conn.cursor() as cursor:
        query = "SELECT * from attendancelogs WHERE sdtNhanVien = %s ORDER BY timeStart DESC"
        cursor.execute(query, (maNhanVien,))
        results = cursor.fetchall()  # Fetch all records, even if there's only one
        if results:
            return [AttendanceLog.from_dict(result) for result in results]  # Return as a list
        else:
            return []

@app.route('/listlogdeepfake/<int:attendance_id>', methods=['GET'])
def listlogdeepfake(attendance_id):
    conn1 = connect_db('pass', 'pass', 'AttendanceSystem', 'localhost', 3306)
    log_deepfake = get_log_deepfake_by_id(conn1, attendance_id)
    print(log_deepfake)
    return render_template('listlogdeepfake.html', logDeepfake = log_deepfake)  # Tạo một trang web đơn giản để tải ảnh lên

@app.route('/api/changeStatus/<int:maNhanVien>', methods=['POST'])
def change_status(maNhanVien):
    conn1 = connect_db('pass', 'pass', 'AttendanceSystem', 'localhost', 3306)
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

@app.route('/save-media-start', methods=['POST'])
def save_media():
    try:
        file = request.files.get('file')
        file_type = request.form.get('fileType')
        sdt = request.form.get('sdt')

        # Generate a unique filename based on the timestamp
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
        file_name = f"{sdt}_{timestamp}"

        if file_type == 'image' and file:
            # For image
            image_path = os.path.join(app.config['UPLOAD_FOLDER_data'], f"{file_name}.jpg")
            file.save(image_path)
            file_path = f"/static/images/data/{file_name}.jpg"
            return jsonify({"message": "Image saved successfully", "file_path": file_path}), 200
        
        elif file_type == 'video' and file:
            video_path = os.path.join(app.config['UPLOAD_FOLDER_data'], f"{file_name}.mp4")
            file.save(video_path)
            file_path = f"/static/images/data/{file_name}.mp4"
            return jsonify({"message": "Video saved successfully", "file_path": file_path}), 200
        
        return jsonify({"error": "Invalid file type"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def handle_start_again(Sdt, statusStart, isDeepfakeDetectedStart, deepfakeScoreStart, photoCapturedStart):
    # Kết nối đến cơ sở dữ liệu
    conn1 = connect_db('pass', 'pass', 'AttendanceSystem', 'localhost', 3306)
    try:
            with conn1.cursor() as cursor:
                # Truy vấn kiểm tra bản ghi đã tồn tại
                sql_check = """
                    SELECT `logId` 
                    FROM `AttendanceLogs`
                    WHERE `sdtNhanVien` = %s AND DATE(`timeStart`) = DATE(CURRENT_TIMESTAMP())
                """
                cursor.execute(sql_check, (Sdt))
                result = cursor.fetchone()
                print(result)

                if result:  # Nếu bản ghi tồn tại, cập nhật
                    logId = result['logId']
                    sql_update = """
                        UPDATE `AttendanceLogs`
                        SET 
                            `timeStart` = CURRENT_TIMESTAMP,
                            `statusStart` = %s,
                            `isDeepfakeDetectedStart` = %s,
                            `deepfakeScoreStart` = %s,
                            `photoCapturedStart` = %s
                        WHERE `logId` = %s
                    """
                    cursor.execute(sql_update, (statusStart, isDeepfakeDetectedStart, deepfakeScoreStart, photoCapturedStart, logId))
                    print(f"Bản ghi logId = {logId} đã được cập nhật.")
                    conn1.commit()
                    conn1.close()
                    beepy.beep(sound=2)
                else:
                    handle_start(Sdt, statusStart, isDeepfakeDetectedStart, deepfakeScoreStart, photoCapturedStart)
    except Exception as e:
            print(f"Đã xảy ra lỗi: {e}")

def save_media(file, file_type, email,sdt):
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
    file_name = f"{email}_{sdt}_{timestamp}"
    if file_type == 'image' and file:
        image_path = os.path.join(app.config['UPLOAD_FOLDER_data'], f"{file_name}.jpg")
        file.save(image_path)
        return '/static/images/data/' + file_name + '.jpg'

def handle_start(Sdt, statusStart, isDeepfakeDetectedStart, deepfakeScoreStart, photoCapturedStart):
    try:
        conn1 = connect_db('pass', 'pass', 'AttendanceSystem', 'localhost', 3306)
        with conn1.cursor() as cursor:
            # Câu lệnh INSERT
            sql = """
                INSERT INTO `AttendanceLogs` (
                    `sdtNhanVien`, 
                    `timeStart`, 
                    `statusStart`, 
                    `isDeepfakeDetectedStart`, 
                    `deepfakeScoreStart`, 
                    `photoCapturedStart`
                ) VALUES (%s, CURRENT_TIMESTAMP, %s, %s, %s, %s)
            """
            # Thực thi câu lệnh
            cursor.execute(sql, (Sdt, statusStart, isDeepfakeDetectedStart, deepfakeScoreStart, photoCapturedStart))
            # Lưu thay đổi vào cơ sở dữ liệu
            conn1.commit()
            print("Dữ liệu đã được chèn thành công vào bảng AttendanceLogs.")
    except Exception as e:
        print(f"Đã xảy ra lỗi: {e}")
    finally:
        # Đóng kết nối
        beepy.beep(sound=2)
        conn1.close()

def handle_start_deepfake(Sdt, statusStart, isDeepfakeDetectedStart, deepfakeScoreStart, photoCapturedStart):
    try:
        conn1 = connect_db('pass', 'pass', 'AttendanceSystem', 'localhost', 3306)
        with conn1.cursor() as cursor:
            # Câu lệnh INSERT
            sql = """
                INSERT INTO `AttendanceLogs` (
                    `sdtNhanVien`, 
                    `timeStart`, 
                    `StatusDeepFakeStart`, 
                    `isDeepfakeDetectedStart`, 
                    `deepfakeScoreStart`, 
                    `LinkVideoDeepFakeStart`
                ) VALUES (%s, CURRENT_TIMESTAMP, %s, %s, %s, %s)
            """
            # Thực thi câu lệnh
            cursor.execute(sql, (Sdt, statusStart, isDeepfakeDetectedStart, deepfakeScoreStart, photoCapturedStart))
            # Lưu thay đổi vào cơ sở dữ liệu
            conn1.commit()
            print("Dữ liệu đã được chèn thành công vào bảng AttendanceLogs.")
    except Exception as e:
        print(f"Đã xảy ra lỗi: {e}")
    finally:
        # Đóng kết nối
        beepy.beep(sound=2)
        conn1.close()

def handle_start_again_attendance_deepfake(Sdt, statusStart, isDeepfakeDetectedStart, deepfakeScoreStart, file_path):
    # Kết nối đến cơ sở dữ liệu
    conn1 = connect_db('pass', 'pass', 'AttendanceSystem', 'localhost', 3306)
    try:
            with conn1.cursor() as cursor:
                # Truy vấn kiểm tra bản ghi đã tồn tại
                sql_check = """
                    SELECT `logId` 
                    FROM `AttendanceLogs`
                    WHERE `sdtNhanVien` = %s AND DATE(`timeStart`) = DATE(CURRENT_TIMESTAMP())
                """
                cursor.execute(sql_check, (Sdt))
                result = cursor.fetchone()
                print(result)

                if result:  # Nếu bản ghi tồn tại, cập nhật
                    logId = result['logId']
                    sql_update = """
                        UPDATE `AttendanceLogs`
                        SET 
                            `StatusDeepFakeStart` = %s,
                            `isDeepfakeDetectedStart` = %s,
                            `deepfakeScoreStart` = %s,
                            `LinkVideoDeepFakeStart` = %s
                        WHERE `logId` = %s
                    """
                    cursor.execute(sql_update, (statusStart, isDeepfakeDetectedStart, deepfakeScoreStart,file_path, logId))
                    print(f"Bản ghi logId = {logId} đã được cập nhật.")
                    conn1.commit()
                    conn1.close()
                    beepy.beep(sound=2)
                else:
                    handle_start_deepfake(Sdt, statusStart, isDeepfakeDetectedStart, deepfakeScoreStart, file_path)
    except Exception as e:
            print(f"Đã xảy ra lỗi: {e}")

def handle_End_again_attendance_deepfake(Sdt, statusEnd, isDeepfakeDetectedEnd, deepfakeScoreEnd, file_path):
    # Kết nối đến cơ sở dữ liệu
    conn1 = connect_db('pass', 'pass', 'AttendanceSystem', 'localhost', 3306)
    try:
            with conn1.cursor() as cursor:
                # Truy vấn kiểm tra bản ghi đã tồn tại
                sql_check = """
                    SELECT `logId` 
                    FROM `AttendanceLogs`
                    WHERE `sdtNhanVien` = %s AND DATE(`timeStart`) = DATE(CURRENT_TIMESTAMP())
                """
                cursor.execute(sql_check, (Sdt))
                result = cursor.fetchone()
                print(result)

                if result:  # Nếu bản ghi tồn tại, cập nhật
                    logId = result['logId']
                    sql_update = """
                        UPDATE `AttendanceLogs`
                        SET 
                            `StatusDeepFakeEnd` = %s,
                            `isDeepfakeDetectedEnd` = %s,
                            `deepfakeScoreEnd` = %s,
                            `LinkVideoDeepFakeEnd` = %s
                        WHERE `logId` = %s
                    """
                    cursor.execute(sql_update, (statusEnd, isDeepfakeDetectedEnd, deepfakeScoreEnd,file_path, logId))
                    print(f"Bản ghi logId = {logId} đã được cập nhật.")
                    conn1.commit()
                    conn1.close()
                    beepy.beep(sound=2)
                else:
                    raise Exception("Bản ghi không tồn tại")
    except Exception as e:
            print(f"Đã xảy ra lỗi: {e}")

@app.route('/attendance/start', methods=['POST'])
def insert_start_api():
    file = request.files.get('image')
    filePath = request.form.get('filePath')
    fileType = request.form.get('fileType')
    sdt = request.form.get('sdt')
    
    if fileType == 'image':
            
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
                    sdt_check = name_class.split('_')[1]
                    email_check = name_class.split('_')[0]
                else:
                    sdt_check = "Unknown"  
                    email_check = name_class
                
                check = ""
                if sdt == sdt_check:
                    check = "SUCCESS"
                else:
                    check = "FAILED"
                    
                handle_start_again(sdt, check, 0, 0.0, filePath)

                response_data = {
                    'status': 'OK',
                    'message': check
                }
                return jsonify(response_data)
        
        response_data = {
            'status': 'NOT'
        }
        return  jsonify(response_data)
    else:
        checkDeepFake, ScoreDeepFake = predict_deepfake(filePath)
        if checkDeepFake == True:
            handle_start_again_attendance_deepfake(sdt,"FAILED", 1, ScoreDeepFake, filePath)
            response_data = {
            'status': 'FAILED'
            }
            return jsonify(response_data)
        elif checkDeepFake == False:
            handle_start_again_attendance_deepfake(sdt,"SUCCESS", 0, ScoreDeepFake, filePath)
            response_data = {
            'status': 'SUCCESS'
            }
            return jsonify(response_data)            
        else:
            handle_start_again_attendance_deepfake(sdt,"NOT DEEPFAKE", 0, ScoreDeepFake, filePath)
            response_data = {
            'status': 'NOT'
            }
            return jsonify(response_data)              

def handle_end(Sdt, statusEnd, isDeepfakeDetectedEnd, deepfakeScoreEnd, photoCapturedEnd):
    conn1 = connect_db('pass', 'pass', 'AttendanceSystem', 'localhost', 3306)
    try:
            with conn1.cursor() as cursor:
                # Truy vấn kiểm tra bản ghi đã tồn tại
                sql_check = """
                    SELECT `logId` 
                    FROM `AttendanceLogs`
                    WHERE `sdtNhanVien` = %s AND DATE(`timeStart`) = DATE(CURRENT_TIMESTAMP())
                """
                cursor.execute(sql_check, (Sdt))
                result = cursor.fetchone()

                if result:  # Nếu bản ghi tồn tại, cập nhật
                    logId = result['logId']
                    sql_update = """
                        UPDATE `AttendanceLogs`
                        SET 
                            `timeEnd` = CURRENT_TIMESTAMP,
                            `statusEnd` = %s,
                            `isDeepfakeDetectedEnd` = %s,
                            `deepfakeScoreEnd` = %s,
                            `photoCapturedEnd` = %s
                        WHERE `logId` = %s
                    """
                    cursor.execute(sql_update, (statusEnd, isDeepfakeDetectedEnd, deepfakeScoreEnd, photoCapturedEnd, logId))
                    print(f"Bản ghi logId = {logId} đã được cập nhật.")
                else:  # Nếu không, chèn mới
                    raise Exception("Bản ghi không tồn tại")
                # Lưu thay đổi
                conn1.commit()
    except Exception as e:
            print(f"Đã xảy ra lỗi: {e}")
    finally:
            # Đóng kết nối
            conn1.close()

@app.route('/attendance/end', methods=['POST'])
def insert_end_api():
    file = request.files.get('image')
    filePath = request.form.get('filePath')
    sdt = request.form.get('sdt')
    fileType = request.form.get('fileType')

    if fileType == 'image':
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
                    sdt_check = name_class.split('_')[1]
                    email_check = name_class.split('_')[0]
                else:
                    sdt_check = "Unknown"  
                    email_check = name_class
                
                check = ""
                if sdt == sdt_check:
                    check = "SUCCESS"
                else:
                    check = "FAILED"
                    
                handle_end(sdt, check, 0, 0.0, filePath)
                response_data = {
                    'status': 'OK',
                    'message': check
                }
                return jsonify(response_data)
    else:
        checkDeepFake, ScoreDeepFake = predict_deepfake(filePath)
        if checkDeepFake == True:
            handle_End_again_attendance_deepfake(sdt,"FAILED", 1, ScoreDeepFake,filePath)
            response_data = {
            'status': 'FAILED'
            }
            return jsonify(response_data)
        elif checkDeepFake == False:
            handle_End_again_attendance_deepfake(sdt,"SUCCESS", 0, ScoreDeepFake,filePath)
            response_data = {
            'status': 'SUCCESS'
            }
            return jsonify(response_data)            
        else:
            handle_End_again_attendance_deepfake(sdt,"NOT DEEPFAKE", 0, ScoreDeepFake,filePath)
            response_data = {
            'status': 'NOT DEEPFAKE'
            }
            return jsonify(response_data)  
        
    response_data = {
        'status': 'NOT'
    }
    return  jsonify(response_data)


@app.route('/check_location/start', methods=['GET'])
def check_location():
    company_id = request.args.get('id', type=int)
    lat = request.args.get('lat', type=float)
    lon = request.args.get('lon', type=float)
    sdt = request.args.get('sdt', type=float)
    company_id = 1


    if company_id is None or lat is None or lon is None:
        return jsonify({"error": "Missing parameters"}), 400

    conn = connect_db('pass', 'pass', 'AttendanceSystem', 'localhost', 3306)
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT latitude, longitude FROM company WHERE id = %s", (company_id,))
    company = cursor.fetchone()

    cursor.close()
    conn.close()

    if not company:
        return jsonify({"error": "Company not found"}), 404

    company_lat = company['latitude']
    company_lon = company['longitude']
    conn1 = connect_db('pass', 'pass', 'AttendanceSystem', 'localhost', 3306)
    # So sánh tọa độ (có thể thêm khoảng cách sai số nếu cần)
    if compare_lat_lon(lat, lon, company_lat, company_lon):
        updateStatusStart(conn1, "SUCCESS", sdt,lat,lon)
        return jsonify({"match": True})
    else:
        updateStatusStart(conn1, "FAILED", sdt,lat,lon)
        return jsonify({"match": False})

def compare_lat_lon(lat1, lon1, lat2, lon2):
    return round(lat1, 1) == round(lat2, 1) and round(lon1, 1) == round(lon2, 1)


@app.route('/check_location/end', methods=['GET'])
def check_locationend():
    company_id = request.args.get('id', type=int)
    lat = request.args.get('lat', type=float)
    lon = request.args.get('lon', type=float)
    sdt = request.args.get('sdt', type=float)
    company_id = 1


    if company_id is None or lat is None or lon is None:
        return jsonify({"error": "Missing parameters"}), 400

    conn = connect_db('pass', 'pass', 'AttendanceSystem', 'localhost', 3306)
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT latitude, longitude FROM company WHERE id = %s", (company_id,))
    company = cursor.fetchone()

    cursor.close()
    conn.close()

    if not company:
        return jsonify({"error": "Company not found"}), 404

    company_lat = company['latitude']
    company_lon = company['longitude']
    conn1 = connect_db('pass', 'pass', 'AttendanceSystem', 'localhost', 3306)
    # So sánh tọa độ (có thể thêm khoảng cách sai số nếu cần)
    if compare_lat_lon(lat, lon, company_lat, company_lon):
        updateStatusEnd(conn1, "SUCCESS", sdt,lat,lon)
        return jsonify({"match": True})
    else:
        updateStatusEnd(conn1, "FAILED", sdt,lat,lon)
        return jsonify({"match": False})

def compare_lat_lon(lat1, lon1, lat2, lon2):
    return round(lat1, 1) == round(lat2, 1) and round(lon1, 1) == round(lon2, 1)

def updateStatusStart(conn1, status, Sdt,lat,lon):
    try:
            with conn1.cursor() as cursor:
                # Truy vấn kiểm tra bản ghi đã tồn tại
                sql_check = """
                    SELECT `logId` 
                    FROM `AttendanceLogs`
                    WHERE `sdtNhanVien` = %s AND DATE(`timeStart`) = DATE(CURRENT_TIMESTAMP())
                """
                cursor.execute(sql_check, (Sdt))
                result = cursor.fetchone()
                print(result)

                if result:  # Nếu bản ghi tồn tại, cập nhật
                    logId = result['logId']
                    sql_update = """
                        UPDATE `AttendanceLogs`
                        SET 
                            `statusStart` = %s,
                            `latStart` = %s,
                            `lonStart` = %s
                        WHERE `logId` = %s
                    """
                    cursor.execute(sql_update, (status,lat,lon, logId))
                    print(f"Bản ghi logId = {logId} đã được cập nhật.")
                    conn1.commit()
                    conn1.close()
                    beepy.beep(sound=2)
    except Exception as e:
            print(f"Đã xảy ra lỗi: {e}")    

def updateStatusEnd(conn1, status, Sdt,lat,lon):
    try:
            with conn1.cursor() as cursor:
                # Truy vấn kiểm tra bản ghi đã tồn tại
                sql_check = """
                    SELECT `logId` 
                    FROM `AttendanceLogs`
                    WHERE `sdtNhanVien` = %s AND DATE(`timeStart`) = DATE(CURRENT_TIMESTAMP())
                """
                cursor.execute(sql_check, (Sdt))
                result = cursor.fetchone()
                print(result)

                if result:  # Nếu bản ghi tồn tại, cập nhật
                    logId = result['logId']
                    sql_update = """
                        UPDATE `AttendanceLogs`
                        SET 
                            `statusEnd` = %s,
                            `latEnd` = %s,
                            `lonEnd` = %s
                        WHERE `logId` = %s
                    """
                    cursor.execute(sql_update, (status,lat,lon, logId))
                    print(f"Bản ghi logId = {logId} đã được cập nhật.")
                    conn1.commit()
                    conn1.close()
                    beepy.beep(sound=2)
    except Exception as e:
            print(f"Đã xảy ra lỗi: {e}")  

if __name__ == '__main__':
    app.run(debug=True)
