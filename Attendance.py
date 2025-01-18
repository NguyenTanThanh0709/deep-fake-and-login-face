import cv2
import face_recognition
import os
import numpy as np
import pandas as pd
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import ttk
from PIL import ImageTk, Image
import beepy
import mediapipe as mp
import threading
import tensorflow as tf

physical_devices = tf.config.experimental.list_physical_devices('GPU')
if len(physical_devices) > 0:
    tf.config.experimental.set_memory_growth(physical_devices[0], True)
    
frame_counter = 0
detection_frequency = 50

# Create a MediaPipe Face Detection object
mp_face_detection = mp.solutions.face_detection
mp_drawing = mp.solutions.drawing_utils
face_detection = mp_face_detection.FaceDetection(min_detection_confidence=0.5)

# Create GUI window
root = tk.Tk()
root.title("Attendance Checker")

def empty_csv():
    with open(Path(__file__).with_name('Attendance.csv'), mode='w') as file:
        file.write('Name,Class,Time,Date\n')

# Menu bar with a file menu
menubar = tk.Menu(root)
filemenu = tk.Menu(menubar, tearoff=0)
filemenu.add_command(label="Empty CSV", command=empty_csv)
filemenu.add_separator()
filemenu.add_command(label="Exit", command=root.quit)
menubar.add_cascade(label="File", menu=filemenu)
root.config(menu=menubar)

# Load and preprocess images
path = Path(__file__).resolve().parent / 'static/images'
images = []
classNames = []
mylist = os.listdir(path)
for cl in mylist:
    curImg = cv2.imread(f'{path}/{cl}')
    images.append(curImg)
    classNames.append(os.path.splitext(cl)[0])

def findEncodings(images):
    encodeList = []

    for img in images:
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Perform face detection only at the specified frequency
        if frame_counter % detection_frequency == 0:
            results = face_detection.process(imgRGB)
            if results.detections:
                for detection in results.detections:
                    bboxC = detection.location_data.relative_bounding_box
                    ih, iw, _ = img.shape
                    bbox = int(bboxC.xmin * iw), int(bboxC.ymin * ih), \
                            int(bboxC.width * iw), int(bboxC.height * ih)
                    x1, y1, width, height = bbox
                    x2, y2 = x1 + width, y1 + height
                    encoded_face = face_recognition.face_encodings(imgRGB, [(y1, x2, y2, x1)])[0]
                    encodeList.append(encoded_face)

    return encodeList

encoded_face_train = findEncodings(images)

# Load CSV content
df = pd.read_csv(Path(__file__).with_name('Attendance.csv'))

def markAttendance(name, class_):
    current_time = datetime.now().strftime('%H:%M:%S')
    current_date = datetime.now().strftime('%Y-%m-%d')

    # Extract the unique identifier from the recognized name
    unique_identifier = name  # You may need to modify this to extract the identifier correctly

    print(f"Marking attendance for: {unique_identifier}, {class_}, {current_time}, {current_date}")

    try:
        # Get the script's directory and construct the file path
        script_dir = os.path.dirname(os.path.abspath(__file__))
        csv_file_path = os.path.join(script_dir, 'Attendance.csv')

        with open(csv_file_path, mode='a') as file:
            file.write(f'{unique_identifier},{class_},{current_time},{current_date}\n')
    except Exception as e:
        print(f"Error writing to CSV: {e}")


    # Update the treeview in the main thread
    root.after(0, lambda: tree.insert('', 'end', values=[unique_identifier, class_, current_time, current_date]))
    beepy.beep(sound=2)

# Create canvas widget to display video capture
canvas = tk.Canvas(root, width=640, height=480)
canvas.pack()

# Create text widget to display attendance name
attendance_label = tk.Label(root, text="Attendance Checking...", font=("Helvetica", 20))
attendance_label.pack(pady=10)

# Create treeview to display attendance records
tree = ttk.Treeview(root)
tree["columns"] = ("Name", "Class", "Time", "Date")
tree.column("#0", width=50)
tree.column("Name", width=100)
tree.column("Class", width=100)
tree.column("Time", width=100)
tree.column("Date", width=100)
tree.heading("#0", text="Index")
tree.heading("Name", text="Name")
tree.heading("Class", text="Class")
tree.heading("Time", text="Time")
tree.heading("Date", text="Date")
tree.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

# Create video capture object
cap = cv2.VideoCapture(0)

def recognition_thread():
    global frame_counter  # Use the global frame_counter variable
    while True:
        success, img = cap.read()
        if success:
            frame_counter += 1  # Increment the frame counter

            # Convert the image to RGB format
            imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

            # Detect faces using MediaPipe Face Detection
            results = face_detection.process(imgRGB)

            if results.detections:
                for detection in results.detections:
                    bboxC = detection.location_data.relative_bounding_box
                    ih, iw, _ = img.shape
                    bbox = int(bboxC.xmin * iw), int(bboxC.ymin * ih), \
                            int(bboxC.width * iw), int(bboxC.height * ih)
                    x1, y1, width, height = bbox
                    x2, y2 = x1 + width, y1 + height

                    # Implement your face recognition logic here using MediaPipe's face recognition capabilities
                    encoded_face = face_recognition.face_encodings(imgRGB, [(y1, x2, y2, x1)])[0]

                    # Implement the matching and attendance marking logic
                    matches = face_recognition.compare_faces(encoded_face_train, encoded_face)
                    face_distances = face_recognition.face_distance(encoded_face_train, encoded_face)
                    match_index = np.argmin(face_distances)

                    if 0 <= match_index < len(classNames):
                        name_class = classNames[match_index]
                        if "_" in name_class:
                            class_ = name_class.split('_')[1]
                            name = name_class.split('_')[0]
                        else:
                            class_ = "Unknown"  # Assign a default class value if delimiter is missing
                            name = name_class

                        # Draw rectangle around the face
                        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                        cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)

                        # Add name label
                        cv2.putText(img, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)

                        # Mark attendance
                        markAttendance(name, class_)
                    else:
                        # Handle the case when match_index is out of range, e.g., show an "Unknown" label
                        name_class = "Unknown"

            # Convert the image to PIL format
            cv2image = cv2.cvtColor(img, cv2.COLOR_BGR2RGBA)
            img = Image.fromarray(cv2image)

            # Create the ImageTk object
            imgtk = ImageTk.PhotoImage(image=img)

            # Display the image on the GUI canvas
            canvas.create_image(0, 0, anchor=tk.NW, image=imgtk)

            # Update the GUI window
            root.update()

# Start the face recognition thread
recognition_thread = threading.Thread(target=recognition_thread)
recognition_thread.start()

# Main event loop for the GUI
root.mainloop()
