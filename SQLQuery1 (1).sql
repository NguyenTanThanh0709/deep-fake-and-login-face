-- Departments table
CREATE TABLE Departments (
    department_id INT AUTO_INCREMENT PRIMARY KEY,
    department_name VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Employees table
CREATE TABLE Employees (
    maNhanVien INT AUTO_INCREMENT PRIMARY KEY,
    tenNhanVien VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    sdt VARCHAR(20) UNIQUE,  -- Increased size for phone number
    password VARCHAR(200) NOT NULL,
    vaiTro VARCHAR(50),
    photo_reference TEXT,
    role VARCHAR(50),  -- Role column
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    IsActive BIT DEFAULT 1,
    department_id INT, -- New foreign key column for Department
    FOREIGN KEY (department_id) REFERENCES Departments(department_id) -- FK to Departments
);

-- AttendanceLogs table
CREATE TABLE AttendanceLogs (
    logId BIGINT AUTO_INCREMENT PRIMARY KEY,
    maNhanVien INT NOT NULL,  -- Corrected column name to match Employees

    timeStart TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    statusStart ENUM('SUCCESS', 'FAILED', 'NOT') NOT NULL,
    isDeepfakeDetectedStart BOOLEAN DEFAULT FALSE,
    deepfakeScoreStart FLOAT,
    photoCapturedStart TEXT,

    timeEnd TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    statusEnd ENUM('SUCCESS', 'FAILED', 'NOT') NOT NULL,
    isDeepfakeDetectedEnd BOOLEAN DEFAULT FALSE,
    deepfakeScoreEnd FLOAT,
    photoCapturedEnd TEXT,
    
    FOREIGN KEY (maNhanVien) REFERENCES Employees(maNhanVien) ON DELETE CASCADE  -- Fixed foreign key reference
);

-- DeepfakeLogs table
CREATE TABLE DeepfakeLogs (
    deepfake_log_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    log_id BIGINT,
    detection_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deepfake_score FLOAT NOT NULL,
	Prediction NVARCHAR(10) NOT NULL,
    photo_analyzed TEXT,
    FOREIGN KEY (log_id) REFERENCES AttendanceLogs(logId)  -- FK reference from AttendanceLogs
);

INSERT INTO Departments (department_name) 
VALUES 
    ('Phòng Kế Toán'), 
    ('Phòng IT'), 
    ('Phòng Nhân Sự'), 
    ('Phòng Sale');


