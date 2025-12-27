USE campushub;

-- --------------------------------------------------------
-- 1. CLEANUP (Reset Database State)
-- --------------------------------------------------------
SET FOREIGN_KEY_CHECKS = 0;
TRUNCATE TABLE audit_log;
TRUNCATE TABLE enrollments;
TRUNCATE TABLE courses;
TRUNCATE TABLE users;
SET FOREIGN_KEY_CHECKS = 1;

-- --------------------------------------------------------
-- 2. SEED USERS
-- Password for all users is the scrypt hash from the schema (likely 'admin123')
-- --------------------------------------------------------
INSERT INTO users (id, username, email, password_hash, role, security_question, security_answer_hash) VALUES 
-- Admin (ID: 1)
(1, 'admin', 'admin@campushub.com', 'scrypt:32768:8:1$y8Hx2KqP4nGvWjRm$6f3e5d8a9b2c7e1f4a3d6b9c8e5f2a7d1b4c9e6f3a8d5b2e7c4f9a1d6b3e8c5f2a9d7b4e1c6f3a8d5b2e9c7f4a1d3b6e8c', 'admin', 'What is your favorite color?', 'scrypt:32768:8:1$a1b2c3d4e5f6g7h8$1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p7q8r9s0t1u2v3w4x5y6z7a8b9c0d1e2f3g4h5i6j7k8l9m0n1o2p3q4r5s6t7u8v9w0');

-- Teachers (IDs: 2, 3)
(2, 'ms_tabeer', 'tabeer@campushub.com', 'scrypt:32768:8:1$y8Hx2KqP4nGvWjRm$6f3e5d8a9b2c7e1f4a3d6b9c8e5f2a7d1b4c9e6f3a8d5b2e7c4f9a1d6b3e8c5f2a9d7b4e1c6f3a8d5b2e9c7f4a1d3b6e8c', 'teacher', NULL, NULL),
(3, 'ms_ammara', 'ammara@campushub.com', 'scrypt:32768:8:1$y8Hx2KqP4nGvWjRm$6f3e5d8a9b2c7e1f4a3d6b9c8e5f2a7d1b4c9e6f3a8d5b2e7c4f9a1d6b3e8c5f2a9d7b4e1c6f3a8d5b2e9c7f4a1d3b6e8c', 'teacher', NULL, NULL),

-- Students (IDs: 4 - 8)
(4, 'meesam_bukhari', 'meesam@student.campushub.com', 'scrypt:32768:8:1$y8Hx2KqP4nGvWjRm$6f3e5d8a9b2c7e1f4a3d6b9c8e5f2a7d1b4c9e6f3a8d5b2e7c4f9a1d6b3e8c5f2a9d7b4e1c6f3a8d5b2e9c7f4a1d3b6e8c', 'student', NULL, NULL),
(5, 'rija_bukhari', 'rija@student.campushub.com', 'scrypt:32768:8:1$y8Hx2KqP4nGvWjRm$6f3e5d8a9b2c7e1f4a3d6b9c8e5f2a7d1b4c9e6f3a8d5b2e7c4f9a1d6b3e8c5f2a9d7b4e1c6f3a8d5b2e9c7f4a1d3b6e8c', 'student', NULL, NULL),
(6, 'qazi_shadab', 'shadab@student.campushub.com', 'scrypt:32768:8:1$y8Hx2KqP4nGvWjRm$6f3e5d8a9b2c7e1f4a3d6b9c8e5f2a7d1b4c9e6f3a8d5b2e7c4f9a1d6b3e8c5f2a9d7b4e1c6f3a8d5b2e9c7f4a1d3b6e8c', 'student', NULL, NULL),
(7, 'haris_lodhi', 'haris@student.campushub.com', 'scrypt:32768:8:1$y8Hx2KqP4nGvWjRm$6f3e5d8a9b2c7e1f4a3d6b9c8e5f2a7d1b4c9e6f3a8d5b2e7c4f9a1d6b3e8c5f2a9d7b4e1c6f3a8d5b2e9c7f4a1d3b6e8c', 'student', NULL, NULL),
(8, 'najam_iqbal', 'najam@student.campushub.com', 'scrypt:32768:8:1$y8Hx2KqP4nGvWjRm$6f3e5d8a9b2c7e1f4a3d6b9c8e5f2a7d1b4c9e6f3a8d5b2e7c4f9a1d6b3e8c5f2a9d7b4e1c6f3a8d5b2e9c7f4a1d3b6e8c', 'student', NULL, NULL);

-- --------------------------------------------------------
-- 3. SEED COURSES
-- --------------------------------------------------------
INSERT INTO courses (id, course_code, course_name, description, credits, teacher_id, semester, max_students) VALUES
(1, 'CS101', 'Intro to Computer Science', 'Fundamentals of programming and problem solving', 3, 2, 'Fall 2024', 40),
(2, 'CS201', 'Data Structures & Algorithms', 'Advanced programming concepts and algorithms', 4, 2, 'Fall 2024', 35),
(3, 'MATH101', 'Calculus I', 'Differential and integral calculus', 4, 3, 'Fall 2024', 50),
(4, 'ENG101', 'English Composition', 'Academic writing and communication', 3, 3, 'Fall 2024', 30),
(5, 'PHY101', 'Physics I', 'Classical mechanics and thermodynamics', 4, 2, 'Fall 2024', 40),
(6, 'HIS105', 'World History', 'A survey of world history since 1900', 3, 3, 'Spring 2025', 60);

-- --------------------------------------------------------
-- 4. SEED ENROLLMENTS
-- Statuses: enrolled, completed, dropped, pending
-- --------------------------------------------------------
INSERT INTO enrollments (student_id, course_id, status, grade, enrollment_date) VALUES
-- Alice (ID 4) - Good student
(4, 1, 'completed', 'A', '2024-01-15 10:00:00'),
(4, 3, 'enrolled', NULL, '2024-08-20 09:00:00'),
(4, 4, 'enrolled', NULL, '2024-08-21 11:30:00'),

-- Bob (ID 5) - Average student
(5, 1, 'completed', 'B+', '2024-01-15 10:05:00'),
(5, 2, 'enrolled', NULL, '2024-08-22 14:00:00'),

-- Charlie (ID 6) - Struggling student
(6, 1, 'dropped', 'W', '2024-01-20 16:00:00'),
(6, 4, 'enrolled', NULL, '2024-08-23 09:15:00'),

-- Diana (ID 7) - High achiever
(7, 2, 'enrolled', NULL, '2024-08-20 08:30:00'),
(7, 3, 'enrolled', NULL, '2024-08-20 08:35:00'),
(7, 5, 'enrolled', NULL, '2024-08-20 08:40:00'),

-- Evan (ID 8) - New enrollment
(8, 1, 'pending', NULL, '2024-09-01 12:00:00');

-- --------------------------------------------------------
-- 5. SEED AUDIT LOG
-- Simulate some system activity
-- --------------------------------------------------------
INSERT INTO audit_log (user_id, action, table_name, record_id, old_value, new_value, ip_address) VALUES
(1, 'CREATE', 'users', 2, NULL, '{"username": "prof_smith"}', '192.168.1.1'),
(1, 'CREATE', 'users', 3, NULL, '{"username": "prof_johnson"}', '192.168.1.1'),
(2, 'UPDATE', 'courses', 1, '{"max_students": 35}', '{"max_students": 40}', '192.168.1.50'),
(4, 'INSERT', 'enrollments', 1, NULL, '{"status": "enrolled"}', '10.0.0.5');