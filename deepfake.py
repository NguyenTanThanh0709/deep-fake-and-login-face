import cv2
import numpy as np
from tensorflow.keras.models import load_model
import os

# Tải mô hình đã huấn luyện
model = load_model('deepfake_detection_model.h5')

# Hàm trích xuất khung hình từ video
def extract_frames(video_path):
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
    frames = extract_frames(video_path)
    
    if not frames:
        print("Không tìm thấy khung hình nào trong video!")
        return
    
    preprocessed_frames = preprocess_frames(frames)

    # Dự đoán cho các khung hình
    predictions = model.predict(preprocessed_frames)

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
    elif deepfake_score < 0.3 and deepfake_count < total_frames / 2:
        print("Video này có khả năng cao là thật.")
    else:
        print("Không chắc chắn về độ thật/giả của video này.")


# Đường dẫn đến thư mục chứa video
video_folder = 'train_sample_videos/'  # Thay thế bằng đường dẫn đến thư mục video của bạn

# Duyệt qua tất cả các video trong thư mục
for filename in os.listdir(video_folder):
    if filename.endswith('.mp4'):
        video_path = os.path.join(video_folder, filename)
        print(f"Đang xử lý video: {video_path}")
        predict_deepfake(video_path)