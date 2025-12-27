-- CampusHub Database Schema

CREATE DATABASE IF NOT EXISTS campushub;
USE campushub;

-- Users Table
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('student', 'teacher', 'admin') NOT NULL DEFAULT 'student',
    security_question VARCHAR(255),
    security_answer_hash VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    INDEX idx_email (email),
    INDEX idx_username (username)
);

-- Courses Table
CREATE TABLE courses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    course_code VARCHAR(20) UNIQUE NOT NULL,
    course_name VARCHAR(100) NOT NULL,
    description TEXT,
    credits INT NOT NULL,
    teacher_id INT,
    semester VARCHAR(20),
    max_students INT DEFAULT 50,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (teacher_id) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_course_code (course_code)
);

-- Enrollments Table
CREATE TABLE enrollments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    course_id INT NOT NULL,
    enrollment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status ENUM('enrolled', 'completed', 'dropped', 'pending') DEFAULT 'enrolled',
    grade VARCHAR(5),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_deleted BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
    UNIQUE KEY unique_enrollment (student_id, course_id),
    INDEX idx_student (student_id),
    INDEX idx_course (course_id)
);

-- Audit Log Table
CREATE TABLE audit_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    action VARCHAR(50) NOT NULL,
    table_name VARCHAR(50) NOT NULL,
    record_id INT,
    old_value TEXT,
    new_value TEXT,
    ip_address VARCHAR(45),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_user (user_id),
    INDEX idx_action (action),
    INDEX idx_created (created_at)
);

-- Insert Default Admin User (password: admin123)
INSERT INTO users (username, email, password_hash, role, security_question, security_answer_hash) 
VALUES (
    'admin',
    'admin@campushub.com',
    'scrypt:32768:8:1$y8Hx2KqP4nGvWjRm$6f3e5d8a9b2c7e1f4a3d6b9c8e5f2a7d1b4c9e6f3a8d5b2e7c4f9a1d6b3e8c5f2a9d7b4e1c6f3a8d5b2e9c7f4a1d3b6e8c',
    'admin',
    'What is your favorite color?',
    'scrypt:32768:8:1$a1b2c3d4e5f6g7h8$1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p7q8r9s0t1u2v3w4x5y6z7a8b9c0d1e2f3g4h5i6j7k8l9m0n1o2p3q4r5s6t7u8v9w0'
);

-- Insert Sample Teachers
INSERT INTO users (username, email, password_hash, role) VALUES
('ms_tabeer', 'tabeer@campushub.com', 'scrypt:32768:8:1$y8Hx2KqP4nGvWjRm$6f3e5d8a9b2c7e1f4a3d6b9c8e5f2a7d1b4c9e6f3a8d5b2e7c4f9a1d6b3e8c5f2a9d7b4e1c6f3a8d5b2e9c7f4a1d3b6e8c', 'teacher'),
('ms_ammara', 'ammara@campushub.com', 'scrypt:32768:8:1$y8Hx2KqP4nGvWjRm$6f3e5d8a9b2c7e1f4a3d6b9c8e5f2a7d1b4c9e6f3a8d5b2e7c4f9a1d6b3e8c5f2a9d7b4e1c6f3a8d5b2e9c7f4a1d3b6e8c', 'teacher');

-- Insert Sample Courses
INSERT INTO courses (course_code, course_name, description, credits, teacher_id, semester, max_students) VALUES
('CS101', 'Introduction to Computer Science', 'Fundamentals of programming and problem solving', 3, 2, 'Fall 2024', 40),
('CS201', 'Data Structures and Algorithms', 'Advanced programming concepts and algorithms', 4, 2, 'Fall 2024', 35),
('MATH101', 'Calculus I', 'Differential and integral calculus', 4, 3, 'Fall 2024', 50),
('ENG101', 'English Composition', 'Academic writing and communication', 3, 3, 'Fall 2024', 30),
('PHY101', 'Physics I', 'Classical mechanics and thermodynamics', 4, 2, 'Fall 2024', 40);