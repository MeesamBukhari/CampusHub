from flask import Flask, request, session, jsonify
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
from mysql.connector import Error
from datetime import datetime, timedelta
import logging
from functools import wraps
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
CORS(app, supports_credentials=True, origins=["http://localhost:5173"])

# Configure Logging
logging.basicConfig(
    filename='campushub.log',    # Hardcoded filename
    level=logging.INFO,          # Hardcoded level
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Database Connection
def get_db_connection():
    try:
        conn = mysql.connector.connect(**Config.DB_CONFIG)
        return conn
    except Error as e:
        logger.error(f"Database connection error: {e}")
        return None

# Audit Log Function
def log_audit(user_id, action, table_name, record_id, old_value=None, new_value=None):
    try:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            ip_address = request.remote_addr
            cursor.execute(
                "INSERT INTO audit_log (user_id, action, table_name, record_id, old_value, new_value, ip_address) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (user_id, action, table_name, record_id, old_value, new_value, ip_address)
            )
            conn.commit()
            cursor.close()
            conn.close()
    except Error as e:
        logger.error(f"Audit log error: {e}")

# Authentication Decorators
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Unauthorized access', 'code': 401}), 401
        return f(*args, **kwargs)
    return decorated_function

def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                return jsonify({'error': 'Unauthorized access', 'code': 401}), 401
            if session.get('role') not in roles:
                return jsonify({'error': 'Access denied', 'code': 403}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# ============ AUTH ROUTES ============

@app.route('/api/auth/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        role = data.get('role', 'student')
        security_question = data.get('securityQuestion')
        security_answer = data.get('securityAnswer')
        
        if not all([username, email, password]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        if role not in ['student', 'teacher', 'admin']:
            return jsonify({'error': 'Invalid role'}), 400
        
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = conn.cursor()
        
        # Check if user exists
        cursor.execute("SELECT id FROM users WHERE username = %s OR email = %s", (username, email))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({'error': 'Username or email already exists'}), 409
        
        password_hash = generate_password_hash(password)
        security_answer_hash = generate_password_hash(security_answer) if security_answer else None
        
        cursor.execute(
            "INSERT INTO users (username, email, password_hash, role, security_question, security_answer_hash) VALUES (%s, %s, %s, %s, %s, %s)",
            (username, email, password_hash, role, security_question, security_answer_hash)
        )
        conn.commit()
        user_id = cursor.lastrowid
        
        log_audit(user_id, 'CREATE', 'users', user_id, None, f"User {username} registered")
        logger.info(f"New user registered: {username} ({role})")
        
        cursor.close()
        conn.close()
        
        return jsonify({'message': 'Registration successful', 'userId': user_id}), 201
    
    except Exception as e:
        logger.error(f"Registration error: {e}")
        return jsonify({'error': 'Registration failed'}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not all([username, password]):
            return jsonify({'error': 'Missing credentials'}), 400
        
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT id, username, email, password_hash, role, is_active FROM users WHERE username = %s",
            (username,)
        )
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not user or not check_password_hash(user['password_hash'], password):
            logger.warning(f"Failed login attempt for username: {username}")
            return jsonify({'error': 'Invalid credentials'}), 401
        
        if not user['is_active']:
            return jsonify({'error': 'Account is inactive'}), 403
        
        # Create session
        session.permanent = True
        session['user_id'] = user['id']
        session['username'] = user['username']
        session['email'] = user['email']
        session['role'] = user['role']
        session['login_time'] = datetime.now().isoformat()
        
        log_audit(user['id'], 'LOGIN', 'users', user['id'], None, f"User {username} logged in")
        logger.info(f"User logged in: {username} ({user['role']})")
        
        return jsonify({
            'message': 'Login successful',
            'user': {
                'id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'role': user['role']
            }
        }), 200
    
    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({'error': 'Login failed'}), 500

@app.route('/api/auth/logout', methods=['POST'])
@login_required
def logout():
    try:
        user_id = session.get('user_id')
        username = session.get('username')
        
        log_audit(user_id, 'LOGOUT', 'users', user_id, None, f"User {username} logged out")
        logger.info(f"User logged out: {username}")
        
        session.clear()
        return jsonify({'message': 'Logout successful'}), 200
    
    except Exception as e:
        logger.error(f"Logout error: {e}")
        return jsonify({'error': 'Logout failed'}), 500

@app.route('/api/auth/session', methods=['GET'])
def check_session():
    if 'user_id' in session:
        return jsonify({
            'authenticated': True,
            'user': {
                'id': session['user_id'],
                'username': session['username'],
                'email': session['email'],
                'role': session['role']
            }
        }), 200
    return jsonify({'authenticated': False}), 200

@app.route('/api/auth/recover', methods=['POST'])
def recover_password():
    try:
        data = request.get_json()
        email = data.get('email')
        security_answer = data.get('securityAnswer')
        new_password = data.get('newPassword')
        
        if not all([email, security_answer, new_password]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT id, username, security_answer_hash FROM users WHERE email = %s",
            (email,)
        )
        user = cursor.fetchone()
        
        if not user or not user['security_answer_hash']:
            cursor.close()
            conn.close()
            return jsonify({'error': 'Invalid email or security question not set'}), 404
        
        if not check_password_hash(user['security_answer_hash'], security_answer):
            cursor.close()
            conn.close()
            return jsonify({'error': 'Incorrect security answer'}), 401
        
        new_password_hash = generate_password_hash(new_password)
        cursor.execute(
            "UPDATE users SET password_hash = %s WHERE id = %s",
            (new_password_hash, user['id'])
        )
        conn.commit()
        
        log_audit(user['id'], 'UPDATE', 'users', user['id'], None, 'Password recovered')
        logger.info(f"Password recovered for user: {user['username']}")
        
        cursor.close()
        conn.close()
        
        return jsonify({'message': 'Password reset successful'}), 200
    
    except Exception as e:
        logger.error(f"Password recovery error: {e}")
        return jsonify({'error': 'Password recovery failed'}), 500

# ============ COURSE ROUTES ============

@app.route('/api/courses', methods=['GET'])
@login_required
def get_courses():
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = conn.cursor(dictionary=True)
        
        search = request.args.get('search', '')
        semester = request.args.get('semester', '')
        
        query = """
            SELECT c.*, u.username as teacher_name,
            (SELECT COUNT(*) FROM enrollments WHERE course_id = c.id AND is_deleted = FALSE) as enrolled_count
            FROM courses c
            LEFT JOIN users u ON c.teacher_id = u.id
            WHERE c.is_active = TRUE
        """
        params = []
        
        if search:
            query += " AND (c.course_code LIKE %s OR c.course_name LIKE %s)"
            params.extend([f"%{search}%", f"%{search}%"])
        
        if semester:
            query += " AND c.semester = %s"
            params.append(semester)
        
        query += " ORDER BY c.course_code"
        
        cursor.execute(query, params)
        courses = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify({'courses': courses}), 200
    
    except Exception as e:
        logger.error(f"Get courses error: {e}")
        return jsonify({'error': 'Failed to fetch courses'}), 500

@app.route('/api/courses/<int:course_id>', methods=['GET'])
@login_required
def get_course(course_id):
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT c.*, u.username as teacher_name,
            (SELECT COUNT(*) FROM enrollments WHERE course_id = c.id AND is_deleted = FALSE) as enrolled_count
            FROM courses c
            LEFT JOIN users u ON c.teacher_id = u.id
            WHERE c.id = %s
        """, (course_id,))
        
        course = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not course:
            return jsonify({'error': 'Course not found'}), 404
        
        return jsonify({'course': course}), 200
    
    except Exception as e:
        logger.error(f"Get course error: {e}")
        return jsonify({'error': 'Failed to fetch course'}), 500

@app.route('/api/courses', methods=['POST'])
@role_required('admin', 'teacher')
def create_course():
    try:
        data = request.get_json()
        
        required_fields = ['courseCode', 'courseName', 'credits', 'semester', 'maxStudents']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
        
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = conn.cursor()
        
        # Check if course code exists
        cursor.execute("SELECT id FROM courses WHERE course_code = %s", (data['courseCode'],))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({'error': 'Course code already exists'}), 409
        
        teacher_id = data.get('teacherId') if session['role'] == 'admin' else session['user_id']
        
        cursor.execute("""
            INSERT INTO courses (course_code, course_name, description, credits, teacher_id, semester, max_students)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            data['courseCode'],
            data['courseName'],
            data.get('description', ''),
            data['credits'],
            teacher_id,
            data['semester'],
            data['maxStudents']
        ))
        
        conn.commit()
        course_id = cursor.lastrowid
        
        log_audit(session['user_id'], 'CREATE', 'courses', course_id, None, f"Course {data['courseCode']} created")
        logger.info(f"Course created: {data['courseCode']} by user {session['username']}")
        
        cursor.close()
        conn.close()
        
        return jsonify({'message': 'Course created successfully', 'courseId': course_id}), 201
    
    except Exception as e:
        logger.error(f"Create course error: {e}")
        return jsonify({'error': 'Failed to create course'}), 500

@app.route('/api/courses/<int:course_id>', methods=['PUT'])
@role_required('admin', 'teacher')
def update_course(course_id):
    try:
        data = request.get_json()
        
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = conn.cursor(dictionary=True)
        
        # Check if course exists and user has permission
        cursor.execute("SELECT * FROM courses WHERE id = %s", (course_id,))
        course = cursor.fetchone()
        
        if not course:
            cursor.close()
            conn.close()
            return jsonify({'error': 'Course not found'}), 404
        
        if session['role'] == 'teacher' and course['teacher_id'] != session['user_id']:
            cursor.close()
            conn.close()
            return jsonify({'error': 'Access denied'}), 403
        
        # Update course
        update_fields = []
        params = []
        
        if 'courseName' in data:
            update_fields.append("course_name = %s")
            params.append(data['courseName'])
        if 'description' in data:
            update_fields.append("description = %s")
            params.append(data['description'])
        if 'credits' in data:
            update_fields.append("credits = %s")
            params.append(data['credits'])
        if 'semester' in data:
            update_fields.append("semester = %s")
            params.append(data['semester'])
        if 'maxStudents' in data:
            update_fields.append("max_students = %s")
            params.append(data['maxStudents'])
        
        if update_fields:
            params.append(course_id)
            query = f"UPDATE courses SET {', '.join(update_fields)} WHERE id = %s"
            cursor.execute(query, params)
            conn.commit()
            
            log_audit(session['user_id'], 'UPDATE', 'courses', course_id, str(course), str(data))
            logger.info(f"Course updated: {course['course_code']} by user {session['username']}")
        
        cursor.close()
        conn.close()
        
        return jsonify({'message': 'Course updated successfully'}), 200
    
    except Exception as e:
        logger.error(f"Update course error: {e}")
        return jsonify({'error': 'Failed to update course'}), 500

@app.route('/api/courses/<int:course_id>', methods=['DELETE'])
@role_required('admin')
def delete_course(course_id):
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM courses WHERE id = %s", (course_id,))
        course = cursor.fetchone()
        
        if not course:
            cursor.close()
            conn.close()
            return jsonify({'error': 'Course not found'}), 404
        
        # Soft delete
        cursor.execute("UPDATE courses SET is_active = FALSE WHERE id = %s", (course_id,))
        conn.commit()
        
        log_audit(session['user_id'], 'DELETE', 'courses', course_id, str(course), None)
        logger.info(f"Course deleted: {course['course_code']} by user {session['username']}")
        
        cursor.close()
        conn.close()
        
        return jsonify({'message': 'Course deleted successfully'}), 200
    
    except Exception as e:
        logger.error(f"Delete course error: {e}")
        return jsonify({'error': 'Failed to delete course'}), 500

# ============ ENROLLMENT ROUTES ============

@app.route('/api/enrollments', methods=['GET'])
@login_required
def get_enrollments():
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = conn.cursor(dictionary=True)
        
        role = session['role']
        user_id = session['user_id']
        
        if role == 'student':
            query = """
                SELECT e.*, c.course_code, c.course_name, c.credits, c.semester, u.username as teacher_name
                FROM enrollments e
                JOIN courses c ON e.course_id = c.id
                LEFT JOIN users u ON c.teacher_id = u.id
                WHERE e.student_id = %s AND e.is_deleted = FALSE
                ORDER BY e.enrollment_date DESC
            """
            cursor.execute(query, (user_id,))
        
        elif role == 'teacher':
            query = """
                SELECT e.*, c.course_code, c.course_name, s.username as student_name, s.email as student_email
                FROM enrollments e
                JOIN courses c ON e.course_id = c.id
                JOIN users s ON e.student_id = s.id
                WHERE c.teacher_id = %s AND e.is_deleted = FALSE
                ORDER BY e.enrollment_date DESC
            """
            cursor.execute(query, (user_id,))
        
        else:  # admin
            query = """
                SELECT e.*, c.course_code, c.course_name, s.username as student_name, 
                       s.email as student_email, t.username as teacher_name
                FROM enrollments e
                JOIN courses c ON e.course_id = c.id
                JOIN users s ON e.student_id = s.id
                LEFT JOIN users t ON c.teacher_id = t.id
                WHERE e.is_deleted = FALSE
                ORDER BY e.enrollment_date DESC
            """
            cursor.execute(query)
        
        enrollments = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify({'enrollments': enrollments}), 200
    
    except Exception as e:
        logger.error(f"Get enrollments error: {e}")
        return jsonify({'error': 'Failed to fetch enrollments'}), 500

@app.route('/api/enrollments', methods=['POST'])
@login_required
def create_enrollment():
    try:
        data = request.get_json()
        course_id = data.get('courseId')
        
        if not course_id:
            return jsonify({'error': 'Missing course ID'}), 400
        
        student_id = data.get('studentId') if session['role'] == 'admin' else session['user_id']
        
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = conn.cursor(dictionary=True)
        
        # Check if course exists and is active
        cursor.execute("SELECT * FROM courses WHERE id = %s AND is_active = TRUE", (course_id,))
        course = cursor.fetchone()
        
        if not course:
            cursor.close()
            conn.close()
            return jsonify({'error': 'Course not found or inactive'}), 404
        
        # Check if already enrolled
        cursor.execute(
            "SELECT id FROM enrollments WHERE student_id = %s AND course_id = %s AND is_deleted = FALSE",
            (student_id, course_id)
        )
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({'error': 'Already enrolled in this course'}), 409
        
        # Check course capacity
        cursor.execute(
            "SELECT COUNT(*) as count FROM enrollments WHERE course_id = %s AND is_deleted = FALSE",
            (course_id,)
        )
        result = cursor.fetchone()
        if result['count'] >= course['max_students']:
            cursor.close()
            conn.close()
            return jsonify({'error': 'Course is full'}), 400
        
        # Create enrollment
        cursor.execute(
            "INSERT INTO enrollments (student_id, course_id, status) VALUES (%s, %s, 'enrolled')",
            (student_id, course_id)
        )
        conn.commit()
        enrollment_id = cursor.lastrowid
        
        log_audit(session['user_id'], 'CREATE', 'enrollments', enrollment_id, None, 
                 f"Student {student_id} enrolled in course {course_id}")
        logger.info(f"Enrollment created: Student {student_id} in course {course['course_code']}")
        
        cursor.close()
        conn.close()
        
        return jsonify({'message': 'Enrollment successful', 'enrollmentId': enrollment_id}), 201
    
    except Exception as e:
        logger.error(f"Create enrollment error: {e}")
        return jsonify({'error': 'Failed to create enrollment'}), 500

@app.route('/api/enrollments/<int:enrollment_id>', methods=['PUT'])
@role_required('admin', 'teacher')
def update_enrollment(enrollment_id):
    try:
        data = request.get_json()
        
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT e.*, c.teacher_id 
            FROM enrollments e 
            JOIN courses c ON e.course_id = c.id 
            WHERE e.id = %s
        """, (enrollment_id,))
        
        enrollment = cursor.fetchone()
        
        if not enrollment:
            cursor.close()
            conn.close()
            return jsonify({'error': 'Enrollment not found'}), 404
        
        if session['role'] == 'teacher' and enrollment['teacher_id'] != session['user_id']:
            cursor.close()
            conn.close()
            return jsonify({'error': 'Access denied'}), 403
        
        # Update enrollment
        update_fields = []
        params = []
        
        if 'status' in data:
            update_fields.append("status = %s")
            params.append(data['status'])
        if 'grade' in data:
            update_fields.append("grade = %s")
            params.append(data['grade'])
        
        if update_fields:
            params.append(enrollment_id)
            query = f"UPDATE enrollments SET {', '.join(update_fields)} WHERE id = %s"
            cursor.execute(query, params)
            conn.commit()
            
            log_audit(session['user_id'], 'UPDATE', 'enrollments', enrollment_id, str(enrollment), str(data))
            logger.info(f"Enrollment updated: ID {enrollment_id} by user {session['username']}")
        
        cursor.close()
        conn.close()
        
        return jsonify({'message': 'Enrollment updated successfully'}), 200
    
    except Exception as e:
        logger.error(f"Update enrollment error: {e}")
        return jsonify({'error': 'Failed to update enrollment'}), 500

@app.route('/api/enrollments/<int:enrollment_id>', methods=['DELETE'])
@login_required
def delete_enrollment(enrollment_id):
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM enrollments WHERE id = %s", (enrollment_id,))
        enrollment = cursor.fetchone()
        
        if not enrollment:
            cursor.close()
            conn.close()
            return jsonify({'error': 'Enrollment not found'}), 404
        
        # Check permissions
        if session['role'] == 'student' and enrollment['student_id'] != session['user_id']:
            cursor.close()
            conn.close()
            return jsonify({'error': 'Access denied'}), 403
        
        # Soft delete
        cursor.execute("UPDATE enrollments SET is_deleted = TRUE WHERE id = %s", (enrollment_id,))
        conn.commit()
        
        log_audit(session['user_id'], 'DELETE', 'enrollments', enrollment_id, str(enrollment), None)
        logger.info(f"Enrollment deleted: ID {enrollment_id} by user {session['username']}")
        
        cursor.close()
        conn.close()
        
        return jsonify({'message': 'Enrollment deleted successfully'}), 200
    
    except Exception as e:
        logger.error(f"Delete enrollment error: {e}")
        return jsonify({'error': 'Failed to delete enrollment'}), 500

# ============ USER MANAGEMENT ROUTES (Admin Only) ============

@app.route('/api/users', methods=['GET'])
@role_required('admin')
def get_users():
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = conn.cursor(dictionary=True)
        
        role_filter = request.args.get('role', '')
        search = request.args.get('search', '')
        
        query = "SELECT id, username, email, role, created_at, is_active FROM users WHERE 1=1"
        params = []
        
        if role_filter:
            query += " AND role = %s"
            params.append(role_filter)
        
        if search:
            query += " AND (username LIKE %s OR email LIKE %s)"
            params.extend([f"%{search}%", f"%{search}%"])
        
        query += " ORDER BY created_at DESC"
        
        cursor.execute(query, params)
        users = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify({'users': users}), 200
    
    except Exception as e:
        logger.error(f"Get users error: {e}")
        return jsonify({'error': 'Failed to fetch users'}), 500

@app.route('/api/users/<int:user_id>', methods=['PUT'])
@role_required('admin')
def update_user(user_id):
    try:
        data = request.get_json()
        
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        
        if not user:
            cursor.close()
            conn.close()
            return jsonify({'error': 'User not found'}), 404
        
        update_fields = []
        params = []
        
        if 'role' in data:
            update_fields.append("role = %s")
            params.append(data['role'])
        if 'isActive' in data:
            update_fields.append("is_active = %s")
            params.append(data['isActive'])
        
        if update_fields:
            params.append(user_id)
            query = f"UPDATE users SET {', '.join(update_fields)} WHERE id = %s"
            cursor.execute(query, params)
            conn.commit()
            
            log_audit(session['user_id'], 'UPDATE', 'users', user_id, str(user), str(data))
            logger.info(f"User updated: {user['username']} by admin {session['username']}")
        
        cursor.close()
        conn.close()
        
        return jsonify({'message': 'User updated successfully'}), 200
    
    except Exception as e:
        logger.error(f"Update user error: {e}")
        return jsonify({'error': 'Failed to update user'}), 500

# ============ DASHBOARD/STATS ROUTES ============

@app.route('/api/dashboard/stats', methods=['GET'])
@login_required
def get_dashboard_stats():
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = conn.cursor(dictionary=True)
        
        role = session['role']
        user_id = session['user_id']
        
        stats = {}
        
        if role == 'student':
            cursor.execute(
                "SELECT COUNT(*) as count FROM enrollments WHERE student_id = %s AND is_deleted = FALSE",
                (user_id,)
            )
            stats['enrolledCourses'] = cursor.fetchone()['count']
            
            cursor.execute(
                "SELECT COUNT(*) as count FROM courses WHERE is_active = TRUE"
            )
            stats['availableCourses'] = cursor.fetchone()['count']
        
        elif role == 'teacher':
            cursor.execute(
                "SELECT COUNT(*) as count FROM courses WHERE teacher_id = %s AND is_active = TRUE",
                (user_id,)
            )
            stats['myCourses'] = cursor.fetchone()['count']
            
            cursor.execute("""
                SELECT COUNT(*) as count FROM enrollments e
                JOIN courses c ON e.course_id = c.id
                WHERE c.teacher_id = %s AND e.is_deleted = FALSE
            """, (user_id,))
            stats['totalStudents'] = cursor.fetchone()['count']
        
        else:  # admin
            cursor.execute("SELECT COUNT(*) as count FROM users WHERE is_active = TRUE")
            stats['totalUsers'] = cursor.fetchone()['count']
            
            cursor.execute("SELECT COUNT(*) as count FROM courses WHERE is_active = TRUE")
            stats['totalCourses'] = cursor.fetchone()['count']
            
            cursor.execute("SELECT COUNT(*) as count FROM enrollments WHERE is_deleted = FALSE")
            stats['totalEnrollments'] = cursor.fetchone()['count']
        
        cursor.close()
        conn.close()
        
        return jsonify({'stats': stats}), 200
    
    except Exception as e:
        logger.error(f"Get dashboard stats error: {e}")
        return jsonify({'error': 'Failed to fetch stats'}), 500

# ============ ERROR HANDLERS ============

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Resource not found', 'code': 404}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return jsonify({'error': 'Internal server error', 'code': 500}), 500

@app.errorhandler(401)
def unauthorized(error):
    return jsonify({'error': 'Unauthorized access', 'code': 401}), 401

@app.errorhandler(403)
def forbidden(error):
    return jsonify({'error': 'Access denied', 'code': 403}), 403

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)